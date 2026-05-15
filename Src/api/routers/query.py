from fastapi import APIRouter, Depends, HTTPException

from src.api.config import AppState
from src.api.dependencies import get_state
from src.api.schemas import QueryRequest, QueryResponse
from src.Main_pipeline import generate_sql, is_prompt_injection, run_sql_query
from src.utils import format_web_summary
from src.web_search import tavily_search

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def run_query(
    req: QueryRequest, state: AppState = Depends(get_state)
) -> QueryResponse:
    if req.model not in state.llm_instances:
        raise HTTPException(
            status_code=400, detail=f"Unknown model: {req.model}"
        )

    if is_prompt_injection(req.question):
        return QueryResponse(
            answer="Security alert: Unsafe input detected.",
            source="blocked",
        )

    llm = state.llm_instances[req.model]
    sql = generate_sql(llm, req.question, state.schema)
    if sql:
        result = run_sql_query(sql, state.db_file)
        return QueryResponse(answer=result, sql=sql, source="sql")

    web = tavily_search(req.question, state.api_keys["tavily"])
    return QueryResponse(answer=format_web_summary(req.question, web), source="web")
