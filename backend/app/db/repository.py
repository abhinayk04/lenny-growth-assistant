import json
from datetime import date

from sqlalchemy import text

from app.db.database import engine
from app.ingestion.chunker import TranscriptChunk


def insert_episode(episode: dict) -> None:
    query = text("""
        INSERT INTO episodes (
            id,
            guest,
            title,
            youtube_url,
            video_id,
            publish_date,
            description,
            duration_seconds,
            duration,
            view_count,
            channel,
            keywords
        )
        VALUES (
            :id,
            :guest,
            :title,
            :youtube_url,
            :video_id,
            :publish_date,
            :description,
            :duration_seconds,
            :duration,
            :view_count,
            :channel,
            CAST(:keywords AS jsonb)
        )
        ON CONFLICT (id) DO UPDATE SET
            guest = EXCLUDED.guest,
            title = EXCLUDED.title,
            youtube_url = EXCLUDED.youtube_url,
            video_id = EXCLUDED.video_id,
            publish_date = EXCLUDED.publish_date,
            description = EXCLUDED.description,
            duration_seconds = EXCLUDED.duration_seconds,
            duration = EXCLUDED.duration,
            view_count = EXCLUDED.view_count,
            channel = EXCLUDED.channel,
            keywords = EXCLUDED.keywords,
            updated_at = NOW()
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                **episode,
                "keywords": json.dumps(episode.get("keywords") or []),
            },
        )


def insert_chunks(
    chunks: list[TranscriptChunk],
    embeddings: list[list[float]],
) -> None:
    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings must have the same length")

    query = text("""
        INSERT INTO transcript_chunks (
            episode_id,
            chunk_index,
            speakers,
            start_timestamp,
            end_timestamp,
            text,
            embedding
        )
        VALUES (
            :episode_id,
            :chunk_index,
            CAST(:speakers AS jsonb),
            :start_timestamp,
            :end_timestamp,
            :text,
            :embedding
        )
        ON CONFLICT (episode_id, chunk_index) DO UPDATE SET
            speakers = EXCLUDED.speakers,
            start_timestamp = EXCLUDED.start_timestamp,
            end_timestamp = EXCLUDED.end_timestamp,
            text = EXCLUDED.text,
            embedding = EXCLUDED.embedding
    """)

    rows = []

    for chunk, embedding in zip(chunks, embeddings):
        rows.append(
            {
                "episode_id": chunk.episode_id,
                "chunk_index": chunk.chunk_index,
                "speakers": json.dumps(chunk.speakers),
                "start_timestamp": chunk.start_timestamp,
                "end_timestamp": chunk.end_timestamp,
                "text": chunk.text,
                "embedding": embedding,
            }
        )

    with engine.begin() as connection:
        connection.execute(query, rows)


def start_ingestion_run(source: str) -> int:
    query = text("""
        INSERT INTO ingestion_runs (status, source)
        VALUES ('running', :source)
        RETURNING id
    """)

    with engine.begin() as connection:
        result = connection.execute(query, {"source": source})
        return int(result.scalar_one())


def complete_ingestion_run(
    run_id: int,
    episodes_processed: int,
    chunks_created: int,
) -> None:
    query = text("""
        UPDATE ingestion_runs
        SET
            status = 'completed',
            episodes_processed = :episodes_processed,
            chunks_created = :chunks_created,
            completed_at = NOW()
        WHERE id = :run_id
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "run_id": run_id,
                "episodes_processed": episodes_processed,
                "chunks_created": chunks_created,
            },
        )


def fail_ingestion_run(run_id: int, error_message: str) -> None:
    query = text("""
        UPDATE ingestion_runs
        SET
            status = 'failed',
            error_message = :error_message,
            completed_at = NOW()
        WHERE id = :run_id
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "run_id": run_id,
                "error_message": error_message[:4000],
            },
        )


def count_episodes() -> int:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT COUNT(*) FROM episodes")
        )
        return int(result.scalar_one())


def count_chunks() -> int:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT COUNT(*) FROM transcript_chunks")
        )
        return int(result.scalar_one())
