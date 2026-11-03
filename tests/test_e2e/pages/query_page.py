"""
Query Page Object
==================
Page object for the main AskData query interface.

Encapsulates interactions with the natural language input,
submit button, and suggestion chips.
"""

from playwright.sync_api import Page


class QueryPage:
    """Page object for the AskData query input interface."""

    def __init__(self, page: Page):
        self.page = page

    @property
    def query_input(self):
        """The main NL query input field."""
        # Try multiple selectors — Vercel AI SDK apps vary
        selectors = [
            self.page.get_by_placeholder("Ask a question"),
            self.page.get_by_placeholder("Send a message"),
            self.page.get_by_placeholder("Type your question"),
            self.page.get_by_role("textbox"),
            self.page.locator("textarea"),
            self.page.locator("input[type='text']"),
        ]
        for selector in selectors:
            if selector.first.is_visible(timeout=3000):
                return selector.first
        # Fallback to first textbox/textarea
        return self.page.locator("textarea, input[type='text']").first

    @property
    def submit_button(self):
        """The query submit button."""
        selectors = [
            self.page.get_by_role("button", name="Send"),
            self.page.get_by_role("button", name="Submit"),
            self.page.get_by_role("button", name="Ask"),
            self.page.locator("button[type='submit']"),
        ]
        for selector in selectors:
            try:
                if selector.first.is_visible(timeout=2000):
                    return selector.first
            except Exception:
                continue
        return self.page.locator("button[type='submit']").first

    def type_query(self, query: str) -> None:
        """Type a natural language query into the input field."""
        input_field = self.query_input
        input_field.click()
        input_field.fill(query)

    def submit_query(self, query: str) -> None:
        """Type and submit a natural language query."""
        self.type_query(query)

        # Try submit button first, fall back to Enter key
        try:
            btn = self.submit_button
            if btn.is_visible(timeout=2000):
                btn.click()
                return
        except Exception:
            pass

        # Fallback: press Enter
        self.query_input.press("Enter")

    def is_input_visible(self) -> bool:
        """Check if the query input is visible."""
        try:
            return self.query_input.is_visible(timeout=5000)
        except Exception:
            return False

    def has_suggestion_chips(self) -> bool:
        """Check if the UI shows query suggestion chips."""
        try:
            chips = self.page.locator("[data-testid*='suggestion'], button:has-text('Show me')")
            return chips.count() > 0
        except Exception:
            return False

    def click_suggestion(self, index: int = 0) -> None:
        """Click a query suggestion chip."""
        chips = self.page.locator("[data-testid*='suggestion'], button:has-text('Show me')")
        if chips.count() > index:
            chips.nth(index).click()

    def assert_query_interface_ready(self) -> None:
        """Verify the query interface is loaded and ready."""
        assert self.is_input_visible(), "Query input is not visible"
