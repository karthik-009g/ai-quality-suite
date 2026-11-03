"""
Tests root conftest — imports and re-exports fixtures from the project root conftest.

This file ensures pytest discovers the root conftest.py fixtures
and adds the src/ directory to the Python path.
"""

import sys
from pathlib import Path

# Ensure src/ is on the path so `askdata_quality` package is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
