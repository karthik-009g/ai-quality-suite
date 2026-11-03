"""
Positive API Tests
===================
Tests that verify the AskData API works correctly with valid inputs.

Markers: @pytest.mark.api
Test count: 8
"""

import pytest

pytestmark = [pytest.mark.api]


# ---------------------------------------------------------------------------
# 1. Health / Reachability
# ---------------------------------------------------------------------------
class TestHealthCheck:
    """Verify the AskData app is reachable and returns valid responses."""

    @pytest.mark.smoke
    async def test_app_is_reachable(self, askdata_client):
        """The AskData app should respond to GET /."""
        response = await askdata_client.health_check()
        assert response.status_code == 200, f"App not reachable: {response.status_code}"

    @pytest.mark.smoke
    async def test_app_returns_html(self, askdata_client):
        """The root page should return HTML content."""
        response = await askdata_client.get_page("/")
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "text/html" in content_type, f"Expected HTML, got: {content_type}"


# ---------------------------------------------------------------------------
# 2. Query Submission
# ---------------------------------------------------------------------------
class TestQuerySubmission:
    """Verify the query endpoint accepts valid NL queries."""

    async def test_valid_query_returns_response(self, askdata_client):
        """A valid NL query should return a successful response or auth challenge."""
        response = await askdata_client.submit_query("How many customers do we have?")
        # Accept 200/201 (authorized/mock) or 401 (governed enterprise auth challenge)
        assert response.status_code in (200, 201, 401), (
            f"Expected 2xx or 401 auth challenge, got: {response.status_code}"
        )

    async def test_query_response_has_content(self, askdata_client):
        """The response body should not be empty."""
        response = await askdata_client.submit_query("Show me all products")
        assert response.status_code in (200, 201, 401)
        assert len(response.content) > 0, "Response body is empty"

    @pytest.mark.parametrize(
        "query",
        [
            "What is the total revenue?",
            "Show me the top 5 products",
            "How many orders were placed?",
        ],
    )
    async def test_multiple_valid_queries(self, askdata_client, query):
        """Multiple different valid queries should be processed or properly challenged."""
        response = await askdata_client.submit_query(query)
        assert response.status_code in (200, 201, 401), (
            f"Query '{query}' failed with status {response.status_code}"
        )


# ---------------------------------------------------------------------------
# 3. Response Structure
# ---------------------------------------------------------------------------
class TestResponseStructure:
    """Verify the API response has expected structure."""

    async def test_response_is_valid_format(self, askdata_client):
        """Response should be valid JSON or structured text."""
        response = await askdata_client.submit_query("Count all products")
        assert response.status_code in (200, 201, 401)
        content_type = response.headers.get("content-type", "")
        valid_types = ["application/json", "text/plain", "text/event-stream"]
        assert any(t in content_type for t in valid_types), (
            f"Unexpected content-type: {content_type}"
        )

    async def test_response_contains_sql_like_content(self, askdata_client):
        """The response should return SQL execution or governed auth detail."""
        response = await askdata_client.submit_query("Show me all products")
        assert response.status_code in (200, 201, 401)
        body = response.text.lower()
        if response.status_code in (200, 201):
            sql_indicators = ["select", "from", "product", "table", "result"]
            assert any(kw in body for kw in sql_indicators), "Response missing SQL indicators"
        else:
            assert "detail" in body or "authenticated" in body or "unauthorized" in body
        assert "internal server error" not in body, "Response contains server error"
