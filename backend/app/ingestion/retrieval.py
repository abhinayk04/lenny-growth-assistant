from dataclasses import dataclass

from sqlalchemy import text

from app.db.database import engine
from app.ingestion.embeddings import EmbeddingService


@dataclass(frozen=True)
class RetrievalResult:
    chunk_id: int
    episode_id: str
    chunk_index: int
    title: str
    guest: str | None
    youtube_url: str | None
    publish_date: str | None
    speakers: list[str]
    start_timestamp: str | None
    end_timestamp: str | None
    text: str
    similarity: float


def search_similar_chunks(
    query: str,
    limit: int = 5,
) -> list[RetrievalResult]:
    embedding_service = EmbeddingService()
    query_embedding = embedding_service.embed(query)

    sql = text("""
        SELECT
            tc.id,
            tc.episode_id,
            tc.chunk_index,
            tc.speakers,
            tc.start_timestamp,
            tc.end_timestamp,
            tc.text,
            e.title,
            e.guest,
            e.youtube_url,
            e.publish_date,
            1 - (tc.embedding <=> CAST(:embedding AS vector)) AS similarity
        FROM transcript_chunks tc
        JOIN episodes e
            ON e.id = tc.episode_id
        WHERE tc.embedding IS NOT NULL
        ORDER BY tc.embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
    """)

    with engine.connect() as connection:
        result = connection.execute(
            sql,
            {
                "embedding": str(query_embedding),
                "limit": limit,
            },
        )

        return [
            RetrievalResult(
                chunk_id=row.id,
                episode_id=row.episode_id,
                chunk_index=row.chunk_index,
                title=row.title,
                guest=row.guest,
                youtube_url=row.youtube_url,
                publish_date=str(row.publish_date)
                if row.publish_date
                else None,
                speakers=row.speakers or [],
                start_timestamp=row.start_timestamp,
                end_timestamp=row.end_timestamp,
                text=row.text,
                similarity=float(row.similarity),
            )
            for row in result
        ]
