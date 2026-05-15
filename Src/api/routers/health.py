from fastapi import APIRouter, Depends

from src.api.config import AppState
from src.api.dependencies import get_state
from src.api.schemas import ModelsResponse

router = APIRouter(tags=["meta"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/v1/models", response_model=ModelsResponse)
async def list_models(state: AppState = Depends(get_state)) -> ModelsResponse:
    return ModelsResponse(models=list(state.llm_instances.keys()))
