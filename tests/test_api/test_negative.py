"""
Negative API Tests
===================
Tests that verify the AskData API handles invalid inputs gracefully.

Markers: @pytest.mark.api
Test count: 8
"""

import pytest

pytestmark = [pytest.mark.api]


# ---------------------------------------------------------------------------
# 1. Malformed Input
# ---------------------------------------------------------------------------
class TestMalformedInput:
    """Verify the API rejects or handles malformed requests."""

    @pytest.mark.xfail(
        reason="DEFECT-001: AskData Vercel route returns 500 on raw empty body instead of 400 Bad Request",
        strict=False,
    )
    async def test_empty_body(self, api_client):
        """An empty POST body should return 400 or 422, not 500."""
        response = await api_client.post("/api/chat", content=b"")
        assert response.status_code != 500, "Server returned 500 on empty body — should be 4xx"

    async def test_empty_query_string(self, askdata_client):
        """An empty query string should be handled gracefully."""
        response = await askdata_client.submit_query("")
        # Should not crash — either reject (4xx) or handle gracefully
        assert response.status_code != 500, "Server returned 500 on empty query"

    @pytest.mark.xfail(
        reason="DEFECT-002: AskData Vercel route returns 500 on invalid JSON instead of 400 Bad Request",
        strict=False,
    )
    async def test_invalid_json(self, api_client):
        """Malformed JSON should return a client error, not crash."""
        response = await api_client.post(
            "/api/chat",
            content=b"{{invalid json!!!",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code != 500, "Server returned 500 on invalid JSON"

    @pytest.mark.xfail(
        reason="DEFECT-003: AskData Vercel route returns 500 on non-JSON content-type instead of 415 Unsupported Media Type",
        strict=False,
    )
    async def test_wrong_content_type(self, api_client):
        """Sending non-JSON content type should be handled."""
        response = await api_client.post(
            "/api/chat",
            content=b"<xml>not json</xml>",
            headers={"Content-Type": "application/xml"},
        )
        assert response.status_code != 500, "Server returned 500 on wrong content type"


# ---------------------------------------------------------------------------
# 2. Boundary Conditions
# ---------------------------------------------------------------------------
class TestBoundaryConditions:
    """Test edge cases and boundary conditions."""

    async def test_extremely_long_query(self, askdata_client):
        """A very long query should be rejected or truncated, not crash."""
        long_query = "Show me all " + "products and " * 500 + "categories"
        response = await askdata_client.submit_query(long_query)
        # Should handle gracefully — 4xx or 200 with truncation
        assert response.status_code != 500, "Server returned 500 on extremely long query"

    async def test_special_characters_in_query(self, askdata_client):
        """Special characters should not break the API."""
        response = await askdata_client.submit_query(
            "Show products with names like 'O'Brien' & <special>"
        )
        assert response.status_code != 500, "Server returned 500 on special characters"

    async def test_unicode_query(self, askdata_client):
        """Unicode characters should be handled properly."""
        response = await askdata_client.submit_query("显示所有产品 — Zeige alle Produkte 🛍️")
        assert response.status_code != 500, "Server returned 500 on Unicode query"

    async def test_missing_messages_field(self, askdata_client):
        """Payload without 'messages' field should be handled."""
        response = await askdata_client.submit_query_raw(payload={"query": "Show me products"})
        assert response.status_code != 500, "Server returned 500 on missing messages field"
