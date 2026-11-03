"""
Golden Dataset Loader
======================
Loads, validates, and provides golden NL→SQL test cases from
versioned JSON files. Used by both LLM evaluation and API tests.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class GoldenCase:
    """A single NL→SQL golden test case."""

    id: str
    category: str
    difficulty: int
    natural_language: str
    expected_sql: str
    expected_columns: list[str]
    expected_row_count: dict[str, int]
    tags: list[str] = field(default_factory=list)
    edge_case: bool = False
    description: str = ""
    version: str = "1.0.0"

    @property
    def pytest_id(self) -> str:
        """Generate a readable pytest parametrize ID."""
        return f"{self.id}-{self.category}-tier{self.difficulty}"


def load_golden_cases(file_path: Path) -> list[GoldenCase]:
    """Load golden cases from a single JSON file."""
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    cases = []
    for case_data in data.get("cases", []):
        cases.append(GoldenCase(**case_data))
    return cases


def load_all_golden_cases(dataset_dir: Path) -> list[GoldenCase]:
    """
    Load all golden cases from all tier files in a directory.

    Scans for all .json files matching tier*.json pattern,
    loads them in order, and returns a flat list.
    """
    all_cases: list[GoldenCase] = []
    tier_files = sorted(dataset_dir.glob("tier*.json"))

    for tier_file in tier_files:
        cases = load_golden_cases(tier_file)
        all_cases.extend(cases)

    return all_cases


def get_cases_by_tier(cases: list[GoldenCase], tier: int) -> list[GoldenCase]:
    """Filter cases by difficulty tier."""
    return [c for c in cases if c.difficulty == tier]


def get_cases_by_category(cases: list[GoldenCase], category: str) -> list[GoldenCase]:
    """Filter cases by category."""
    return [c for c in cases if c.category == category]


def get_case_by_id(cases: list[GoldenCase], case_id: str) -> GoldenCase | None:
    """Find a specific case by ID."""
    for c in cases:
        if c.id == case_id:
            return c
    return None
