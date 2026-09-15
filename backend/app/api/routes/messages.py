from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.agent.service import answer_question
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


@router.post("")
def create_new_message(
    session_id: UUID,
    request: CreateMessageRequest,
) -> dict:
    if get_session(session_id) is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "SESSION_NOT_FOUND",
                "message": "Session not found.",
            },
        )

    previous_messages = get_session_messages(session_id)

    user_message = create_message(
        session_id=session_id,
        role="user",
        content=request.content,
    )

    result = answer_question(request.content, history=previous_messages)

    assistant_message = create_message(
        session_id=session_id,
        role="assistant",
        content=result["answer"],
    )

    return {
        "user_message": MessageResponse(
            id=user_message["id"],
            session_id=str(user_message["session_id"]),
            role=user_message["role"],
            content=user_message["content"],
            created_at=user_message["created_at"].isoformat(),
        ),
        "assistant_message": MessageResponse(
            id=assistant_message["id"],
            session_id=str(assistant_message["session_id"]),
            role=assistant_message["role"],
            content=assistant_message["content"],
            created_at=assistant_message["created_at"].isoformat(),
        ),
        "grounded": result["grounded"],
        "sources": result["sources"],
    }


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