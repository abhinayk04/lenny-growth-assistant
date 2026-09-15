from collections import defaultdict

from sqlalchemy import text

from app.db.database import engine
from app.ingestion.retrieval import search_similar_chunks


def search_keyword_chunks(
    query: str,
    limit: int = 10,
) -> list[dict]:
    sql = text("""
        SELECT
            tc.id AS chunk_id,
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
            ts_rank_cd(
                to_tsvector('english', tc.text),
                websearch_to_tsquery('english', :query)
            ) AS keyword_score
        FROM transcript_chunks tc
        JOIN episodes e
            ON e.id = tc.episode_id
        WHERE to_tsvector('english', tc.text)
              @@ websearch_to_tsquery('english', :query)
        ORDER BY keyword_score DESC
        LIMIT :limit
    """)

    with engine.connect() as connection:
        result = connection.execute(
            sql,
            {
                "query": query,
                "limit": limit,
            },
        )

        return [dict(row._mapping) for row in result]


def reciprocal_rank_fusion(
    vector_results: list,
    keyword_results: list[dict],
    k: int = 60,
) -> list[dict]:
    scores = defaultdict(float)
    items = {}

    for rank, result in enumerate(vector_results, start=1):
        chunk_id = result.chunk_id
        scores[chunk_id] += 1 / (k + rank)

        items[chunk_id] = {
            "chunk_id": result.chunk_id,
            "episode_id": result.episode_id,
            "chunk_index": result.chunk_index,
            "title": result.title,
            "guest": result.guest,
            "youtube_url": result.youtube_url,
            "publish_date": result.publish_date,
            "speakers": result.speakers,
            "start_timestamp": result.start_timestamp,
            "end_timestamp": result.end_timestamp,
            "text": result.text,
            "vector_similarity": result.similarity,
            "keyword_score": 0.0,
        }

    for rank, result in enumerate(keyword_results, start=1):
        chunk_id = result["chunk_id"]
        scores[chunk_id] += 1 / (k + rank)

        if chunk_id not in items:
            items[chunk_id] = {
                "chunk_id": result["chunk_id"],
                "episode_id": result["episode_id"],
                "chunk_index": result["chunk_index"],
                "title": result["title"],
                "guest": result["guest"],
                "youtube_url": result["youtube_url"],
                "publish_date": (
                    str(result["publish_date"])
                    if result["publish_date"]
                    else None
                ),
                "speakers": result["speakers"] or [],
                "start_timestamp": result["start_timestamp"],
                "end_timestamp": result["end_timestamp"],
                "text": result["text"],
                "vector_similarity": 0.0,
                "keyword_score": 0.0,
            }

        items[chunk_id]["keyword_score"] = float(
            result["keyword_score"]
        )

    ranked = []

    for chunk_id, score in scores.items():
        item = items[chunk_id]
        item["rrf_score"] = score
        ranked.append(item)

    ranked.sort(
        key=lambda item: item["rrf_score"],
        reverse=True,
    )

    return ranked


def hybrid_search(
    query: str,
    limit: int = 5,
    candidate_limit: int = 15,
) -> list[dict]:
    vector_results = search_similar_chunks(
        query,
        candidate_limit,
    )

    keyword_results = search_keyword_chunks(
        query,
        candidate_limit,
    )

    fused_results = reciprocal_rank_fusion(
        vector_results,
        keyword_results,
    )

    # Deduplicate by episode_id so distinct episodes are returned for user display
    deduped = []
    seen_episodes = set()
    for item in fused_results:
        ep_id = item.get("episode_id")
        if ep_id not in seen_episodes:
            seen_episodes.add(ep_id)
            deduped.append(item)
            if len(deduped) >= limit:
                break

    if len(deduped) < limit:
        for item in fused_results:
            if item not in deduped:
                deduped.append(item)
                if len(deduped) >= limit:
                    break

    return deduped
