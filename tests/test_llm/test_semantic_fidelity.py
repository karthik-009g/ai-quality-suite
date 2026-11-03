"""
Semantic Fidelity Tests (Custom G-Eval)
========================================
Uses a custom G-Eval metric to evaluate whether the generated SQL
faithfully captures the semantic intent of the NL query.

This goes beyond structural comparison — it uses an LLM judge to
reason about whether the SQL would actually answer the question.

Markers: @pytest.mark.llm, @pytest.mark.slow
Test count: 5
"""

import pytest

from deepeval import assert_test
from deepeval.test_case import LLMTestCase


pytestmark = [pytest.mark.llm, pytest.mark.slow]


class TestSemanticFidelitySimple:
    """Test semantic fidelity on straightforward queries."""

    @pytest.mark.parametrize("nl_query,sql_output", [
        (
            "Show me all products",
            "SELECT * FROM products",
        ),
        (
            "How many customers registered this year?",
            "SELECT COUNT(*) FROM customers WHERE created_at >= DATE_TRUNC('year', CURRENT_DATE)",
        ),
    ], ids=["select-all", "temporal-count"])
    def test_simple_fidelity(self, nl_query, sql_output, sql_fidelity_metric):
        """Simple NL→SQL should achieve high semantic fidelity."""
        test_case = LLMTestCase(
            input=nl_query,
            actual_output=sql_output,
            expected_output=sql_output,
        )
        assert_test(test_case, [sql_fidelity_metric])


class TestSemanticFidelityComplex:
    """Test semantic fidelity on complex, multi-step queries."""

    def test_aggregation_fidelity(self, sql_fidelity_metric):
        """Aggregation queries should capture grouping intent."""
        test_case = LLMTestCase(
            input="What is the average order value per month?",
            actual_output=(
                "SELECT DATE_TRUNC('month', order_date) AS month, "
                "AVG(total) AS avg_order_value "
                "FROM orders GROUP BY month ORDER BY month"
            ),
            expected_output=(
                "SELECT DATE_TRUNC('month', order_date) AS month, "
                "AVG(total) AS avg_order_value "
                "FROM orders GROUP BY DATE_TRUNC('month', order_date) ORDER BY month"
            ),
        )
        assert_test(test_case, [sql_fidelity_metric])

    def test_join_intent_fidelity(self, sql_fidelity_metric):
        """Multi-table queries should correctly resolve relationships."""
        test_case = LLMTestCase(
            input="Show me customers who bought electronics",
            actual_output=(
                "SELECT DISTINCT c.name FROM customers c "
                "INNER JOIN orders o ON c.id = o.customer_id "
                "INNER JOIN order_items oi ON o.id = oi.order_id "
                "INNER JOIN products p ON oi.product_id = p.id "
                "WHERE p.category = 'Electronics'"
            ),
            expected_output=(
                "SELECT DISTINCT c.name FROM customers c "
                "JOIN orders o ON c.id = o.customer_id "
                "JOIN order_items oi ON o.id = oi.order_id "
                "JOIN products p ON oi.product_id = p.id "
                "WHERE p.category = 'Electronics'"
            ),
        )
        assert_test(test_case, [sql_fidelity_metric])

    def test_ambiguous_intent_handling(self, sql_fidelity_metric):
        """Ambiguous queries should still produce semantically valid SQL."""
        test_case = LLMTestCase(
            input="How are we doing?",
            actual_output=(
                "SELECT DATE_TRUNC('month', order_date) AS month, "
                "COUNT(*) AS order_count, SUM(total) AS revenue "
                "FROM orders "
                "WHERE order_date >= CURRENT_DATE - INTERVAL '3 months' "
                "GROUP BY month ORDER BY month"
            ),
            expected_output=(
                "SELECT DATE_TRUNC('month', order_date) AS month, "
                "COUNT(*) AS order_count, SUM(total) AS revenue "
                "FROM orders "
                "WHERE order_date >= DATE_TRUNC('quarter', CURRENT_DATE) "
                "GROUP BY DATE_TRUNC('month', order_date) ORDER BY month"
            ),
        )
        assert_test(test_case, [sql_fidelity_metric])
