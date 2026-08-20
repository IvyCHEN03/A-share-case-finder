#!/usr/bin/env python3
"""Smoke tests for the bundled deterministic pipeline."""

from __future__ import annotations

import json
import subprocess
import tempfile
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "src" / "a-share-corner-case-finder" / "scripts" / "case_pipeline.py"


def run(*args: str) -> dict:
    completed = subprocess.run(
        ["python3", str(SCRIPT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def run_payload(payload: dict, *args: str) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False)
        handle.flush()
        return subprocess.run(
            ["python3", str(SCRIPT), "classify", handle.name, *args],
            check=False,
            capture_output=True,
            text=True,
        )


def main() -> None:
    selftest = run("selftest")
    assert selftest["ok"] is True
    assert selftest["ratings"] == [
        "S1 / A-E1",
        "S1 / B-E2",
        "S1 / C-E1",
        "S1 / D-E3",
    ]

    schema = run("schema")
    classified = run_payload(schema)
    assert classified.returncode == 0
    classified_data = json.loads(classified.stdout)
    assert classified_data["date_check"]["as_of_date"] == "2025-12-31"

    future_payload = dict(schema)
    future_payload["as_of_date"] = (date.today() + timedelta(days=1)).isoformat()
    rejected = run_payload(future_payload)
    assert rejected.returncode == 2
    assert "in the future" in rejected.stdout

    late_event_payload = dict(schema)
    late_event_payload["as_of_date"] = "2024-01-01"
    rejected = run_payload(late_event_payload)
    assert rejected.returncode == 2
    assert "later than as_of_date" in rejected.stdout

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = tmp_path / "source.pdf"
        target = tmp_path / "target.pdf"
        source.write_bytes(b"%PDF-1.4\n% smoke test\n")
        fetched = run(
            "fetch",
            "--url",
            source.as_uri(),
            "--output",
            str(target),
            "--retries",
            "1",
        )
        assert fetched["ok"] is True
        assert target.read_bytes().startswith(b"%PDF-")

    print("case_pipeline smoke tests passed")


if __name__ == "__main__":
    main()
