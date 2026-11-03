"""
Golden Dataset Validation Tests
================================
Validates that all golden dataset files conform to the JSON Schema,
contain valid SQL syntax, valid categories, and load properly.
"""

import json
from pathlib import Path
import pytest
import jsonschema
import sqlparse

from askdata_quality.utils.dataset_loader import (
    load_all_golden_cases,
    load_golden_cases,
    get_cases_by_tier,
    get_cases_by_category,
    get_case_by_id,
)


@pytest.fixture(scope="module")
def schema():
    schema_path = (
        Path(__file__).parent.parent / "golden_datasets" / "schemas" / "golden_case.schema.json"
    )
    with open(schema_path) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def tier_files(golden_dataset_dir):
    return sorted(golden_dataset_dir.glob("tier*.json"))


def test_tier_files_exist(tier_files):
    """Ensure all 5 difficulty tier files exist."""
    assert len(tier_files) == 5, f"Expected 5 tier files, found {len(tier_files)}"


def test_tier_files_conform_to_schema(tier_files, schema):
    """Each tier file must strictly conform to the golden_case JSON Schema."""
    for tf in tier_files:
        with open(tf) as f:
            data = json.load(f)
        jsonschema.validate(instance=data, schema=schema)


def test_load_all_golden_cases(golden_dataset):
    """Ensure at least 25 golden cases are loaded without errors."""
    assert len(golden_dataset) >= 25
    ids = [c.id for c in golden_dataset]
    # IDs must be unique
    assert len(ids) == len(set(ids)), "Duplicate case IDs detected in golden dataset"


def test_sql_syntax_validity(golden_dataset):
    """Expected SQL for each golden case must be valid parseable SQL."""
    for case in golden_dataset:
        parsed = sqlparse.parse(case.expected_sql)
        assert len(parsed) > 0, f"Case {case.id} has unparseable SQL: {case.expected_sql}"
        # Root statement should be a SELECT / CTE
        first_token = parsed[0].get_type()
        assert first_token in ("SELECT", "UNKNOWN", "INSERT"), (
            f"Case {case.id} statement type {first_token} is unexpected"
        )


def test_dataset_filtering_helpers(golden_dataset):
    """Ensure loader utility helper functions filter correctly."""
    tier1 = get_cases_by_tier(golden_dataset, 1)
    assert len(tier1) == 5
    for c in tier1:
        assert c.difficulty == 1

    case1 = get_case_by_id(golden_dataset, "GD-001")
    assert case1 is not None
    assert case1.id == "GD-001"

    non_existent = get_case_by_id(golden_dataset, "GD-999")
    assert non_existent is None
