from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.config import AppSettings, build_app_state
from src.api.routers import chat, health, query


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = AppSettings.load()
    app.state.settings = settings
    app.state.app_state = build_app_state(settings)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="RoBrain Investment Advisor API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(query.router, prefix="/v1")
    app.include_router(chat.router, prefix="/v1")
    return app


app = create_app()
