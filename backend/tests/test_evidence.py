from app.ingestion.evidence import retrieve_with_evidence_gate


def test_product_growth_question_has_sufficient_evidence():
    decision = retrieve_with_evidence_gate(
        "How should a product team improve user retention?"
    )

    assert decision.sufficient is True
    assert decision.results


def test_unrelated_question_is_rejected():
    decision = retrieve_with_evidence_gate(
        "What is the capital of France?"
    )

    assert decision.sufficient is False
    assert decision.results
