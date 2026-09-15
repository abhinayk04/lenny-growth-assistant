from dataclasses import dataclass
import re

from app.ingestion.parser import TranscriptEpisode


@dataclass(frozen=True)
class TranscriptChunk:
    episode_id: str
    guest: str | None
    title: str
    youtube_url: str | None
    video_id: str | None
    publish_date: str | None
    chunk_index: int
    speakers: list[str]
    start_timestamp: str | None
    end_timestamp: str | None
    text: str


@dataclass(frozen=True)
class SpeakerTurn:
    speaker: str
    timestamp: str | None
    text: str


SPEAKER_PATTERN = re.compile(
    r"^(?P<speaker>[^:\n]+?)(?:\s+\((?P<timestamp>\d{1,2}:\d{2}:\d{2})\))?:\s*(?P<text>.*)$"
)


def _parse_speaker_turns(transcript: str) -> list[SpeakerTurn]:
    """Parse transcript lines into speaker turns."""
    turns: list[SpeakerTurn] = []

    current_speaker: str | None = None
    current_timestamp: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_speaker, current_timestamp, current_lines

        if current_speaker and current_lines:
            text = " ".join(line.strip() for line in current_lines).strip()

            if text:
                turns.append(
                    SpeakerTurn(
                        speaker=current_speaker,
                        timestamp=current_timestamp,
                        text=text,
                    )
                )

        current_speaker = None
        current_timestamp = None
        current_lines = []

    for line in transcript.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        match = SPEAKER_PATTERN.match(stripped)

        if match:
            flush()

            current_speaker = match.group("speaker").strip()
            current_timestamp = match.group("timestamp")

            first_text = match.group("text").strip()

            if first_text:
                current_lines.append(first_text)

        elif current_speaker:
            current_lines.append(stripped)

    flush()

    return turns


def _estimate_tokens(text: str) -> int:
    """Estimate tokens using whitespace-separated words."""
    return len(re.findall(r"\S+", text))


def _format_turn(turn: SpeakerTurn) -> str:
    """Format one speaker turn for a chunk."""
    if turn.timestamp:
        return f"{turn.speaker} ({turn.timestamp}): {turn.text}"

    return f"{turn.speaker}: {turn.text}"


def _split_large_turn(
    turn: SpeakerTurn,
    target_tokens: int,
) -> list[SpeakerTurn]:
    """Split an unusually large speaker turn into smaller pieces."""
    words = turn.text.split()

    if len(words) <= target_tokens:
        return [turn]

    pieces: list[SpeakerTurn] = []

    for start in range(0, len(words), target_tokens):
        piece_text = " ".join(words[start : start + target_tokens])

        pieces.append(
            SpeakerTurn(
                speaker=turn.speaker,
                timestamp=turn.timestamp if start == 0 else None,
                text=piece_text,
            )
        )

    return pieces


def _chunk_turns(
    turns: list[SpeakerTurn],
    target_tokens: int = 1200,
    overlap_tokens: int = 200,
) -> list[list[SpeakerTurn]]:
    """Group speaker turns into approximately target-sized chunks."""
    if not turns:
        return []

    normalized_turns: list[SpeakerTurn] = []

    for turn in turns:
        normalized_turns.extend(
            _split_large_turn(turn, target_tokens)
        )

    chunks: list[list[SpeakerTurn]] = []
    current: list[SpeakerTurn] = []
    current_tokens = 0

    for turn in normalized_turns:
        turn_tokens = _estimate_tokens(_format_turn(turn))

        if current and current_tokens + turn_tokens > target_tokens:
            chunks.append(current)

            overlap: list[SpeakerTurn] = []
            overlap_count = 0

            for previous_turn in reversed(current):
                previous_tokens = _estimate_tokens(
                    _format_turn(previous_turn)
                )

                if overlap_count + previous_tokens > overlap_tokens:
                    break

                overlap.insert(0, previous_turn)
                overlap_count += previous_tokens

            current = overlap
            current_tokens = overlap_count

        current.append(turn)
        current_tokens += turn_tokens

    if current:
        chunks.append(current)

    return chunks


def chunk_transcript(
    episode: TranscriptEpisode,
    target_tokens: int = 1200,
    overlap_tokens: int = 200,
) -> list[TranscriptChunk]:
    """Convert one parsed episode into source-traceable chunks."""
    turns = _parse_speaker_turns(episode.transcript)

    if not turns:
        raise ValueError(
            f"Transcript contains no speaker turns: {episode.episode_id}"
        )

    grouped_chunks = _chunk_turns(
        turns,
        target_tokens=target_tokens,
        overlap_tokens=overlap_tokens,
    )

    chunks: list[TranscriptChunk] = []

    for index, chunk_turns in enumerate(grouped_chunks):
        text = "\n\n".join(
            _format_turn(turn)
            for turn in chunk_turns
        )

        speakers = list(
            dict.fromkeys(turn.speaker for turn in chunk_turns)
        )

        timestamps = [
            turn.timestamp
            for turn in chunk_turns
            if turn.timestamp is not None
        ]

        chunks.append(
            TranscriptChunk(
                episode_id=episode.episode_id,
                guest=episode.guest,
                title=episode.title,
                youtube_url=episode.youtube_url,
                video_id=episode.video_id,
                publish_date=episode.publish_date,
                chunk_index=index,
                speakers=speakers,
                start_timestamp=timestamps[0] if timestamps else None,
                end_timestamp=timestamps[-1] if timestamps else None,
                text=text,
            )
        )

    return chunks