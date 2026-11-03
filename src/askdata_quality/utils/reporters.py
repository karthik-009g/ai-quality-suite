"""
Report Generator
==================
Generates structured evaluation reports in multiple formats:
- Console (rich tables)
- JSON (machine-readable)
- HTML (human-readable, suitable for CI artifacts)
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class TestResult:
    """A single test result entry."""

    test_id: str
    test_name: str
    category: str  # api, llm, e2e, safety
    status: str  # passed, failed, skipped, error
    duration_ms: float = 0.0
    score: float | None = None  # For LLM metrics
    threshold: float | None = None
    details: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationReport:
    """Aggregate evaluation report."""

    suite_name: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    pass_rate: float = 0.0
    results: list[TestResult] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_result(self, result: TestResult) -> None:
        """Add a test result and update counters."""
        self.results.append(result)
        self.total_tests += 1
        if result.status == "passed":
            self.passed += 1
        elif result.status == "failed":
            self.failed += 1
        elif result.status == "skipped":
            self.skipped += 1
        self.pass_rate = self.passed / self.total_tests if self.total_tests > 0 else 0.0

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self), indent=2, default=str)

    def save_json(self, output_dir: Path, filename: str | None = None) -> Path:
        """Save report as JSON file."""
        output_dir.mkdir(parents=True, exist_ok=True)
        fname = filename or f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path = output_dir / fname
        output_path.write_text(self.to_json(), encoding="utf-8")
        return output_path

    def save_html(self, output_dir: Path, filename: str | None = None) -> Path:
        """Save report as a self-contained HTML file."""
        output_dir.mkdir(parents=True, exist_ok=True)
        fname = filename or f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        output_path = output_dir / fname

        html = _generate_html(self)
        output_path.write_text(html, encoding="utf-8")
        return output_path

    def print_summary(self) -> None:
        """Print a summary to console with Windows encoding guard."""
        try:
            from rich.console import Console
            from rich.table import Table

            console = Console(highlight=False)
            table = Table(title=f"{self.suite_name} - Evaluation Report")

            table.add_column("Metric", style="cyan", no_wrap=True)
            table.add_column("Value", style="magenta")

            table.add_row("Total Tests", str(self.total_tests))
            table.add_row("Passed", f"[green]PASS: {self.passed}[/green]")
            table.add_row("Failed", f"[red]FAIL: {self.failed}[/red]")
            table.add_row("Skipped", f"[yellow]SKIP: {self.skipped}[/yellow]")
            table.add_row("Pass Rate", f"{self.pass_rate:.1%}")
            table.add_row("Timestamp", self.timestamp)

            console.print(table)
        except Exception:
            print(f"\n{'=' * 50}")
            print(f"  {self.suite_name} - Evaluation Report")
            print(f"{'=' * 50}")
            print(f"  Total: {self.total_tests} | Pass: {self.passed} | Fail: {self.failed}")
            print(f"  Pass Rate: {self.pass_rate:.1%}")
            print(f"{'=' * 50}\n")


def _generate_html(report: EvaluationReport) -> str:
    """Generate a self-contained HTML report."""
    status_color = "#22c55e" if report.pass_rate >= 0.9 else "#ef4444"

    rows_html = ""
    for r in report.results:
        badge = {
            "passed": '<span style="color:#22c55e">✅ PASS</span>',
            "failed": '<span style="color:#ef4444">❌ FAIL</span>',
            "skipped": '<span style="color:#f59e0b">⏭️ SKIP</span>',
        }.get(r.status, r.status)

        score_cell = f"{r.score:.2f}" if r.score is not None else "—"

        rows_html += f"""
        <tr>
            <td>{r.test_id}</td>
            <td>{r.test_name}</td>
            <td>{r.category}</td>
            <td>{badge}</td>
            <td>{score_cell}</td>
            <td>{r.details[:100]}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{report.suite_name} — Report</title>
    <style>
        body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #0f172a; color: #e2e8f0; }}
        h1 {{ color: #38bdf8; }}
        .summary {{ display: flex; gap: 1rem; margin: 1rem 0; }}
        .card {{ background: #1e293b; padding: 1rem 1.5rem; border-radius: 8px; text-align: center; }}
        .card .number {{ font-size: 2rem; font-weight: bold; color: {status_color}; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1.5rem; }}
        th, td {{ padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background: #1e293b; color: #94a3b8; }}
        tr:hover {{ background: #1e293b; }}
    </style>
</head>
<body>
    <h1>📊 {report.suite_name}</h1>
    <p style="color:#94a3b8">Generated: {report.timestamp}</p>

    <div class="summary">
        <div class="card"><div class="number">{report.total_tests}</div>Total</div>
        <div class="card"><div class="number" style="color:#22c55e">{report.passed}</div>Passed</div>
        <div class="card"><div class="number" style="color:#ef4444">{report.failed}</div>Failed</div>
        <div class="card"><div class="number">{report.pass_rate:.0%}</div>Pass Rate</div>
    </div>

    <table>
        <thead>
            <tr><th>ID</th><th>Test</th><th>Category</th><th>Status</th><th>Score</th><th>Details</th></tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
</body>
</html>"""
