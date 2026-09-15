from uuid import UUID
from fastapi import APIRouter, HTTPException

from app.agent.service import generate_ship30
from app.api.schemas.ship30 import Ship30Request, Ship30Response
from app.db.message_repository import get_session_messages
from app.db.session_repository import get_session

router = APIRouter(
    prefix="/api/sessions/{session_id}/ship30",
    tags=["ship30"],
)


@router.post("", response_model=Ship30Response)
def create_ship30_essay(
    session_id: UUID,
    request: Ship30Request,
) -> Ship30Response:
    if get_session(session_id) is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "SESSION_NOT_FOUND",
                "message": "Session not found.",
            },
        )

    previous_messages = get_session_messages(session_id)
    result = generate_ship30(request.topic, history=previous_messages)

    return Ship30Response(
        content=result["content"],
        sources=result["sources"],
        grounded=result["grounded"],
    )
