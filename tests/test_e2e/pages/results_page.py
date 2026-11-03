"""
Results Page Object
====================
Page object for the AskData results display.

Handles SQL output, data tables, charts, and error messages.
"""

from playwright.sync_api import Page


class ResultsPage:
    """Page object for AskData query results display."""

    def __init__(self, page: Page):
        self.page = page

    def wait_for_response(self, timeout: int = 30000) -> None:
        """Wait for the query response to appear."""
        # Wait for any response content to appear
        self.page.wait_for_selector(
            "[data-testid*='result'], [data-testid*='message'], "
            ".prose, pre, code, table, [role='table'], "
            "[class*='response'], [class*='result'], [class*='message']",
            timeout=timeout,
        )

    @property
    def sql_output(self):
        """The displayed SQL query in the response."""
        return self.page.locator("pre, code, [class*='sql'], [data-testid*='sql']")

    @property
    def data_table(self):
        """The data results table."""
        return self.page.locator("table, [role='table'], [class*='table']")

    @property
    def error_message(self):
        """Any error message displayed."""
        return self.page.locator("[class*='error'], [role='alert'], [data-testid*='error']")

    @property
    def response_content(self):
        """General response content area."""
        return self.page.locator(
            "[data-testid*='message'], [class*='response'], "
            "[class*='message'], .prose, [class*='assistant']"
        )

    def has_sql_output(self) -> bool:
        """Check if SQL output is visible."""
        try:
            return self.sql_output.first.is_visible(timeout=5000)
        except Exception:
            return False

    def has_data_table(self) -> bool:
        """Check if a data table is visible."""
        try:
            return self.data_table.first.is_visible(timeout=5000)
        except Exception:
            return False

    def has_error(self) -> bool:
        """Check if an error message is visible."""
        try:
            return self.error_message.first.is_visible(timeout=3000)
        except Exception:
            return False

    def has_response(self) -> bool:
        """Check if any response content is visible."""
        try:
            return self.response_content.first.is_visible(timeout=5000)
        except Exception:
            return False

    def get_response_text(self) -> str:
        """Get the text content of the response."""
        try:
            return self.response_content.first.inner_text(timeout=5000)
        except Exception:
            return ""

    def assert_no_raw_error(self) -> None:
        """Verify no raw SQL errors or stack traces are exposed."""
        response_text = self.get_response_text().lower()
        dangerous_patterns = [
            "traceback",
            "stack trace",
            "internal server error",
            "psycopg2",
            "sqlalchemy",
            "connection refused",
            "permission denied",
        ]
        for pattern in dangerous_patterns:
            assert pattern not in response_text, f"Raw error exposed in UI: found '{pattern}'"

    def assert_no_destructive_sql_shown(self) -> None:
        """Verify no destructive SQL operations are shown to user."""
        response_text = self.get_response_text().lower()
        destructive_keywords = ["drop table", "delete from", "truncate", "alter table"]
        for keyword in destructive_keywords:
            assert keyword not in response_text, f"Destructive SQL shown in UI: '{keyword}'"
