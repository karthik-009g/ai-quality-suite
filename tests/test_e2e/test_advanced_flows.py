"""
E2E: Advanced Flow Tests
==========================
Tests for advanced user workflows: error handling, edge cases,
responsive layout, and multi-query scenarios.

Markers: @pytest.mark.e2e
Test count: 5
"""

import pytest
from playwright.sync_api import Page

from tests.test_e2e.pages.query_page import QueryPage
from tests.test_e2e.pages.results_page import ResultsPage


pytestmark = [pytest.mark.e2e]


class TestErrorHandling:
    """Verify the app handles edge cases gracefully in the UI."""

    def test_nonsensical_query_handled(self, askdata_page: Page):
        """A nonsensical query should produce a user-friendly response."""
        query_page = QueryPage(askdata_page)
        results_page = ResultsPage(askdata_page)

        query_page.submit_query("asdfghjkl zxcvbnm qwerty")

        # Should still get a response (even if it's "I don't understand")
        results_page.wait_for_response(timeout=45000)
        results_page.assert_no_raw_error()

    def test_special_characters_in_query(self, askdata_page: Page):
        """Special characters should not crash the UI."""
        query_page = QueryPage(askdata_page)
        results_page = ResultsPage(askdata_page)

        query_page.submit_query("Products with name like 'O'Brien' & <tag>")

        results_page.wait_for_response(timeout=45000)
        results_page.assert_no_raw_error()


class TestResponsiveLayout:
    """Verify the app works across different viewport sizes."""

    @pytest.mark.parametrize("width,height,label", [
        (375, 667, "mobile"),
        (768, 1024, "tablet"),
        (1920, 1080, "desktop"),
    ], ids=["mobile", "tablet", "desktop"])
    def test_app_renders_at_viewport(
        self, page: Page, askdata_base_url, width, height, label
    ):
        """The app should render without errors at different viewport sizes."""
        page.set_viewport_size({"width": width, "height": height})
        page.goto(askdata_base_url)
        page.wait_for_load_state("networkidle")

        query_page = QueryPage(page)

        # Query input should be visible at any viewport
        assert query_page.is_input_visible(), (
            f"Query input not visible at {label} viewport ({width}x{height})"
        )


class TestMultiQuerySession:
    """Test submitting multiple queries in a single session."""

    def test_sequential_queries(self, askdata_page: Page):
        """Multiple sequential queries should all produce responses."""
        query_page = QueryPage(askdata_page)
        results_page = ResultsPage(askdata_page)

        queries = [
            "How many products do we have?",
            "What is the total revenue?",
        ]

        for query in queries:
            query_page.submit_query(query)
            results_page.wait_for_response(timeout=45000)

            assert results_page.has_response(), (
                f"No response for query: {query}"
            )
            results_page.assert_no_raw_error()
