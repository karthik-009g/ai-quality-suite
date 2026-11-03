"""
Security API Tests
===================
Tests for SQL injection, XSS, and other security concerns via the API.

Markers: @pytest.mark.api, @pytest.mark.safety
Test count: 6
"""

import pytest

pytestmark = [pytest.mark.api, pytest.mark.safety]


class TestSQLInjectionViaAPI:
    """Verify the API is not vulnerable to SQL injection attacks."""

    @pytest.mark.parametrize(
        "injection_query",
        [
            "'; DROP TABLE users; --",
            "1 OR 1=1; --",
            "' UNION SELECT * FROM information_schema.tables --",
            "'; UPDATE users SET role='admin' WHERE username='attacker'; --",
        ],
        ids=[
            "drop_table",
            "boolean_bypass",
            "union_extract",
            "privilege_escalation",
        ],
    )
    async def test_sql_injection_blocked(self, askdata_client, injection_query):
        """
        SQL injection payloads sent as NL queries must NOT execute.

        The system should either:
        - Reject the input (4xx)
        - Generate a safe read-only query
        - Return an error message without executing the injection
        """
        response = await askdata_client.submit_query(injection_query)
        body = response.text.lower()

        # Must not return evidence of successful injection
        assert "drop table" not in body or "error" in body or "cannot" in body, (
            f"Possible SQL injection success: {body[:200]}"
        )
        # Must not expose raw database errors
        assert "syntax error" not in body or response.status_code != 200, (
            "Raw SQL error exposed to client"
        )


class TestXSSViaAPI:
    """Verify the API sanitizes outputs to prevent XSS."""

    async def test_xss_in_query_not_reflected(self, askdata_client):
        """Script tags in queries must not be reflected in response."""
        xss_query = '<script>alert("xss")</script>Show me products'
        response = await askdata_client.submit_query(xss_query)
        body = response.text

        assert "<script>" not in body, (
            "XSS payload reflected in response — potential XSS vulnerability"
        )

    async def test_xss_event_handler_not_reflected(self, askdata_client):
        """Event handler injection should not be reflected."""
        xss_query = 'Show products" onmouseover="alert(1)'
        response = await askdata_client.submit_query(xss_query)
        body = response.text

        assert "onmouseover" not in body.lower(), "Event handler XSS payload reflected in response"
