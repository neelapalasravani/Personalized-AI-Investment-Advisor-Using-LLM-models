import asyncio
import json
from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain.schema import HumanMessage, SystemMessage

from src.api.config import AppState
from src.api.dependencies import get_state
from src.api.schemas import ChatStreamRequest

router = APIRouter(tags=["chat"])

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful financial assistant focused on long-term ETF investing. "
    "Answer clearly, cite reasoning, and avoid speculative claims."
)


async def _sse_iterator(llm, messages) -> AsyncIterator[bytes]:
    """Yield token deltas as Server-Sent Events.

    The wire format follows the ``data: <json>\\n\\n`` SSE convention used by
    the OpenAI streaming API, terminated with a ``[DONE]`` sentinel so browser
    clients can detect end-of-stream without relying on connection close.
    """
    try:
        async for chunk in llm.astream(messages):
            text = getattr(chunk, "content", "") or ""
            if not text:
                continue
            payload = json.dumps({"delta": text})
            yield f"data: {payload}\n\n".encode("utf-8")
        yield b"data: [DONE]\n\n"
    except asyncio.CancelledError:
        # Client disconnected; let Starlette clean up the response.
        raise
    except Exception as exc:  # noqa: BLE001 - surfaced to the client as SSE error event
        err = json.dumps({"error": str(exc)})
        yield f"event: error\ndata: {err}\n\n".encode("utf-8")


@router.post("/chat/stream")
async def chat_stream(
    req: ChatStreamRequest, state: AppState = Depends(get_state)
) -> StreamingResponse:
    if req.model not in state.llm_instances:
        raise HTTPException(
            status_code=400, detail=f"Unknown model: {req.model}"
        )

    llm = state.llm_instances[req.model]
    messages = [
        SystemMessage(content=req.system_prompt or DEFAULT_SYSTEM_PROMPT),
        HumanMessage(content=req.question),
    ]

    return StreamingResponse(
        _sse_iterator(llm, messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            # Disable proxy buffering (nginx) so tokens flush immediately.
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
