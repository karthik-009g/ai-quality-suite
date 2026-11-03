"""
Login Page Object
==================
Page object for the AskData login/authentication flow.

Note: The Vercel natural-language-postgres template may not have
a login page. This page object handles both authenticated and
unauthenticated scenarios gracefully.
"""

from playwright.sync_api import Page, expect


class LoginPage:
    """Page object for the login/authentication flow."""

    def __init__(self, page: Page):
        self.page = page
        self.url_pattern = "**/login*"

    @property
    def username_input(self):
        return self.page.locator("input[placeholder*='Email' i], input[type='email'], input[name='email'], input[placeholder*='Username' i]").first

    @property
    def password_input(self):
        return self.page.locator("input[type='password'], input[placeholder*='Password' i]").first

    @property
    def submit_button(self):
        return self.page.locator("button[type='submit'], button:has-text('Login'), button:has-text('Sign in')").first

    def is_login_required(self) -> bool:
        """Check if the app requires login."""
        try:
            return self.username_input.is_visible(timeout=2000) and self.password_input.is_visible(timeout=2000)
        except Exception:
            return False

    def login(self, username: str, password: str) -> None:
        """Perform login with provided credentials."""
        if not self.is_login_required():
            return  # No login needed

        self.username_input.fill(username)
        self.password_input.fill(password)
        self.submit_button.click()

        # Wait for navigation away from login page
        self.page.wait_for_load_state("networkidle")

    def assert_logged_in(self) -> None:
        """Verify we're past the login page."""
        # Should NOT be on a login URL anymore
        assert "login" not in self.page.url.lower(), (
            f"Still on login page: {self.page.url}"
        )
