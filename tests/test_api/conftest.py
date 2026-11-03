"""
API Test Fixtures
==================
Fixtures specific to API endpoint testing.
"""

import pytest

from askdata_quality.clients import AskDataClient


@pytest.fixture(scope="session")
def askdata_client(env_config):
    """AskData API client for test use."""
    return AskDataClient(
        base_url=env_config.askdata_base_url,
        timeout=min(env_config.test_timeout, 10),
        mock_mode=env_config.mock_mode,
    )


@pytest.fixture
def valid_query_payload():
    """A known-good query payload for positive tests."""
    return {
        "query": "Show me all products",
        "messages": [{"role": "user", "content": "Show me all products"}],
    }


@pytest.fixture
def valid_queries():
    """Set of valid natural language queries for parametrized tests."""
    return [
        "How many customers do we have?",
        "Show me the top 10 products by price",
        "What is the total revenue?",
        "List all orders from last month",
    ]
