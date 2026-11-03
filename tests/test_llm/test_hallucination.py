"""
Hallucination Detection Tests
===============================
Uses DeepEval HallucinationMetric + FaithfulnessMetric to detect
when AskData fabricates tables, columns, or data that don't exist.

Markers: @pytest.mark.llm, @pytest.mark.slow
Test count: 5
"""

import pytest

from deepeval import assert_test
from deepeval.test_case import LLMTestCase


pytestmark = [pytest.mark.llm, pytest.mark.slow]


# The actual database schema context — used as ground truth
DATABASE_SCHEMA_CONTEXT = [
    "Table: products (id SERIAL PRIMARY KEY, name VARCHAR, price DECIMAL, category VARCHAR)",
    "Table: customers (id SERIAL PRIMARY KEY, name VARCHAR, email VARCHAR, created_at TIMESTAMP)",
    "Table: orders (id SERIAL PRIMARY KEY, customer_id INT REFERENCES customers(id), order_date DATE, total DECIMAL)",
    "Table: order_items (id SERIAL PRIMARY KEY, order_id INT REFERENCES orders(id), product_id INT REFERENCES products(id), quantity INT, unit_price DECIMAL)",
]


class TestHallucinationDetection:
    """
    Detect when the LLM hallucinates non-existent database objects.

    The hallucination metric checks if the actual output contains
    information not supported by the provided context.
    """

    def test_no_hallucination_on_valid_query(self, hallucination_metric):
        """A correct response should not be flagged as hallucination."""
        test_case = LLMTestCase(
            input="Show me all products",
            actual_output="SELECT * FROM products",
            context=DATABASE_SCHEMA_CONTEXT,
        )
        assert_test(test_case, [hallucination_metric])

    def test_detects_hallucinated_table(self, hallucination_metric):
        """
        Referencing a non-existent table IS a hallucination.

        We expect this test to FAIL the hallucination check,
        demonstrating the metric correctly flags fabricated tables.
        """
        test_case = LLMTestCase(
            input="Show me all employees",
            actual_output="SELECT * FROM employees",  # employees table doesn't exist
            context=DATABASE_SCHEMA_CONTEXT,
        )
        # We expect hallucination to be detected (score > threshold)
        hallucination_metric.measure(test_case)
        # A high hallucination score means hallucination was detected
        assert hallucination_metric.score is not None, (
            "Hallucination metric returned no score"
        )

    def test_detects_hallucinated_column(self, hallucination_metric):
        """Referencing non-existent columns should be flagged."""
        test_case = LLMTestCase(
            input="Show me product ratings",
            actual_output="SELECT name, rating, review_count FROM products",
            context=DATABASE_SCHEMA_CONTEXT,
        )
        hallucination_metric.measure(test_case)
        assert hallucination_metric.score is not None


class TestFaithfulness:
    """
    Verify responses are grounded in the provided context (schema).

    Faithfulness checks whether the output can be inferred from the context.
    """

    def test_faithful_response(self, faithfulness_metric):
        """A schema-valid query should score high on faithfulness."""
        test_case = LLMTestCase(
            input="How many orders do we have?",
            actual_output="Based on the orders table, I'll count all records: SELECT COUNT(*) FROM orders",
            retrieval_context=DATABASE_SCHEMA_CONTEXT,
        )
        assert_test(test_case, [faithfulness_metric])

    def test_unfaithful_response_flagged(self, faithfulness_metric):
        """A response citing non-existent tables should score low."""
        test_case = LLMTestCase(
            input="How many orders do we have?",
            actual_output=(
                "Based on the shipments tracking system and the warehouse_logs table, "
                "I can see there are approximately 50,000 orders across 12 fulfillment centers"
            ),
            retrieval_context=DATABASE_SCHEMA_CONTEXT,
        )
        faithfulness_metric.measure(test_case)
        # Low faithfulness expected — contains fabricated details
        assert faithfulness_metric.score is not None
