import re
import uuid
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import text

from app.db.database import engine


def sanitize_html(content: str) -> str:
    """Sanitize HTML content by stripping script tags and dangerous attributes."""
    if not content:
        return ""
    # Remove script tags and content
    cleaned = re.sub(r"<script.*?>.*?</script>", "", content, flags=re.DOTALL | re.IGNORECASE)
    # Remove inline event handlers
    cleaned = re.sub(r"\s+on\w+=(['\"]).*?\1", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+on\w+=\S+", "", cleaned, flags=re.IGNORECASE)
    # Remove javascript: URLs
    cleaned = re.sub(r"javascript:[^\s'\"]+", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def create_artifact(
    session_id: UUID,
    title: str,
    artifact_type: str,
    content: str,
) -> dict:
    artifact_id = uuid.uuid4()
    sanitized_content = sanitize_html(content) if artifact_type.lower() in ("html", "html/css") else content.strip()

    query = text("""
        INSERT INTO artifacts (
            id,
            session_id,
            title,
            type,
            content
        )
        VALUES (
            :id,
            :session_id,
            :title,
            :type,
            :content
        )
        RETURNING
            id,
            session_id,
            title,
            type,
            content,
            created_at
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {
                "id": artifact_id,
                "session_id": session_id,
                "title": title,
                "type": artifact_type,
                "content": sanitized_content,
            },
        ).mappings().one()

    return dict(result)


def get_artifact(artifact_id: UUID) -> Optional[dict]:
    query = text("""
        SELECT
            id,
            session_id,
            title,
            type,
            content,
            created_at
        FROM artifacts
        WHERE id = :id
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {"id": artifact_id},
        ).mappings().first()

    return dict(result) if result else None


def get_session_artifacts(session_id: UUID) -> List[dict]:
    query = text("""
        SELECT
            id,
            session_id,
            title,
            type,
            content,
            created_at
        FROM artifacts
        WHERE session_id = :session_id
        ORDER BY created_at DESC
    """)

    with engine.connect() as connection:
        results = connection.execute(
            query,
            {"session_id": session_id},
        ).mappings().all()

    return [dict(r) for r in results]
