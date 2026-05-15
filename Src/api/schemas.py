from typing import Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Natural-language question.")
    model: str = Field("Llama-3.3-70B", description="LLM model name to use.")


class QueryResponse(BaseModel):
    answer: str
    sql: Optional[str] = None
    source: str = Field(..., description='"sql" | "web" | "blocked"')


class ChatStreamRequest(BaseModel):
    question: str = Field(..., min_length=1)
    model: str = Field("Llama-3.3-70B")
    system_prompt: Optional[str] = None


class ModelsResponse(BaseModel):
    models: list[str]
