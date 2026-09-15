from uuid import UUID

from sqlalchemy import text

from app.db.database import engine


def create_message(
    session_id: UUID,
    role: str,
    content: str,
) -> dict:
    query = text("""
        INSERT INTO messages (
            session_id,
            role,
            content
        )
        VALUES (
            :session_id,
            :role,
            :content
        )
        RETURNING
            id,
            session_id,
            role,
            content,
            created_at
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {
                "session_id": session_id,
                "role": role,
                "content": content,
            },
        ).mappings().one()

    return dict(result)


def get_session_messages(
    session_id: UUID,
) -> list[dict]:
    query = text("""
        SELECT
            id,
            session_id,
            role,
            content,
            created_at
        FROM messages
        WHERE session_id = :session_id
        ORDER BY created_at ASC, id ASC
    """)

    with engine.connect() as connection:
        results = connection.execute(
            query,
            {"session_id": session_id},
        ).mappings().all()

    return [dict(result) for result in results]