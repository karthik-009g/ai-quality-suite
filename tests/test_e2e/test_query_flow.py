"""
E2E: Core Query Flow Tests
============================
End-to-end tests for the primary AskData user journey:
  Login → Ask NL Question → View SQL + Results

Markers: @pytest.mark.e2e
Test count: 6
"""

import pytest
from playwright.sync_api import Page, expect

from tests.test_e2e.pages.query_page import QueryPage
from tests.test_e2e.pages.results_page import ResultsPage


pytestmark = [pytest.mark.e2e]


class TestAppLoads:
    """Verify the AskData app loads correctly."""

    def test_app_loads_successfully(self, askdata_page: Page):
        """The app should load without errors."""
        # Page should have a title
        title = askdata_page.title()
        assert title, "Page has no title"

    def test_query_interface_visible(self, query_page: QueryPage):
        """The query input should be visible on load."""
        query_page.assert_query_interface_ready()

    def test_no_console_errors_on_load(self, askdata_page: Page):
        """The app should load without JavaScript console errors."""
        errors = []

        askdata_page.on("console", lambda msg: (
            errors.append(msg.text) if msg.type == "error" else None
        ))

        # Reload to capture console messages
        askdata_page.reload()
        askdata_page.wait_for_load_state("networkidle")

        # Filter out known benign errors (e.g., favicon 404)
        real_errors = [
            e for e in errors
            if "favicon" not in e.lower() and "404" not in e
        ]
        assert len(real_errors) == 0, (
            f"Console errors on load: {real_errors}"
        )


class TestQueryFlow:
    """Test the core query submission and results flow."""

    def test_submit_query_and_get_response(
        self, askdata_page: Page, askdata_base_url
    ):
        """User can type a query, submit it, and see a response."""
        query_page = QueryPage(askdata_page)
        results_page = ResultsPage(askdata_page)

        query_page.submit_query("How many products do we have?")

        # Wait for response
        results_page.wait_for_response(timeout=45000)

        # Should have some response content
        assert results_page.has_response(), (
            "No response appeared after submitting query"
        )

    def test_response_contains_no_raw_errors(
        self, askdata_page: Page, askdata_base_url
    ):
        """Response should not expose raw technical errors."""
        query_page = QueryPage(askdata_page)
        results_page = ResultsPage(askdata_page)

        query_page.submit_query("Show me all products")
        results_page.wait_for_response(timeout=45000)
        results_page.assert_no_raw_error()

    def test_response_no_destructive_sql(
        self, askdata_page: Page, askdata_base_url
    ):
        """Response should never show destructive SQL operations."""
        query_page = QueryPage(askdata_page)
        results_page = ResultsPage(askdata_page)

        query_page.submit_query("Show me the total number of orders")
        results_page.wait_for_response(timeout=45000)
        results_page.assert_no_destructive_sql_shown()
