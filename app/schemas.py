
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=8000)


class ChatResponse(BaseModel):
    answer: str
    status: str
    tools_used: list[str] = []
    risk: float | None = None
    quality: float | None = None
    grounded: float | None = None
    safe: float | None = None
    latency_ms: int
    request_id: str
