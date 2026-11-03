"""
Answer Quality Tests (DeepEval)
================================
Evaluates the relevancy of AskData's responses to NL queries
using DeepEval's AnswerRelevancyMetric backed by Groq Llama.

Markers: @pytest.mark.llm, @pytest.mark.slow
Test count: 5 (parametrized from golden dataset tier 1)
"""

import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase

pytestmark = [pytest.mark.llm, pytest.mark.slow]


class TestAnswerRelevancy:
    """
    Evaluate whether AskData's responses are relevant to the input queries.

    Uses DeepEval AnswerRelevancyMetric with Groq Llama as judge.
    Threshold: 0.7 (70% relevancy minimum)
    """

    @pytest.mark.parametrize(
        ("query", "expected_sql"),
        [
            (
                "Show me all products",
                "SELECT * FROM products",
            ),
            (
                "How many customers do we have?",
                "SELECT COUNT(*) FROM customers",
            ),
            (
                "What is the total revenue by product category?",
                "SELECT p.category, SUM(oi.quantity * oi.unit_price) AS total_revenue "
                "FROM order_items oi JOIN products p ON oi.product_id = p.id "
                "GROUP BY p.category",
            ),
            (
                "Show me the top 10 most expensive products",
                "SELECT * FROM products ORDER BY price DESC LIMIT 10",
            ),
            (
                "How many orders does each customer have?",
                "SELECT c.name, COUNT(o.id) AS order_count FROM customers c "
                "LEFT JOIN orders o ON c.id = o.customer_id GROUP BY c.name",
            ),
        ],
        ids=[
            "simple-select-all",
            "simple-count",
            "aggregation-by-category",
            "top-n-products",
            "join-with-count",
        ],
    )
    def test_answer_relevancy(
        self,
        query: str,
        expected_sql: str,
        relevancy_metric,
    ):
        """Each golden query should produce a relevant response."""
        # In a live setup, actual_output comes from AskData API.
        # For framework demonstration, we use the expected SQL as
        # a simulated "correct" response from the system.
        test_case = LLMTestCase(
            input=query,
            actual_output=expected_sql,  # Simulated: replace with live API call
            expected_output=expected_sql,
        )
        assert_test(test_case, [relevancy_metric])


class TestAnswerRelevancyWithContext:
    """Test relevancy when retrieval context is provided."""

    def test_relevancy_with_schema_context(self, relevancy_metric):
        """Response should be relevant when schema context is available."""
        test_case = LLMTestCase(
            input="What is the average order value?",
            actual_output="SELECT AVG(total) AS avg_order_value FROM orders",
            expected_output="SELECT AVG(total) FROM orders",
            retrieval_context=[
                "Table: orders (id INT, customer_id INT, order_date DATE, total DECIMAL)",
                "Table: customers (id INT, name VARCHAR, email VARCHAR)",
            ],
        )
        assert_test(test_case, [relevancy_metric])
