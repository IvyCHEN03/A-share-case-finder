#!/usr/bin/env python3
"""Deterministic helpers for A-share corner-case research.

Standard-library only.  The script does not search for cases or make legal
judgments; it handles repeatable transport, file checks, and rating logic.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any


ALLOWED_STRENGTHS = {"hard", "preferred", "fallback", "unresolved"}
RETRYABLE_HTTP = {408, 425, 429, 500, 502, 503, 504}


def parse_iso_date(value: Any, label: str) -> date:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be an ISO date (YYYY-MM-DD)")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO date (YYYY-MM-DD)") from exc


def validate_dates(payload: dict[str, Any]) -> dict[str, Any]:
    today = date.today()
    scenario_mode = payload.get("scenario_mode") is True
    as_of = parse_iso_date(payload.get("as_of_date", today.isoformat()), "as_of_date")
    if as_of > today and not scenario_mode:
        raise ValueError(
            f"as_of_date {as_of.isoformat()} is in the future; set scenario_mode=true only for a clearly labelled hypothetical"
        )

    for case in payload.get("cases") or []:
        case_name = case.get("name", "<unnamed>")
        dates = case.get("dates") or {}
        if not isinstance(dates, dict):
            raise ValueError(f"{case_name}.dates must be an object")
        for event, value in dates.items():
            event_date = parse_iso_date(value, f"{case_name}.dates.{event}")
            if event_date > as_of and not scenario_mode:
                raise ValueError(
                    f"{case_name}.dates.{event} {event_date.isoformat()} is later than as_of_date {as_of.isoformat()}"
                )

    return {
        "today": today.isoformat(),
        "as_of_date": as_of.isoformat(),
        "scenario_mode": scenario_mode,
    }


def fail(message: str, code: int = 2) -> None:
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
    raise SystemExit(code)


def dump(data: Any, output: str | None = None) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def validate_pdf(data: bytes) -> bool:
    return data.lstrip().startswith(b"%PDF-")


def fetch(args: argparse.Namespace) -> None:
    attempts: list[dict[str, Any]] = []
    headers = {"User-Agent": "Mozilla/5.0 AShareCaseResearch/1.0"}

    for url in args.url:
        for attempt in range(1, args.retries + 1):
            try:
                request = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(request, timeout=args.timeout) as response:
                    data = response.read(args.max_bytes + 1)
                    if len(data) > args.max_bytes:
                        raise ValueError(f"response exceeds {args.max_bytes} bytes")
                    if args.expect == "pdf" and not validate_pdf(data):
                        raise ValueError("response is not a valid PDF payload")

                    output = Path(args.output)
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_bytes(data)
                    dump(
                        {
                            "ok": True,
                            "source_url": url,
                            "output": str(output.resolve()),
                            "bytes": len(data),
                            "attempt": attempt,
                            "expect": args.expect,
                            "attempts": attempts,
                        }
                    )
                    return
            except urllib.error.HTTPError as exc:
                attempts.append(
                    {"url": url, "attempt": attempt, "error": f"HTTP {exc.code}"}
                )
                if exc.code not in RETRYABLE_HTTP:
                    break
            except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
                attempts.append(
                    {"url": url, "attempt": attempt, "error": str(exc)}
                )

            if attempt < args.retries:
                time.sleep(min(args.backoff * (2 ** (attempt - 1)), 8.0))

    dump(
        {
            "ok": False,
            "error": "all source URLs failed",
            "attempts": attempts,
            "next_action": "try an official mirror; otherwise downgrade evidence and disclose the gap",
        }
    )
    raise SystemExit(2)


def inspect_pdf(args: argparse.Namespace) -> None:
    path = Path(args.file)
    if not path.is_file():
        fail(f"file not found: {path}")
    data = path.read_bytes()
    if not validate_pdf(data):
        fail("file does not start with a PDF signature")

    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        dump(
            {
                "ok": True,
                "pdf_valid": True,
                "text_status": "tool_unavailable",
                "next_action": "use the host PDF reader, page rendering, or OCR",
            }
        )
        return

    try:
        result = subprocess.run(
            [pdftotext, str(path), "-"],
            check=False,
            capture_output=True,
            timeout=args.timeout,
        )
    except subprocess.TimeoutExpired:
        dump(
            {
                "ok": True,
                "pdf_valid": True,
                "text_status": "timeout",
                "next_action": "extract selected pages or render/OCR the relevant pages",
            }
        )
        return

    text = result.stdout.decode("utf-8", errors="ignore").strip()
    if result.returncode != 0:
        dump(
            {
                "ok": True,
                "pdf_valid": True,
                "text_status": "extract_failed",
                "stderr": result.stderr.decode("utf-8", errors="ignore")[-500:],
                "next_action": "render the relevant pages and use OCR; verify numbers visually",
            }
        )
    elif len(text) < args.min_text_chars:
        dump(
            {
                "ok": True,
                "pdf_valid": True,
                "text_status": "scanned_or_sparse",
                "text_chars": len(text),
                "next_action": "render/OCR the relevant pages and compare against the page image",
            }
        )
    else:
        dump(
            {
                "ok": True,
                "pdf_valid": True,
                "text_status": "extractable",
                "text_chars": len(text),
            }
        )


def evidence_grade(evidence: dict[str, Any]) -> str:
    source = evidence.get("source_url") or evidence.get("source_file")
    locator = str(evidence.get("locator") or "").strip()
    if evidence.get("primary_text_read") is True and source and locator:
        return "E1"
    if evidence.get("primary_file_located") is True and source:
        return "E2"
    if evidence.get("secondary_only") is True or evidence.get("search_snippet_only") is True:
        return "E3"
    return "E4"


def classify_one(
    case: dict[str, Any], conditions: dict[str, dict[str, Any]], scope_version: str
) -> dict[str, Any]:
    results = case.get("results")
    if not isinstance(results, dict):
        raise ValueError(f"case {case.get('name', '<unnamed>')} is missing results")

    false_non_relaxable: list[str] = []
    false_relaxable: list[str] = []
    unknown_hard: list[str] = []
    unresolved_scope: list[str] = []
    preferred_met = 0
    preferred_known = 0

    for condition_id, condition in conditions.items():
        value = results.get(condition_id)
        if value not in (True, False, None):
            raise ValueError(f"{case.get('name')}.{condition_id} must be true, false, or null")

        strength = condition["strength"]
        if strength == "hard":
            if value is None:
                unknown_hard.append(condition_id)
            elif value is False:
                target = false_relaxable if condition.get("relaxable") is True else false_non_relaxable
                target.append(condition_id)
        elif strength == "preferred" and value is not None:
            preferred_known += 1
            preferred_met += int(value is True)
        elif strength == "unresolved":
            unresolved_scope.append(condition_id)

    if false_non_relaxable:
        match = "C"
        reason = f"confirmed hard-condition conflict: {', '.join(false_non_relaxable)}"
    elif unknown_hard or unresolved_scope:
        match = "D"
        unresolved = unknown_hard + unresolved_scope
        reason = f"unresolved conditions: {', '.join(unresolved)}"
    elif false_relaxable:
        match = "B"
        reason = f"only relaxable hard conditions are missing: {', '.join(false_relaxable)}"
    else:
        match = "A"
        reason = "all hard conditions are satisfied"

    evidence = evidence_grade(case.get("evidence") or {})
    return {
        "name": case.get("name", "<unnamed>"),
        "scope_version": scope_version,
        "match": match,
        "evidence": evidence,
        "rating": f"{scope_version} / {match}-{evidence}",
        "strict_eligible": match == "A" and evidence == "E1",
        "preferred_met": preferred_met,
        "preferred_known": preferred_known,
        "reason": reason,
    }


def classify(args: argparse.Namespace) -> None:
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    scope_version = str(payload.get("scope_version") or "S1")
    raw_conditions = payload.get("conditions")
    cases = payload.get("cases")
    if not isinstance(raw_conditions, list) or not raw_conditions:
        fail("conditions must be a non-empty list")
    if not isinstance(cases, list) or not cases:
        fail("cases must be a non-empty list")

    try:
        date_check = validate_dates(payload)
    except ValueError as exc:
        fail(str(exc))

    conditions: dict[str, dict[str, Any]] = {}
    for condition in raw_conditions:
        if not isinstance(condition, dict) or not condition.get("id"):
            fail("each condition requires an id")
        condition_id = str(condition["id"])
        strength = condition.get("strength")
        if strength not in ALLOWED_STRENGTHS:
            fail(f"{condition_id} has invalid strength: {strength}")
        if condition_id in conditions:
            fail(f"duplicate condition id: {condition_id}")
        conditions[condition_id] = condition

    try:
        rows = [classify_one(case, conditions, scope_version) for case in cases]
    except ValueError as exc:
        fail(str(exc))

    order = {"A": 0, "B": 1, "D": 2, "C": 3}
    rows.sort(
        key=lambda row: (
            order[row["match"]],
            -(row["preferred_met"] / row["preferred_known"] if row["preferred_known"] else 0),
            row["name"],
        )
    )
    dump(
        {
            "ok": True,
            "scope_version": scope_version,
            "date_check": date_check,
            "cases": rows,
        },
        args.output,
    )


def schema(_: argparse.Namespace) -> None:
    dump(
        {
            "scope_version": "S1",
            "as_of_date": "2025-12-31",
            "conditions": [
                {"id": "N1", "label": "属于IPO募投项目", "strength": "hard", "relaxable": False},
                {"id": "N2", "label": "原境内主体继续保留", "strength": "hard", "relaxable": False},
                {"id": "P1", "label": "逐主体披露金额", "strength": "preferred"},
            ],
            "cases": [
                {
                    "name": "历史示例公司",
                    "dates": {
                        "prospectus": "2022-08-29",
                        "change_announcement": "2024-03-20",
                    },
                    "results": {"N1": True, "N2": True, "P1": True},
                    "evidence": {
                        "primary_file_located": True,
                        "primary_text_read": True,
                        "source_file": "原始披露文件.pdf",
                        "locator": "募集资金运用章节",
                    },
                }
            ],
        }
    )


def selftest(_: argparse.Namespace) -> None:
    conditions = {
        "N1": {"strength": "hard", "relaxable": False},
        "N2": {"strength": "hard", "relaxable": True},
        "P1": {"strength": "preferred"},
    }
    cases = [
        {
            "name": "A",
            "results": {"N1": True, "N2": True, "P1": True},
            "evidence": {"primary_text_read": True, "source_file": "x.pdf", "locator": "p.1"},
        },
        {
            "name": "B",
            "results": {"N1": True, "N2": False, "P1": False},
            "evidence": {"primary_file_located": True, "source_file": "x.pdf"},
        },
        {
            "name": "C",
            "results": {"N1": False, "N2": True, "P1": True},
            "evidence": {"primary_text_read": True, "source_file": "x.pdf", "locator": "p.1"},
        },
        {
            "name": "D",
            "results": {"N1": None, "N2": True, "P1": True},
            "evidence": {"secondary_only": True},
        },
    ]
    actual = [classify_one(case, conditions, "S1")["rating"] for case in cases]
    expected = ["S1 / A-E1", "S1 / B-E2", "S1 / C-E1", "S1 / D-E3"]
    if actual != expected:
        fail(f"selftest mismatch: {actual}")
    dump({"ok": True, "tests": 4, "ratings": actual})


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)

    fetch_parser = sub.add_parser("fetch", help="download from official URLs with retries and validation")
    fetch_parser.add_argument("--url", action="append", required=True, help="source URL; repeat for mirrors")
    fetch_parser.add_argument("--output", required=True)
    fetch_parser.add_argument("--expect", choices=("pdf", "any"), default="pdf")
    fetch_parser.add_argument("--timeout", type=float, default=20.0)
    fetch_parser.add_argument("--retries", type=int, default=3)
    fetch_parser.add_argument("--backoff", type=float, default=1.0)
    fetch_parser.add_argument("--max-bytes", type=int, default=100 * 1024 * 1024)
    fetch_parser.set_defaults(func=fetch)

    inspect_parser = sub.add_parser("inspect", help="check PDF validity and text extractability")
    inspect_parser.add_argument("file")
    inspect_parser.add_argument("--timeout", type=float, default=30.0)
    inspect_parser.add_argument("--min-text-chars", type=int, default=200)
    inspect_parser.set_defaults(func=inspect_pdf)

    classify_parser = sub.add_parser("classify", help="assign deterministic A/B/C/D and E1-E4 ratings")
    classify_parser.add_argument("input")
    classify_parser.add_argument("--output")
    classify_parser.set_defaults(func=classify)

    schema_parser = sub.add_parser("schema", help="print a sample classification input")
    schema_parser.set_defaults(func=schema)

    selftest_parser = sub.add_parser("selftest", help="run built-in rating tests")
    selftest_parser.set_defaults(func=selftest)
    return root


def main() -> None:
    args = parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
