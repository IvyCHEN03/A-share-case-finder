#!/usr/bin/env python3
"""Validate public eval JSONL files without external dependencies."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FILES = {
    "trigger-cases.jsonl": {"id", "prompt", "expected_trigger", "reason"},
    "research-cases.jsonl": {
        "id",
        "title",
        "prompt",
        "expected_class",
        "must_include",
        "must_not_claim",
        "gold_file",
        "risk_tags",
    },
}


def main() -> None:
    seen: set[str] = set()
    count = 0

    for filename, required in FILES.items():
        path = ROOT / filename
        if not path.is_file():
            raise SystemExit(f"missing eval file: {path}")

        for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            try:
                case = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{filename}:{line_number}: invalid JSON: {exc}") from exc

            missing = required - case.keys()
            if missing:
                raise SystemExit(
                    f"{filename}:{line_number}: missing fields: {sorted(missing)}"
                )

            case_id = case["id"]
            if case_id in seen:
                raise SystemExit(f"duplicate case id: {case_id}")
            seen.add(case_id)

            if filename == "research-cases.jsonl":
                gold = ROOT / case["gold_file"]
                if not gold.is_file():
                    raise SystemExit(
                        f"{filename}:{line_number}: missing gold file: {gold}"
                    )
            count += 1

    print(f"validated {count} eval cases across {len(FILES)} files")


if __name__ == "__main__":
    main()
