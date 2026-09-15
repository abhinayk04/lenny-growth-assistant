from pathlib import Path

from app.ingestion.chunker import chunk_transcript
from app.ingestion.parser import parse_transcript


CORPUS_DIR = Path("data/transcripts/source/episodes")


def test_chunk_real_transcript():
    path = next(CORPUS_DIR.rglob("transcript.md"))

    episode = parse_transcript(path)
    chunks = chunk_transcript(episode)

    assert chunks
    assert all(chunk.episode_id == episode.episode_id for chunk in chunks)
    assert all(chunk.title == episode.title for chunk in chunks)
    assert all(chunk.text for chunk in chunks)


def test_chunk_preserves_source_metadata():
    path = next(CORPUS_DIR.rglob("transcript.md"))

    episode = parse_transcript(path)
    chunks = chunk_transcript(episode)

    first = chunks[0]

    assert first.episode_id == episode.episode_id
    assert first.guest == episode.guest
    assert first.youtube_url == episode.youtube_url
    assert first.video_id == episode.video_id
    assert first.publish_date == episode.publish_date
    assert first.chunk_index == 0


def test_chunk_preserves_speaker_information():
    path = next(CORPUS_DIR.rglob("transcript.md"))

    episode = parse_transcript(path)
    chunks = chunk_transcript(episode)

    assert any(chunk.speakers for chunk in chunks)

    for chunk in chunks:
        assert isinstance(chunk.speakers, list)
        assert all(speaker.strip() for speaker in chunk.speakers)


def test_chunk_preserves_timestamps_when_available():
    path = next(CORPUS_DIR.rglob("transcript.md"))

    episode = parse_transcript(path)
    chunks = chunk_transcript(episode)

    timestamped_chunks = [
        chunk
        for chunk in chunks
        if chunk.start_timestamp is not None
    ]

    assert timestamped_chunks

    for chunk in timestamped_chunks:
        assert chunk.end_timestamp is not None


def test_chunk_indices_are_sequential():
    path = next(CORPUS_DIR.rglob("transcript.md"))

    episode = parse_transcript(path)
    chunks = chunk_transcript(episode)

    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))


def test_all_corpus_transcripts_chunk():
    files = list(CORPUS_DIR.rglob("transcript.md"))

    assert len(files) == 303

    total_chunks = 0

    for path in files:
        episode = parse_transcript(path)
        chunks = chunk_transcript(episode)

        assert chunks
        assert all(chunk.text for chunk in chunks)

        total_chunks += len(chunks)

    assert total_chunks > 303