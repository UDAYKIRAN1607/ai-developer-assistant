from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
from backend.config import config

app = FastAPI(
    title="AI Developer Assistant",
    description="An AI-powered assistant for code analysis, docs Q&A, and JIRA/GitHub integration",
    version="1.0.0"
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"status": "AI Developer Assistant is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=config.APP_HOST, port=config.APP_PORT, reload=config.DEBUG)
   