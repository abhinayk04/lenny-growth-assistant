from uuid import UUID, uuid4

from sqlalchemy import text

from app.db.database import engine


def create_session() -> UUID:
    session_id = uuid4()

    query = text("""
        INSERT INTO sessions (id)
        VALUES (:session_id)
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {"session_id": session_id},
        )

    return session_id


def get_session(session_id: UUID) -> dict | None:
    query = text("""
        SELECT
            id,
            created_at,
            updated_at
        FROM sessions
        WHERE id = :session_id
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {"session_id": session_id},
        ).mappings().first()

    if result is None:
        return None

    return dict(result)