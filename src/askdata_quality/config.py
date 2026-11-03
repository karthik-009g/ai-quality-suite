"""
Configuration Management
=========================
Pydantic Settings model that loads from .env file and environment variables.
All test modules access config through the `env_config` fixture.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # --- AskData Target ---
    askdata_base_url: str = Field(
        default="https://ask-data-gilt.vercel.app",
        description="Base URL of the AskData web application",
    )
    askdata_api_url: str = Field(
        default="https://ask-data-gilt.vercel.app",
        description="Base URL of the AskData API endpoints",
    )

    # --- Groq LLM Judge ---
    groq_api_key: str = Field(
        default="",
        description="Groq API key for LLM evaluation (free tier)",
    )
    groq_model_name: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model to use as DeepEval judge",
    )

    # --- E2E / Playwright ---
    askdata_username: str = Field(default="", description="Login username for E2E tests")
    askdata_password: str = Field(default="", description="Login password for E2E tests")
    playwright_browser: str = Field(default="chromium", description="Browser for Playwright")
    playwright_headed: bool = Field(default=False, description="Run browser in headed mode")

    # --- Test Behaviour ---
    test_timeout: int = Field(default=120, description="Default test timeout in seconds")
    log_level: str = Field(default="INFO", description="Logging level")
    ci: bool = Field(default=False, description="Running in CI environment")
    mock_mode: bool = Field(
        default=False,
        description="Use local mock backend for offline/deterministic CI testing",
    )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}
