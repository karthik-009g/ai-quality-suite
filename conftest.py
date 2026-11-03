"""
Root conftest.py — AskData Quality Suite
=========================================
Provides session-scoped fixtures shared across ALL test domains:
  - Environment configuration
  - API client (HTTPX async)
  - Groq LLM judge for DeepEval
  - Golden dataset loader
"""

from pathlib import Path

import httpx
import pytest

# ---------------------------------------------------------------------------
# Ensure .env is loaded before anything else
# ---------------------------------------------------------------------------
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Configuration fixture
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def env_config():
    """Load and validate environment configuration."""
    from askdata_quality.config import Settings

    return Settings()


# ---------------------------------------------------------------------------
# HTTPX async client for API tests
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def api_base_url(env_config):
    """Base URL for the AskData API."""
    return env_config.askdata_base_url


@pytest.fixture
async def api_client(api_base_url):
    """Async HTTPX client for API tests. Fresh per test for isolation."""
    async with httpx.AsyncClient(
        base_url=api_base_url,
        timeout=httpx.Timeout(30.0),
        follow_redirects=True,
    ) as client:
        yield client


# ---------------------------------------------------------------------------
# Groq LLM Judge for DeepEval
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def groq_judge(env_config):
    """Session-scoped Groq LLM judge for DeepEval metrics."""
    from askdata_quality.groq_judge import GroqJudge

    return GroqJudge(
        model_name=env_config.groq_model_name,
        api_key=env_config.groq_api_key,
    )


# ---------------------------------------------------------------------------
# Golden Dataset
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def golden_dataset_dir():
    """Path to golden dataset directory."""
    return Path(__file__).parent / "golden_datasets" / "v1"


@pytest.fixture(scope="session")
def golden_dataset(golden_dataset_dir):
    """Load all golden dataset cases from all tier files."""
    from askdata_quality.utils.dataset_loader import load_all_golden_cases

    return load_all_golden_cases(golden_dataset_dir)


# ---------------------------------------------------------------------------
# AskData app base URL for E2E
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def askdata_base_url(env_config):
    """Base URL for the AskData web app (E2E tests)."""
    return env_config.askdata_base_url
