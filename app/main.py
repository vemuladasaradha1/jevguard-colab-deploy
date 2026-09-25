
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .agent import JevGuardAgent
from .config import get_settings
from .schemas import ChatRequest, ChatResponse

load_dotenv()

settings = get_settings()
agent: JevGuardAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent

    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is required.")

    if not settings.typesafe_api_key:
        raise RuntimeError("TYPESAFE_API_KEY is required.")

    if settings.langsmith_tracing and settings.langsmith_api_key:
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project

    agent = JevGuardAgent(settings)
    yield
    agent = None


app = FastAPI(
    title="JevGuard",
    version="1.0.0",
    description="Decision-controlled AI agent using Jev + LangGraph + Groq.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


@app.get("/")
async def root():
    return FileResponse("app/static/index.html")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "jevguard",
        "jev_configured": bool(settings.typesafe_api_key),
        "groq_configured": bool(settings.groq_api_key),
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    if agent is None:
        raise HTTPException(
            status_code=503,
            detail="Agent is still starting.",
        )

    try:
        return agent.invoke(payload.query)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {exc}",
        ) from exc
