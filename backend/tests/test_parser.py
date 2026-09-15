from pathlib import Path

import pytest

from app.ingestion.parser import parse_transcript


CORPUS_DIR = Path("data/transcripts/source/episodes")


def test_parse_real_transcript():
    path = next(CORPUS_DIR.rglob("transcript.md"))

    episode = parse_transcript(path)

    assert episode.episode_id
    assert episode.title
    assert episode.transcript
    assert isinstance(episode.keywords, list)


def test_parse_teaser_uses_h1_title():
    path = CORPUS_DIR / "teaser_2021" / "transcript.md"

    episode = parse_transcript(path)

    assert episode.title == "Teaser_2021"
    assert episode.transcript


def test_missing_frontmatter_raises(tmp_path):
    path = tmp_path / "transcript.md"
    path.write_text("# Test\n\nTranscript content", encoding="utf-8")

    with pytest.raises(ValueError, match="frontmatter"):
        parse_transcript(path)


def test_missing_title_raises(tmp_path):
    path = tmp_path / "transcript.md"
    path.write_text(
        "---\nguest: Test Guest\n---\n\nTranscript content",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing title"):
        parse_transcript(path)


def test_empty_transcript_raises(tmp_path):
    path = tmp_path / "transcript.md"
    path.write_text(
        "---\ntitle: Test Episode\n---\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="empty"):
        parse_transcript(path)


def test_corpus_all_transcripts_parse():
    files = list(CORPUS_DIR.rglob("transcript.md"))

    assert len(files) == 303

    for path in files:
        episode = parse_transcript(path)

        assert episode.title
        assert episode.transcript
