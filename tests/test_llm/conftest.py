"""
LLM Evaluation Test Fixtures
==============================
Fixtures for DeepEval LLM evaluation tests.
Provides pre-configured metrics, golden test case conversion,
and the Groq judge instance.
"""

import pytest

from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric,
    ToxicityMetric,
    GEval,
)
try:
    from deepeval.test_case import LLMTestCase, SingleTurnParams as LLMParams
except ImportError:
    from deepeval.test_case import LLMTestCase, LLMTestCaseParams as LLMParams


@pytest.fixture(scope="session")
def relevancy_metric(groq_judge):
    """Answer relevancy metric with Groq judge."""
    return AnswerRelevancyMetric(
        model=groq_judge,
        threshold=0.7,
        include_reason=True,
    )


@pytest.fixture(scope="session")
def faithfulness_metric(groq_judge):
    """Faithfulness metric — checks if output is grounded in context."""
    return FaithfulnessMetric(
        model=groq_judge,
        threshold=0.8,
        include_reason=True,
    )


@pytest.fixture(scope="session")
def hallucination_metric(groq_judge):
    """Hallucination metric — detects fabricated information."""
    return HallucinationMetric(
        model=groq_judge,
        threshold=0.5,  # Score > 0.5 means hallucination detected → fail
        include_reason=True,
    )


@pytest.fixture(scope="session")
def toxicity_metric(groq_judge):
    """Toxicity metric — detects harmful content."""
    return ToxicityMetric(
        model=groq_judge,
        threshold=0.5,
        include_reason=True,
    )


@pytest.fixture(scope="session")
def sql_fidelity_metric(groq_judge):
    """
    Custom G-Eval metric for NL→SQL semantic fidelity.

    Evaluates whether the generated SQL correctly captures the
    intent expressed in the natural language query.
    """
    return GEval(
        name="SQL Semantic Fidelity",
        model=groq_judge,
        evaluation_steps=[
            "Analyze the natural language query to understand the user's intent",
            "Examine the generated SQL query for structural correctness",
            "Check if the SQL query targets the correct tables and columns",
            "Verify that WHERE/HAVING clauses match the filtering intent",
            "Verify that aggregation functions match the requested metrics",
            "Check if ORDER BY and LIMIT match the sorting/ranking intent",
            "Assess whether the SQL would produce results answering the NL query",
        ],
        evaluation_params=[
            LLMParams.INPUT,
            LLMParams.ACTUAL_OUTPUT,
            LLMParams.EXPECTED_OUTPUT,
        ],
        threshold=0.75,
    )


def golden_case_to_llm_test_case(
    golden_case,
    actual_output: str,
    retrieval_context: list[str] | None = None,
) -> LLMTestCase:
    """
    Convert a GoldenCase + actual output into a DeepEval LLMTestCase.

    Args:
        golden_case: A GoldenCase from the golden dataset
        actual_output: The actual SQL/response from AskData
        retrieval_context: Optional context used by the LLM

    Returns:
        LLMTestCase ready for metric evaluation
    """
    return LLMTestCase(
        input=golden_case.natural_language,
        actual_output=actual_output,
        expected_output=golden_case.expected_sql,
        retrieval_context=retrieval_context or [],
        context=[
            f"Expected columns: {golden_case.expected_columns}",
            f"Category: {golden_case.category}",
            f"Difficulty: {golden_case.difficulty}/5",
        ],
    )
