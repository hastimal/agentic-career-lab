from pydantic import BaseModel


class AgentExecutionEvent(BaseModel):
    agent: str
    action: str
    status: str
    runtime: str
    duration_ms: float
    summary: str
    error_code: str | None = None
