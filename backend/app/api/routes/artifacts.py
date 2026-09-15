from uuid import UUID
from fastapi import APIRouter, HTTPException

from app.agent.service import generate_artifact_content
from app.api.schemas.artifacts import CreateArtifactRequest, ArtifactResponse
from app.db.artifact_repository import create_artifact, get_artifact, get_session_artifacts
from app.db.message_repository import get_session_messages
from app.db.session_repository import get_session

router = APIRouter(
    prefix="/api",
    tags=["artifacts"],
)


@router.post("/sessions/{session_id}/artifacts", response_model=ArtifactResponse)
def generate_and_save_artifact(
    session_id: UUID,
    request: CreateArtifactRequest,
) -> ArtifactResponse:
    if get_session(session_id) is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "SESSION_NOT_FOUND",
                "message": "Session not found.",
            },
        )

    previous_messages = get_session_messages(session_id)
    
    # If explicit content provided, use it; otherwise generate content from history/topic
    if request.content and request.content.strip():
        artifact_content = request.content
    else:
        history_summary = "\n".join(f"{m['role']}: {m['content']}" for m in previous_messages[-4:])
        context = f"Title: {request.title}\nRecent Conversation:\n{history_summary}"
        artifact_content = generate_artifact_content(
            title=request.title,
            artifact_type=request.type,
            context=context,
        )

    artifact = create_artifact(
        session_id=session_id,
        title=request.title,
        artifact_type=request.type,
        content=artifact_content,
    )

    return ArtifactResponse(
        id=str(artifact["id"]),
        session_id=str(artifact["session_id"]),
        title=artifact["title"],
        type=artifact["type"],
        content=artifact["content"],
        created_at=artifact["created_at"].isoformat(),
    )


@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
def get_artifact_by_id(artifact_id: UUID) -> ArtifactResponse:
    artifact = get_artifact(artifact_id)
    if not artifact:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "ARTIFACT_NOT_FOUND",
                "message": "Artifact not found.",
            },
        )

    return ArtifactResponse(
        id=str(artifact["id"]),
        session_id=str(artifact["session_id"]),
        title=artifact["title"],
        type=artifact["type"],
        content=artifact["content"],
        created_at=artifact["created_at"].isoformat(),
    )


@router.get("/sessions/{session_id}/artifacts", response_model=list[ArtifactResponse])
def get_artifacts_for_session(session_id: UUID) -> list[ArtifactResponse]:
    if get_session(session_id) is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "SESSION_NOT_FOUND",
                "message": "Session not found.",
            },
        )

    artifacts = get_session_artifacts(session_id)
    return [
        ArtifactResponse(
            id=str(a["id"]),
            session_id=str(a["session_id"]),
            title=a["title"],
            type=a["type"],
            content=a["content"],
            created_at=a["created_at"].isoformat(),
        )
        for a in artifacts
    ]
