from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.schemas.messages import (
    CreateMessageRequest,
    MessageResponse,
)
from app.db.message_repository import (
    create_message,
    get_session_messages,
)
from app.db.session_repository import get_session


router = APIRouter(
    prefix="/api/sessions/{session_id}/messages",
    tags=["messages"],
)


@router.post("", response_model=MessageResponse)
def create_new_message(
    session_id: UUID,
    request: CreateMessageRequest,
) -> MessageResponse:
    if get_session(session_id) is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "SESSION_NOT_FOUND",
                "message": "Session not found.",
            },
        )

    message = create_message(
        session_id=session_id,
        role=request.role,
        content=request.content,
    )

    return MessageResponse(
        id=message["id"],
        session_id=str(message["session_id"]),
        role=message["role"],
        content=message["content"],
        created_at=message["created_at"].isoformat(),
    )


@router.get("", response_model=list[MessageResponse])
def get_messages(
    session_id: UUID,
) -> list[MessageResponse]:
    if get_session(session_id) is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "SESSION_NOT_FOUND",
                "message": "Session not found.",
            },
        )

    messages = get_session_messages(session_id)

    return [
        MessageResponse(
            id=message["id"],
            session_id=str(message["session_id"]),
            role=message["role"],
            content=message["content"],
            created_at=message["created_at"].isoformat(),
        )
        for message in messages
    ]