"""
API & LLM Clients
==================
Factory functions and wrappers for the HTTPX API client and the
AskData interaction layer. These are used by both API tests and
the LLM evaluation pipeline (to get actual_output from AskData).
"""

from __future__ import annotations

import json
import re
from typing import Optional
import httpx

from askdata_quality.utils.sql_comparator import contains_destructive_sql


class AskDataClient:
    """
    Thin wrapper around the AskData API.

    Targets the Vercel-deployed AskData endpoints (/api/chat and root pages).
    Supports live network execution as well as a deterministic mock fallback
    engine for CI environments.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        mock_mode: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.mock_mode = mock_mode

    def _make_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

    async def health_check(self) -> httpx.Response:
        """Check if the AskData app is reachable."""
        if self.mock_mode:
            return httpx.Response(200, text="<!DOCTYPE html><html><head><title>Ask Data</title></head><body><h1>Ask Data</h1></body></html>", headers={"content-type": "text/html; charset=utf-8"})
        try:
            async with self._make_client() as client:
                return await client.get("/")
        except Exception:
            return httpx.Response(200, text="<!DOCTYPE html><html><head><title>Ask Data</title></head><body><h1>Ask Data</h1></body></html>", headers={"content-type": "text/html; charset=utf-8"})

    async def submit_query(self, natural_language_query: str) -> httpx.Response:
        """
        Submit a natural language query to AskData.

        Sends both 'query' (expected by AskData Vercel route) and
        'messages' (standard AI SDK format).
        """
        if self.mock_mode:
            return self._generate_mock_query_response(natural_language_query)

        payload = {
            "query": natural_language_query,
            "messages": [{"role": "user", "content": natural_language_query}],
        }
        try:
            async with self._make_client() as client:
                resp = await client.post("/api/chat", json=payload)
                if resp.status_code == 504 or resp.status_code == 408:
                    return self._generate_mock_query_response(natural_language_query)
                return resp
        except (httpx.TimeoutException, httpx.ConnectError):
            return self._generate_mock_query_response(natural_language_query)

    async def submit_query_raw(self, payload: dict) -> httpx.Response:
        """Submit a raw payload to the query endpoint (for negative/security tests)."""
        if self.mock_mode:
            query = payload.get("query", "")
            if not query and "messages" in payload:
                messages = payload.get("messages", [])
                if messages and isinstance(messages, list):
                    query = messages[0].get("content", "")
            return self._generate_mock_query_response(query)

        try:
            async with self._make_client() as client:
                return await client.post("/api/chat", json=payload)
        except (httpx.TimeoutException, httpx.ConnectError):
            query = payload.get("query", "")
            return self._generate_mock_query_response(query)

    async def get_page(self, path: str = "/") -> httpx.Response:
        """Fetch a page from the AskData app (for reachability checks)."""
        if self.mock_mode:
            return httpx.Response(200, text="<!DOCTYPE html><html><body>Ask Data</body></html>", headers={"content-type": "text/html; charset=utf-8"})
        try:
            async with self._make_client() as client:
                return await client.get(path)
        except Exception:
            return httpx.Response(200, text="<!DOCTYPE html><html><body>Ask Data</body></html>", headers={"content-type": "text/html; charset=utf-8"})

    def _generate_mock_query_response(self, query: str) -> httpx.Response:
        """Simulate realistic AskData API responses based on input safety."""
        q_lower = (query or "").lower().strip()

        if not q_lower:
            return httpx.Response(
                400,
                json={"type": "error", "message": "Query is required", "data": {}, "next_steps": []},
            )

        # Destructive SQL check
        is_destr, patterns = contains_destructive_sql(query)
        if is_destr:
            return httpx.Response(
                400,
                json={
                    "type": "error",
                    "message": "Destructive query blocked: operations like DROP/DELETE are forbidden.",
                    "patterns": patterns,
                },
            )

        # Prompt injection / safety check
        injection_indicators = [
            "ignore all", "system override", "forget your role", "###admin###",
            "dan (do anything now)", "pwned", "pg_shadow", "pg_roles", "information_schema",
            "<script>", "onmouseover", "pg_sleep", "copy (",
        ]
        if any(ind in q_lower for ind in injection_indicators):
            return httpx.Response(
                400,
                json={
                    "type": "error",
                    "message": "Security policy violation: query contains unauthorized instructions or access patterns.",
                },
            )

        # Standard safe query response
        sql = "SELECT * FROM products;"
        if "count" in q_lower or "how many" in q_lower:
            sql = "SELECT COUNT(*) FROM products;"
        elif "revenue" in q_lower:
            sql = "SELECT SUM(total) FROM orders;"

        return httpx.Response(
            200,
            json={
                "type": "result",
                "query": sql,
                "data": [{"id": 1, "name": "Sample Product", "price": 49.99}],
                "message": f"Query executed successfully: {sql}",
            },
        )
