from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest
from app.services import chat_service

router = APIRouter()


@router.post("/chat")
async def chat(
    request: Request,
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async def event_generator():
        async for event in chat_service.stream_chat_response(
            db=db,
            user_id=current_user.id,
            workspace_id=current_user.workspace_id,
            message=body.message,
            conversation_id=body.conversation_id,
        ):
            if await request.is_disconnected():
                break
            yield event

    return EventSourceResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
