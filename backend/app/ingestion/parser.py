from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class TranscriptEpisode:
    episode_id: str
    guest: str | None
    title: str
    youtube_url: str | None
    video_id: str | None
    publish_date: str | None
    description: str | None
    duration_seconds: float | None
    duration: str | None
    view_count: int | None
    channel: str | None
    keywords: list[str]
    transcript: str


def _split_frontmatter(content: str) -> tuple[str, str]:
    """Split YAML frontmatter from Markdown body."""
    if not content.startswith("---"):
        raise ValueError("Transcript does not start with YAML frontmatter")

    parts = content.split("---", 2)

    if len(parts) != 3:
        raise ValueError("Invalid YAML frontmatter structure")

    _, frontmatter, body = parts
    return frontmatter.strip(), body.strip()


def _normalize_text(text: str) -> str:
    """Normalize whitespace without destroying transcript structure."""
    lines = [line.rstrip() for line in text.splitlines()]

    normalized: list[str] = []
    previous_blank = False

    for line in lines:
        if not line.strip():
            if not previous_blank:
                normalized.append("")
            previous_blank = True
            continue

        normalized.append(line.strip())
        previous_blank = False

    return "\n".join(normalized).strip()


def parse_transcript(path: Path) -> TranscriptEpisode:
    """Parse one Lenny transcript Markdown file."""
    content = path.read_text(encoding="utf-8")

    frontmatter_text, body = _split_frontmatter(content)
    metadata: dict[str, Any] = yaml.safe_load(frontmatter_text) or {}

    title = str(metadata.get("title") or "").strip()

    if not title:
        for line in body.splitlines():
            line = line.strip()
            if line.startswith("# ") and not line.startswith("## "):
                title = line[2:].strip()
                break

    if not title:
        raise ValueError(f"Transcript is missing title: {path}")

    transcript = _normalize_text(body)

    if not transcript:
        raise ValueError(f"Transcript body is empty: {path}")

    return TranscriptEpisode(
        episode_id=path.parent.name,
        guest=metadata.get("guest"),
        title=title,
        youtube_url=metadata.get("youtube_url"),
        video_id=metadata.get("video_id"),
        publish_date=(
            str(metadata["publish_date"])
            if metadata.get("publish_date") is not None
            else None
        ),
        description=metadata.get("description"),
        duration_seconds=(
            float(metadata["duration_seconds"])
            if metadata.get("duration_seconds") is not None
            else None
        ),
        duration=metadata.get("duration"),
        view_count=(
            int(metadata["view_count"])
            if metadata.get("view_count") is not None
            else None
        ),
        channel=metadata.get("channel"),
        keywords=list(metadata.get("keywords") or []),
        transcript=transcript,
    )
