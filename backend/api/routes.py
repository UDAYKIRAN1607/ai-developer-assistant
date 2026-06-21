# from fastapi import APIRouter, UploadFile, File, HTTPException
# from fastapi.responses import StreamingResponse
# from pydantic import BaseModel
# from langchain_core.messages import HumanMessage
# from backend.agents.developer_agent import developer_agent
# from backend.agents.code_analysis_agent import run_code_analysis, detect_language
# from google import genai
# import os


# router = APIRouter()

# # ── Request Models ──────────────────────────────────────────────

# class ChatRequest(BaseModel):
#     message: str
#     conversation_id: str | None = None

# class CodeAnalysisRequest(BaseModel):
#     code: str
#     language: str | None = None
#     task: str = "analyze"   # "analyze" | "debug" | "review"

# # ── Chat Route ──────────────────────────────────────────────────

# @router.post("/chat")
# async def chat(request: ChatRequest):
#     """
#     Main chat endpoint — routes through LangGraph developer agent.
#     """
#     initial_state = {
#         "messages": [HumanMessage(content=request.message)],
#         "user_input": request.message,
#         "intent": "",
#         "response": "",
#         "next_action": ""
#     }

#     result = developer_agent.invoke(initial_state)

#     return {
#         "response": result["response"],
#         "intent": result["intent"],
#         "conversation_id": request.conversation_id or "new"
#     }

# # ── Code Analysis Route ─────────────────────────────────────────

# @router.post("/analyze")
# async def analyze_code(request: CodeAnalysisRequest):
#     """
#     Code analysis endpoint — runs through code_analysis_agent.
#     """
#     language = request.language or detect_language(request.code)
#     result = run_code_analysis(
#         code=request.code,
#         language=language,
#         task=request.task
#     )
#     return result

# # ── Docs Upload Route ───────────────────────────────────────────

# @router.post("/docs/upload")
# async def upload_doc(file: UploadFile = File(...)):
#     """
#     Upload a doc for RAG ingestion.
#     Will be wired to RAG pipeline in Day 4.
#     """
#     allowed_types = ["application/pdf", "text/plain", "text/markdown"]
#     if file.content_type not in allowed_types:
#         raise HTTPException(status_code=400, detail="Only PDF, TXT, and MD files are supported")

#     save_path = f"./data/uploads/{file.filename}"
#     os.makedirs("./data/uploads", exist_ok=True)

#     with open(save_path, "wb") as f:
#         content = await file.read()
#         f.write(content)

#     return {
#         "filename": file.filename,
#         "status": "uploaded",
#         "message": "File saved. RAG ingestion will be wired in Day 4."
#     }

# # ── Docs Q&A Route ──────────────────────────────────────────────

# @router.post("/docs/query")
# async def query_docs(request: ChatRequest):
#     """
#     Query against uploaded docs via RAG.
#     Will be wired to retriever in Day 4.
#     """
#     return {
#         "query": request.message,
#         "result": "[RAG not wired yet] Query received successfully"
#     }

# # ── GitHub Route ────────────────────────────────────────────────

# @router.get("/github/issues")
# async def get_github_issues(repo: str):
#     """
#     Fetch GitHub issues for a given repo (owner/repo format).
#     Will be wired to github_tool in Day 3.
#     """
#     return {
#         "repo": repo,
#         "issues": "[GitHub tool not wired yet]"
#     }

# # ── JIRA Route ──────────────────────────────────────────────────

# @router.get("/jira/issues")
# async def get_jira_issues(project_key: str):
#     """
#     Fetch JIRA issues for a given project key.
#     Will be wired to jira_tool in Day 3.
#     """
#     return {
#         "project_key": project_key,
#         "issues": "[JIRA tool not wired yet]"
#     }

# # ── Test Gemini Route ───────────────────────────────────────────
# @router.get("/test-gemini")
# def test_gemini():
#     client = genai.Client(
#         api_key=os.getenv("GEMINI_API_KEY")
#     )

#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents="Explain FastAPI in 3 lines or less."
#     )

#     return {"response": response.text}
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from backend.agents.developer_agent import developer_agent
from backend.tools.code_analyzer import run_full_code_analysis
from backend.tools.bug_detector import run_bug_detection
from backend.tools.github_tool import get_repo_issues, get_repo_pull_requests, get_repo_summary
from backend.tools.jira_tool import get_project_issues, get_issue_detail, get_project_summary
from backend.agents.code_analysis_agent import detect_language
from google import genai
import os

router = APIRouter()

# ── Request Models ───────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class CodeAnalysisRequest(BaseModel):
    code: str
    language: str | None = None
    task: str = "analyze"   # "analyze" | "debug" | "review"

class BugDetectionRequest(BaseModel):
    code: str
    language: str | None = None

# ── Chat Route ───────────────────────────────────────────────────

@router.post("/chat")
async def chat(request: ChatRequest):
    """Main chat endpoint — routes through LangGraph developer agent."""
    initial_state = {
        "messages": [HumanMessage(content=request.message)],
        "user_input": request.message,
        "intent": "",
        "response": "",
        "next_action": ""
    }
    result = developer_agent.invoke(initial_state)
    return {
        "response": result["response"],
        "intent": result["intent"],
        "conversation_id": request.conversation_id or "new"
    }

# ── Code Analysis Route ──────────────────────────────────────────

@router.post("/analyze")
async def analyze_code(request: CodeAnalysisRequest):
    """Full code analysis — AST + complexity + Gemini AI review."""
    result = run_full_code_analysis(
        code=request.code,
        language=request.language,
        task=request.task
    )
    return result

# ── Bug Detection Route ──────────────────────────────────────────

@router.post("/bugs")
async def detect_bugs(request: BugDetectionRequest):
    """Pattern-based + AI-powered bug detection."""
    language = request.language or detect_language(request.code)
    result = run_bug_detection(code=request.code, language=language)
    return result

# ── Docs Upload Route ────────────────────────────────────────────

@router.post("/docs/upload")
async def upload_doc(file: UploadFile = File(...)):
    """Upload a doc for RAG ingestion — wired in Day 4."""
    allowed_types = ["application/pdf", "text/plain", "text/markdown"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF, TXT, and MD files are supported")

    save_path = f"./data/uploads/{file.filename}"
    os.makedirs("./data/uploads", exist_ok=True)

    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {
        "filename": file.filename,
        "status": "uploaded",
        "message": "File saved. RAG ingestion will be wired in Day 4."
    }

# ── Docs Q&A Route ───────────────────────────────────────────────

@router.post("/docs/query")
async def query_docs(request: ChatRequest):
    """Query uploaded docs via RAG — wired in Day 4."""
    return {
        "query": request.message,
        "result": "[RAG not wired yet] Query received successfully"
    }

# ── GitHub Routes ────────────────────────────────────────────────

@router.get("/github/repo")
async def github_repo_summary(repo: str):
    """Fetch GitHub repo metadata. repo format: owner/repo"""
    return get_repo_summary(repo)

@router.get("/github/issues")
async def get_github_issues(repo: str, state: str = "open", limit: int = 10):
    """Fetch GitHub issues for a repo."""
    return get_repo_issues(repo, state=state, limit=limit)

@router.get("/github/pulls")
async def get_github_pulls(repo: str, state: str = "open", limit: int = 10):
    """Fetch GitHub pull requests for a repo."""
    return get_repo_pull_requests(repo, state=state, limit=limit)

# ── JIRA Routes ──────────────────────────────────────────────────

@router.get("/jira/project")
async def jira_project_summary(project_key: str):
    """Fetch JIRA project issue counts by status."""
    return get_project_summary(project_key)

@router.get("/jira/issues")
async def get_jira_issues(project_key: str, status: str = None, limit: int = 10):
    """Fetch JIRA issues for a project key."""
    return get_project_issues(project_key, status=status, limit=limit)

@router.get("/jira/issue/{issue_key}")
async def get_jira_issue(issue_key: str):
    """Fetch full detail of a single JIRA issue."""
    return get_issue_detail(issue_key)

# ── Test Gemini Route (your existing route — kept) ───────────────

@router.get("/test-gemini")
def test_gemini():
    """Quick Gemini connectivity test."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Explain FastAPI in 3 lines or less."
    )
    return {"response": response.text}