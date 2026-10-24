from pydantic import BaseModel, Field
from typing import Literal


class TraceEvent(BaseModel):
    step_index: int = Field(ge=0)
    actor: Literal["model", "application", "tool"]
    event: str
    tool_name: str | None = None
    status: str
