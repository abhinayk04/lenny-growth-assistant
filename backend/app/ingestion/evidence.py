from dataclasses import dataclass

from app.ingestion.hybrid_retrieval import hybrid_search


@dataclass(frozen=True)
class EvidenceDecision:
    sufficient: bool
    results: list[dict]
    reason: str


MIN_VECTOR_SIMILARITY = 0.45


def retrieve_with_evidence_gate(
    query: str,
    limit: int = 5,
) -> EvidenceDecision:
    results = hybrid_search(
        query,
        limit=limit,
        candidate_limit=10,
    )

    if not results:
        return EvidenceDecision(
            sufficient=False,
            results=[],
            reason="No transcript evidence was retrieved.",
        )

    strongest_similarity = max(
        result["vector_similarity"]
        for result in results
    )

    if strongest_similarity < MIN_VECTOR_SIMILARITY:
        return EvidenceDecision(
            sufficient=False,
            results=results,
            reason=(
                "Retrieved evidence did not meet the "
                "minimum semantic relevance threshold."
            ),
        )

    return EvidenceDecision(
        sufficient=True,
        results=results,
        reason="Retrieved evidence meets the minimum semantic relevance threshold.",
    )
