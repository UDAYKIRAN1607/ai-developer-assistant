from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os

router = APIRouter()

# ── Request Models ──────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class CodeAnalysisRequest(BaseModel):
    code: str
    language: str = "python"
    task: str = "analyze"   # "analyze" | "debug" | "review"

# ── Chat Route ──────────────────────────────────────────────────

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint — routes to the LangGraph developer agent.
    Will be wired to developer_agent in Day 2.
    """
    # Placeholder until agent is wired in Day 2
    return {
        "response": f"[Agent not wired yet] You said: {request.message}",
        "conversation_id": request.conversation_id or "new"
    }

# ── Code Analysis Route ─────────────────────────────────────────

@router.post("/analyze")
async def analyze_code(request: CodeAnalysisRequest):
    """
    Code analysis endpoint — routes to code_analyzer + bug_detector tools.
    Will be wired to tools in Day 3.
    """
    # Placeholder until tools are wired in Day 3
    return {
        "language": request.language,
        "task": request.task,
        "result": "[Tools not wired yet] Code received successfully",
        "code_length": len(request.code)
    }

# ── Docs Upload Route ───────────────────────────────────────────

@router.post("/docs/upload")
async def upload_doc(file: UploadFile = File(...)):
    """
    Upload a doc for RAG ingestion.
    Will be wired to RAG pipeline in Day 4.
    """
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

# ── Docs Q&A Route ──────────────────────────────────────────────

@router.post("/docs/query")
async def query_docs(request: ChatRequest):
    """
    Query against uploaded docs via RAG.
    Will be wired to retriever in Day 4.
    """
    return {
        "query": request.message,
        "result": "[RAG not wired yet] Query received successfully"
    }

# ── GitHub Route ────────────────────────────────────────────────

@router.get("/github/issues")
async def get_github_issues(repo: str):
    """
    Fetch GitHub issues for a given repo (owner/repo format).
    Will be wired to github_tool in Day 3.
    """
    return {
        "repo": repo,
        "issues": "[GitHub tool not wired yet]"
    }

# ── JIRA Route ──────────────────────────────────────────────────

@router.get("/jira/issues")
async def get_jira_issues(project_key: str):
    """
    Fetch JIRA issues for a given project key.
    Will be wired to jira_tool in Day 3.
    """
    return {
        "project_key": project_key,
        "issues": "[JIRA tool not wired yet]"
    }