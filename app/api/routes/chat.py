from __future__ import annotations
import json
import httpx
from datetime import datetime
from typing import Any, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.llm.deps import get_llm_client
from app.llm.client import LlmClient
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/v1", tags=["chat"])

@router.get("/healthz")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, llm: LlmClient = Depends(get_llm_client)):
    try:
        return await llm.chat(req)
    except httpx.HTTPStatusError as e:
        status = e.response.status_code if e.response is not None else 502
        detail = e.response.text if e.response is not None else str(e)
        raise HTTPException(status_code=status, detail=detail)

@router.post("/chat/stream")
async def chat_stream(req: ChatRequest, llm: LlmClient = Depends(get_llm_client)):
    if not req.stream:
        req.stream = True
    async def event_source() -> AsyncGenerator[bytes, None]:
        try:
            async for chunk in llm.chat_stream(req):
                yield chunk.encode("utf-8")
        except httpx.HTTPStatusError as e:
            err = json.dumps({"error": str(e)})
            yield f"data: {err}\n\n".encode("utf-8")
    return StreamingResponse(event_source(), media_type="text/event-stream")