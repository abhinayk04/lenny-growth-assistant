from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.db.session_repository import create_session, get_session


router = APIRouter(
    prefix="/api/sessions",
    tags=["sessions"],
)


@router.post("")
def create_new_session() -> dict:
    session_id = create_session()

    return {
        "id": str(session_id),
    }


@router.get("/{session_id}")
def get_existing_session(session_id: UUID) -> dict:
    session = get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "SESSION_NOT_FOUND",
                "message": "Session not found.",
            },
        )

    return {
        "id": str(session["id"]),
        "created_at": session["created_at"],
        "updated_at": session["updated_at"],
    }