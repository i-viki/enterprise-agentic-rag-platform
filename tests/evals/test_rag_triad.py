import pytest
import json
import os
import time
from app.guardrails.self_rag_auditor import self_rag_auditor

@pytest.fixture
def benchmark_dataset():
    data_path = os.path.join(os.path.dirname(__file__), "benchmark_dataset.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_benchmark_dataset_integrity(benchmark_dataset):
    """Verifies golden benchmark dataset format and fields."""
    assert len(benchmark_dataset) >= 5
    for item in benchmark_dataset:
        assert "id" in item
        assert "query" in item
        assert "expected_answer" in item
        assert "ground_truth_context" in item

def test_rag_triad_faithfulness_evaluation(benchmark_dataset):
    """Automated CI Quality Gate: Asserts Faithfulness (Groundedness) >= 0.85."""
    scores = []
    
    for case in benchmark_dataset:
        score, is_grounded = self_rag_auditor.audit_groundedness(
            answer=case["expected_answer"],
            retrieved_contexts=[case["ground_truth_context"]]
        )
        scores.append(score)

    avg_faithfulness = sum(scores) / len(scores)
    print(f"\n[CI Quality Gate] Evaluated Average Faithfulness: {avg_faithfulness:.4f}")
    
    # SLA threshold from Section 8 of IMPLEMENTATION_PLAN_V02.md (CI failure threshold < 0.85)
    assert avg_faithfulness >= 0.85, f"Faithfulness dropped below target threshold: {avg_faithfulness}"

def test_hallucination_rejection():
    """Asserts that ungrounded statements are rejected by the Self-RAG auditor."""
    hallucinated_answer = "The CEO announced that all employees will receive free company yachts and vacation homes in Hawaii."
    context = ["Corporate Travel Policy Section 4.1: Domestic flights are reimbursed up to economy class limit of $500."]

    score, is_grounded = self_rag_auditor.audit_groundedness(
        answer=hallucinated_answer,
        retrieved_contexts=context
    )
    assert not is_grounded
    assert score < 0.50

