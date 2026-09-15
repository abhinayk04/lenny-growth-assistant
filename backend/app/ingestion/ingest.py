from pathlib import Path

from app.db.repository import (
    complete_ingestion_run,
    fail_ingestion_run,
    insert_episode,
    insert_chunks,
    start_ingestion_run,
)
from app.ingestion.chunker import chunk_transcript
from app.ingestion.embeddings import EmbeddingService
from app.ingestion.parser import parse_transcript


SOURCE_DIR = Path("data/transcripts/source/episodes")


def ingest_corpus() -> None:
    transcript_files = sorted(SOURCE_DIR.glob("*/transcript.md"))

    if not transcript_files:
        raise FileNotFoundError(
            f"No transcript files found in {SOURCE_DIR}"
        )

    embedding_service = EmbeddingService()
    run_id = start_ingestion_run(str(SOURCE_DIR))

    episodes_processed = 0
    chunks_created = 0

    try:
        for index, transcript_path in enumerate(transcript_files, start=1):
            episode = parse_transcript(transcript_path)
            chunks = chunk_transcript(episode)

            insert_episode(
                {
                    "id": episode.episode_id,
                    "guest": episode.guest,
                    "title": episode.title,
                    "youtube_url": episode.youtube_url,
                    "video_id": episode.video_id,
                    "publish_date": episode.publish_date,
                    "description": episode.description,
                    "duration_seconds": episode.duration_seconds,
                    "duration": episode.duration,
                    "view_count": episode.view_count,
                    "channel": episode.channel,
                    "keywords": episode.keywords,
                }
            )

            embeddings = embedding_service.embed_many(
                [chunk.text for chunk in chunks]
            )

            insert_chunks(chunks, embeddings)

            episodes_processed += 1
            chunks_created += len(chunks)

            print(
                f"[{index}/{len(transcript_files)}] "
                f"{episode.episode_id}: "
                f"{len(chunks)} chunks"
            )

        complete_ingestion_run(
            run_id,
            episodes_processed,
            chunks_created,
        )

        print(
            f"Ingestion complete: "
            f"{episodes_processed} episodes, "
            f"{chunks_created} chunks"
        )

    except Exception as exc:
        fail_ingestion_run(run_id, str(exc))
        raise


if __name__ == "__main__":
    ingest_corpus()
