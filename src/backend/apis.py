"""API routes for the Menu Engineering Agent backend."""
from typing import Callable, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


def build_router(
    answer_fn: Callable[[str], str],
    tools_fn: Callable[[], Dict[str, Any]],
) -> APIRouter:
    router = APIRouter()

    @router.post("/ask", response_model=AskResponse)
    def ask_question(payload: AskRequest):
        try:
            answer = answer_fn(payload.question)
            return AskResponse(answer=answer)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @router.get("/tools")
    def get_tools():
        try:
            return {"tools": tools_fn()}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return router
