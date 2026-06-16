from typing import TypedDict
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from backend.config import config

# ── State ────────────────────────────────────────────────────────

class CodeAnalysisState(TypedDict):
    code: str
    language: str
    task: str        # "analyze" | "debug" | "review"
    analysis: str
    bugs: list
    suggestions: list

# ── LLM ─────────────────────────────────────────────────────────

def get_llm():
    return ChatGroq(
        api_key=config.GROQ_API_KEY,
        model=config.GROQ_MODEL,
        temperature=0.1
    )

# ── Prompts ──────────────────────────────────────────────────────

ANALYZE_PROMPT = """You are an expert code reviewer. Analyze the following {language} code and provide:

1. **Summary** — What the code does
2. **Issues Found** — List any bugs, errors, or bad practices (with line references if possible)
3. **Suggestions** — How to improve or fix it
4. **Corrected Code** — Provide the fixed version if there are issues

Code:
```{language}
{code}
```

Be concise and developer-focused."""

DEBUG_PROMPT = """You are an expert debugger. Debug the following {language} code:

1. **Root Cause** — What is causing the bug
2. **Affected Lines** — Which lines are problematic
3. **Fix** — Exact fix with corrected code
4. **Explanation** — Why this fix works

Code:
```{language}
{code}
```"""

REVIEW_PROMPT = """You are a senior engineer doing a code review. Review the following {language} code:

1. **Code Quality** — Readability, structure, naming conventions
2. **Performance** — Any performance concerns
3. **Security** — Any security issues
4. **Best Practices** — What follows or violates best practices
5. **Overall Rating** — Score out of 10 with justification

Code:
```{language}
{code}
```"""

# ── Core Analysis Function ───────────────────────────────────────

def run_code_analysis(code: str, language: str = "python", task: str = "analyze") -> dict:
    """
    Main entry point for code analysis.
    Called by tools/code_analyzer.py in Day 3.
    """
    llm = get_llm()

    prompt_map = {
        "analyze": ANALYZE_PROMPT,
        "debug": DEBUG_PROMPT,
        "review": REVIEW_PROMPT
    }

    prompt_template = prompt_map.get(task, ANALYZE_PROMPT)
    prompt = prompt_template.format(language=language, code=code)

    messages = [
        SystemMessage(content="You are an AI Developer Assistant specialized in code analysis."),
        HumanMessage(content=prompt)
    ]

    result = llm.invoke(messages)

    return {
        "task": task,
        "language": language,
        "analysis": result.content,
        "code_length": len(code.splitlines())
    }

# ── Language Detector ────────────────────────────────────────────

def detect_language(code: str) -> str:
    """
    Simple heuristic-based language detection.
    Will be enhanced with AST tools in Day 3.
    """
    code_lower = code.lower()

    if "def " in code and "import " in code:
        return "python"
    elif "function " in code or "const " in code or "let " in code:
        return "javascript"
    elif "public class" in code or "System.out" in code:
        return "java"
    elif "#include" in code or "std::" in code:
        return "cpp"
    elif "func " in code and "fmt." in code:
        return "go"
    else:
        return "python"  # default fallback