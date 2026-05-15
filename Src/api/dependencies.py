from fastapi import Request

from src.api.config import AppState


def get_state(request: Request) -> AppState:
    """FastAPI dependency that exposes the singleton ``AppState``."""
    return request.app.state.app_state
