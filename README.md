# 🧪 AskData Quality Suite

**Automated Testing & LLM Evaluation Framework for [AskData](https://ask-data-gilt.vercel.app/)**

[![CI](https://github.com/YOUR_USERNAME/askdata-quality-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/askdata-quality-suite/actions/workflows/ci.yml)
[![LLM Eval](https://github.com/YOUR_USERNAME/askdata-quality-suite/actions/workflows/llm-eval.yml/badge.svg)](https://github.com/YOUR_USERNAME/askdata-quality-suite/actions/workflows/llm-eval.yml)
[![E2E](https://github.com/YOUR_USERNAME/askdata-quality-suite/actions/workflows/e2e.yml/badge.svg)](https://github.com/YOUR_USERNAME/askdata-quality-suite/actions/workflows/e2e.yml)

> A production-grade AI quality framework that evaluates an NL-to-SQL application across **5 dimensions**: API correctness, LLM output quality, browser automation, AI safety, and CI/CD automation.

---

## 📊 Test Coverage At A Glance

| Layer | Tests | Technology | What It Validates |
|-------|-------|-----------|-------------------|
| 🔌 API | 26 | Pytest + HTTPX | Positive, negative, security endpoint tests |
| 🧠 LLM Eval | 16 | DeepEval + Groq Llama | Answer relevancy, SQL correctness, hallucination |
| 🎭 E2E | 11 | Playwright | Full browser user journeys |
| 🛡️ Safety | 30 | Pytest + Custom | Prompt injection, destructive SQL, data exfiltration |
| **Total** | **83** | | |

---

## 🏗️ Architecture

```
askdata-quality-suite/
├── src/askdata_quality/         # Reusable test infrastructure
│   ├── config.py                # Pydantic settings (env-driven)
│   ├── clients.py               # AskData API client wrapper
│   ├── groq_judge.py            # Free Groq LLM judge for DeepEval
│   └── utils/                   # SQL comparator, dataset loader, reporters
├── tests/
│   ├── test_api/                # API endpoint tests
│   ├── test_llm/                # LLM evaluation (DeepEval metrics)
│   ├── test_e2e/                # Playwright browser tests
│   └── test_safety/             # AI safety red-team tests
├── golden_datasets/v1/          # 25 versioned NL→SQL test cases
├── .github/workflows/           # 3 CI/CD pipelines
└── reports/                     # Generated evaluation reports
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/askdata-quality-suite.git
cd askdata-quality-suite
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
copy .env.example .env
# Edit .env with your values:
#   GROQ_API_KEY=gsk_...       (free at https://console.groq.com)
#   ASKDATA_BASE_URL=https://ask-data-gilt.vercel.app
```

### 3. Run Tests

```bash
# Run all tests (except slow LLM evals)
pytest -m "not slow"

# Run by layer
pytest -m api          # API tests only
pytest -m safety       # Safety tests only
pytest -m e2e          # Browser tests (requires: playwright install chromium)
pytest -m llm          # LLM evaluation (requires GROQ_API_KEY)

# Run everything
pytest
```

---

## 🧠 LLM Evaluation (DeepEval + Groq)

This framework uses **[DeepEval](https://github.com/confident-ai/deepeval)** with **Groq's free Llama-3.3-70b** as the LLM judge. No paid API keys required.

| Metric | Threshold | What It Measures |
|--------|-----------|------------------|
| Answer Relevancy | ≥ 0.70 | Is the response pertinent to the query? |
| Faithfulness | ≥ 0.80 | Is the answer grounded in schema context? |
| Hallucination | ≤ 0.50 | Does output contain fabricated tables/columns? |
| SQL Semantic Fidelity | ≥ 0.75 | Does the SQL capture the NL intent? (G-Eval) |
| Toxicity | ≤ 0.05 | Harmful content detection |

### Get Your Free Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (no credit card needed)
3. Create an API key
4. Add to `.env`: `GROQ_API_KEY=gsk_your_key`

---

## 🛡️ AI Safety Suite

**30 attack vectors** across 3 categories — all must be BLOCKED:

- **Prompt Injection** (15 tests): Direct override, role hijacking, delimiter escape, system prompt extraction
- **Destructive SQL** (10 tests): DROP, DELETE, TRUNCATE, ALTER, UPDATE, INSERT prevention
- **Data Exfiltration** (5 tests): Schema enumeration, UNION injection, timing attacks, stacked queries

---

## 📁 Golden Dataset

**25 NL→SQL test cases** across 5 difficulty tiers:

| Tier | Difficulty | Examples |
|------|-----------|----------|
| 1 | Simple SELECT | `Show me all products` |
| 2 | JOINs | `Orders with customer names` |
| 3 | Aggregation | `Revenue by category` |
| 4 | CTEs/Windows | `Running monthly total` |
| 5 | Ambiguous | `How are we doing this quarter?` |

Cases are versioned, JSON Schema validated, and loaded via parametrized fixtures.

---

## ⚙️ CI/CD Pipelines

| Workflow | Trigger | What It Does |
|----------|---------|-------------|
| `ci.yml` | Every PR | Lint → API tests → Safety tests (blocks merge on failure) |
| `llm-eval.yml` | Nightly cron | Full DeepEval evaluation → threshold gates → alerts |
| `e2e.yml` | PR to main | Playwright browser tests → trace artifacts on failure |

---

## 🛠️ Technology Stack

| Tool | Purpose |
|------|---------|
| **Pytest** | Test framework, fixtures, parametrization |
| **DeepEval** | LLM evaluation metrics (relevancy, faithfulness, hallucination, G-Eval) |
| **Groq** | Free LLM inference (Llama-3.3-70b-versatile) |
| **Playwright** | Browser automation for E2E tests |
| **HTTPX** | Async HTTP client for API tests |
| **Pydantic** | Configuration validation |
| **GitHub Actions** | CI/CD automation |
| **Ruff** | Linting & formatting |

---

## 📈 Reports

After running tests, reports are generated in `reports/`:

```bash
# Generate HTML report
pytest --html=reports/report.html --self-contained-html

# View Playwright traces (on failure)
playwright show-trace test-results/*/trace.zip
```

---

## 📝 License

MIT
