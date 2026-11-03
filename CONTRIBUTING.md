# Contributing to AskData Quality Suite

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -e ".[dev]"
   ```
3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```
4. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

## Running Tests

```bash
# Quick smoke tests
pytest -m smoke

# By layer
pytest -m api
pytest -m llm
pytest -m e2e
pytest -m safety

# All tests
pytest

# With coverage
pytest --cov=src/askdata_quality --cov-report=html
```

## Adding Golden Dataset Cases

1. Add cases to the appropriate tier file in `golden_datasets/v1/`
2. Follow the JSON Schema in `golden_datasets/schemas/golden_case.schema.json`
3. Use the ID format `GD-XXX` (sequential)
4. Include all required fields: `id`, `category`, `difficulty`, `natural_language`, `expected_sql`, `expected_columns`, `expected_row_count`

## Adding New Tests

- API tests → `tests/test_api/`
- LLM evaluation tests → `tests/test_llm/`
- E2E tests → `tests/test_e2e/`
- Safety tests → `tests/test_safety/`

Always use the appropriate markers:
```python
pytestmark = [pytest.mark.api]  # or llm, e2e, safety
```

## Code Style

- Use Ruff for linting: `ruff check .`
- Use Ruff for formatting: `ruff format .`
- Maximum line length: 100 characters
- Python 3.11+ features are encouraged
