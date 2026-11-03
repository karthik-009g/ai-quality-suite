"""
E2E Test Fixtures (Playwright)
================================
Provides browser context, authenticated pages, and page objects
for end-to-end testing of the AskData web application.
"""

import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, env_config):
    """Override default browser context with custom settings."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture
def askdata_page(page: Page, askdata_base_url) -> Page:
    """Navigate to AskData and return the page object."""
    page.goto(askdata_base_url)
    # Wait for the app to be interactive
    page.wait_for_load_state("networkidle")
    return page


@pytest.fixture
def query_page(askdata_page):
    """Return a QueryPage object for the main query interface."""
    from tests.test_e2e.pages.query_page import QueryPage

    return QueryPage(askdata_page)


@pytest.fixture
def results_page(askdata_page):
    """Return a ResultsPage object for viewing query results."""
    from tests.test_e2e.pages.results_page import ResultsPage

    return ResultsPage(askdata_page)
