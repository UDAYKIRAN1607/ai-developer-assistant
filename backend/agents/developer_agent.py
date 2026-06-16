from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from backend.config import config

# ── Agent State ─────────────────────────────────────────────────

class AgentState(TypedDict):
    messages: List[HumanMessage | AIMessage | SystemMessage]
    user_input: str
    intent: str          # "code_analysis" | "docs_qa" | "github" | "jira" | "general"
    response: str
    next_action: str     # which tool/node to route to

# ── LLM ─────────────────────────────────────────────────────────

def get_llm():
    return ChatGroq(
        api_key=config.GROQ_API_KEY,
        model=config.GROQ_MODEL,
        temperature=0.2,
        streaming=True
    )

# ── System Prompt ────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an AI Developer Assistant Agent. You help developers with:
1. Code Analysis & Bug Detection — analyze code, find bugs, suggest fixes
2. Documentation Q&A — answer questions from uploaded technical docs
3. GitHub Integration — fetch and summarize issues, PRs from GitHub repos
4. JIRA Integration — fetch and summarize JIRA tickets and defects
5. General developer questions — architecture, best practices, explanations

Always be concise, technical, and developer-focused in your responses.
When analyzing code, always mention: language detected, issues found, and suggested fixes.
"""

# ── Node: Detect Intent ──────────────────────────────────────────

def detect_intent(state: AgentState) -> AgentState:
    """Classify what the user wants to do."""
    llm = get_llm()

    intent_prompt = f"""Classify the following user message into exactly one of these intents:
- code_analysis: user wants code reviewed, debugged, or analyzed
- docs_qa: user is asking a question about documentation
- github: user wants GitHub issues, PRs, or repo info
- jira: user wants JIRA tickets or project info
- general: general developer question or conversation

User message: "{state['user_input']}"

Respond with only the intent label, nothing else."""

    result = llm.invoke([HumanMessage(content=intent_prompt)])
    intent = result.content.strip().lower()

    # Fallback if model returns unexpected value
    valid_intents = ["code_analysis", "docs_qa", "github", "jira", "general"]
    if intent not in valid_intents:
        intent = "general"

    return {**state, "intent": intent, "next_action": intent}

# ── Node: Route ──────────────────────────────────────────────────

def route_intent(state: AgentState) -> str:
    """Router — decides which node to go to next based on intent."""
    return state["intent"]

# ── Node: General Response ───────────────────────────────────────

def general_response(state: AgentState) -> AgentState:
    """Handle general developer questions."""
    llm = get_llm()

    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    result = llm.invoke(messages)

    return {
        **state,
        "response": result.content,
        "messages": state["messages"] + [AIMessage(content=result.content)]
    }

# ── Node: Code Analysis (stub — wired fully in Day 3) ───────────

def code_analysis_response(state: AgentState) -> AgentState:
    """Route to code analysis — tools will be wired in Day 3."""
    llm = get_llm()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"The user wants code analysis. Their message: {state['user_input']}\nProvide a helpful response and ask them to paste their code if they haven't already.")
    ]
    result = llm.invoke(messages)

    return {
        **state,
        "response": result.content,
        "messages": state["messages"] + [AIMessage(content=result.content)]
    }

# ── Node: Docs Q&A (stub — wired fully in Day 4) ────────────────

def docs_qa_response(state: AgentState) -> AgentState:
    """Route to RAG pipeline — will be wired in Day 4."""
    llm = get_llm()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"The user has a docs question: {state['user_input']}\nLet them know RAG pipeline is being set up and answer generally if you can.")
    ]
    result = llm.invoke(messages)

    return {
        **state,
        "response": result.content,
        "messages": state["messages"] + [AIMessage(content=result.content)]
    }

# ── Node: GitHub (stub — wired fully in Day 3) ──────────────────

def github_response(state: AgentState) -> AgentState:
    """Route to GitHub tool — will be wired in Day 3."""
    return {
        **state,
        "response": "GitHub integration is being wired up. Please provide your repo (owner/repo format) and I'll fetch the issues for you soon.",
        "messages": state["messages"] + [AIMessage(content="GitHub tool coming in Day 3.")]
    }

# ── Node: JIRA (stub — wired fully in Day 3) ────────────────────

def jira_response(state: AgentState) -> AgentState:
    """Route to JIRA tool — will be wired in Day 3."""
    return {
        **state,
        "response": "JIRA integration is being wired up. Please provide your project key and I'll fetch the tickets for you soon.",
        "messages": state["messages"] + [AIMessage(content="JIRA tool coming in Day 3.")]
    }

# ── Build the Graph ──────────────────────────────────────────────

def build_developer_agent():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("detect_intent", detect_intent)
    graph.add_node("general", general_response)
    graph.add_node("code_analysis", code_analysis_response)
    graph.add_node("docs_qa", docs_qa_response)
    graph.add_node("github", github_response)
    graph.add_node("jira", jira_response)

    # Entry point
    graph.set_entry_point("detect_intent")

    # Conditional routing after intent detection
    graph.add_conditional_edges(
        "detect_intent",
        route_intent,
        {
            "general": "general",
            "code_analysis": "code_analysis",
            "docs_qa": "docs_qa",
            "github": "github",
            "jira": "jira"
        }
    )

    # All nodes end after responding
    graph.add_edge("general", END)
    graph.add_edge("code_analysis", END)
    graph.add_edge("docs_qa", END)
    graph.add_edge("github", END)
    graph.add_edge("jira", END)

    return graph.compile()

# Compiled agent — imported by routes.py
developer_agent = build_developer_agent()