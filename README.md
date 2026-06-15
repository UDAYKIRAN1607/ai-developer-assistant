# AI Developer Assistant Agent

An AI-powered developer assistant built with LangGraph + Groq that helps with:
- **Code Analysis & Bug Detection** — Paste code, get instant analysis and fix suggestions
- **RAG-based Docs Q&A** — Ask questions against your uploaded documentation
- **JIRA / GitHub Integration** — Fetch issues, PRs, and defects directly from your tools

## Stack
- **Backend:** Python, FastAPI, LangChain, LangGraph, Groq (LLaMA)
- **Frontend:** React, TypeScript, Vite, Tailwind CSS
- **RAG:** ChromaDB
- **Integrations:** GitHub API, JIRA API

## Project Structure
```
ai-developer-assistant/
├── backend/
│   ├── agents/        # LangGraph agent definitions
│   ├── tools/         # Code analyzer, bug detector, GitHub, JIRA tools
│   ├── rag/           # Embeddings, vector store, retriever
│   ├── api/           # FastAPI routes
│   └── utils/         # Helpers
├── frontend/          # React + TypeScript UI
└── data/              # Docs and uploads
```

## Getting Started
```bash
# Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Fill in your keys
uvicorn backend.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```
