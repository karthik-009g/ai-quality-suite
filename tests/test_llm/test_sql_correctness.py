"""
SQL Correctness Tests
======================
Evaluates the structural and semantic correctness of SQL generated
by AskData against golden expected SQL statements.

Uses both:
- Custom SQL comparator (structural matching)
- DeepEval G-Eval (semantic fidelity)

Markers: @pytest.mark.llm
Test count: 5 (parametrized from golden dataset)
"""

import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase

from askdata_quality.utils.sql_comparator import compare_sql, normalize_sql

pytestmark = [pytest.mark.llm]


class TestSQLStructuralCorrectness:
    """
    Verify SQL structural correctness using the custom SQL comparator.

    This does NOT require an LLM judge — it's pure string/AST comparison.
    """

    @pytest.mark.parametrize(
        ("actual_sql", "expected_sql", "min_score"),
        [
            (
                "SELECT * FROM products",
                "SELECT * FROM products",
                1.0,
            ),
            (
                "select * from products where price > 50",
                "SELECT * FROM products WHERE price > 50",
                1.0,  # Should match after normalization
            ),
            (
                "SELECT name, price FROM products ORDER BY price DESC LIMIT 10",
                "SELECT * FROM products ORDER BY price DESC LIMIT 10",
                0.5,  # Partial match — different SELECT columns
            ),
            (
                "SELECT c.name, COUNT(o.id) AS order_count FROM customers c "
                "JOIN orders o ON c.id = o.customer_id GROUP BY c.name",
                "SELECT c.name, COUNT(o.id) AS order_count FROM customers c "
                "LEFT JOIN orders o ON c.id = o.customer_id GROUP BY c.name",
                0.7,  # Similar but different JOIN type
            ),
            (
                "SELECT category, SUM(price) FROM products GROUP BY category",
                "SELECT p.category, SUM(oi.quantity * oi.unit_price) AS total_revenue "
                "FROM order_items oi JOIN products p ON oi.product_id = p.id "
                "GROUP BY p.category",
                0.2,  # Structurally divergent but related intent
            ),
        ],
        ids=[
            "exact-match",
            "case-insensitive-match",
            "partial-select-match",
            "join-type-difference",
            "structural-divergence",
        ],
    )
    def test_sql_structural_comparison(
        self,
        actual_sql: str,
        expected_sql: str,
        min_score: float,
    ):
        """SQL comparator should score structural similarity correctly."""
        result = compare_sql(expected_sql, actual_sql)
        assert result.structural_score >= min_score, (
            f"Score {result.structural_score} < {min_score}. Details: {result.details}"
        )

    def test_normalization_consistency(self):
        """SQL normalization should be idempotent."""
        sql = "  SELECT   *   FROM   products  WHERE  price > 50  ;  "
        normalized = normalize_sql(sql)
        double_normalized = normalize_sql(normalized)
        assert normalized == double_normalized


class TestSQLSemanticFidelity:
    """
    Verify SQL semantic correctness using DeepEval G-Eval metric.

    Uses Groq Llama as the LLM judge to evaluate whether the
    generated SQL captures the user's intent.
    """

    @pytest.mark.slow
    @pytest.mark.parametrize(
        ("nl_query", "generated_sql", "expected_sql"),
        [
            (
                "Show me all products",
                "SELECT * FROM products",
                "SELECT * FROM products",
            ),
            (
                "What is the total revenue by category?",
                "SELECT category, SUM(price * quantity) AS revenue FROM products "
                "JOIN order_items ON products.id = order_items.product_id "
                "GROUP BY category",
                "SELECT p.category, SUM(oi.quantity * oi.unit_price) AS total_revenue "
                "FROM order_items oi JOIN products p ON oi.product_id = p.id "
                "GROUP BY p.category",
            ),
            (
                "Which customers spent the most?",
                "SELECT c.name, SUM(o.total) AS total_spent FROM customers c "
                "JOIN orders o ON c.id = o.customer_id "
                "GROUP BY c.name ORDER BY total_spent DESC LIMIT 10",
                "SELECT c.name, SUM(o.total) AS total_spent FROM customers c "
                "JOIN orders o ON c.id = o.customer_id "
                "GROUP BY c.name ORDER BY total_spent DESC",
            ),
        ],
        ids=[
            "exact-intent-match",
            "equivalent-aggregation",
            "similar-with-limit-difference",
        ],
    )
    def test_semantic_fidelity(
        self,
        nl_query: str,
        generated_sql: str,
        expected_sql: str,
        sql_fidelity_metric,
    ):
        """Generated SQL should semantically match the NL intent."""
        test_case = LLMTestCase(
            input=nl_query,
            actual_output=generated_sql,
            expected_output=expected_sql,
        )
        assert_test(test_case, [sql_fidelity_metric])
