#!/usr/bin/env python3
"""Recompute all 42 practice-plan answers and verify published artifacts."""

from __future__ import annotations

import argparse
import ast
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parent.parent
CHECKS_PATH = ROOT / "methodology" / "quantity-checks.json"
MANIFEST_PATH = ROOT / "source-manifest.json"


def evaluate(node: ast.AST) -> Decimal:
    if isinstance(node, ast.Expression):
        return evaluate(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return Decimal(str(node.value))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = evaluate(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp):
        left = evaluate(node.left)
        right = evaluate(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
    raise ValueError(f"Unsupported expression element: {ast.dump(node)}")


def calculate(expression: str) -> Decimal:
    tree = ast.parse(expression, mode="eval")
    return evaluate(tree)


def rounded(value: Decimal, decimals: int) -> Decimal:
    quantum = Decimal("1").scaleb(-decimals)
    return value.quantize(quantum, rounding=ROUND_HALF_UP)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def verify_pdf_text(plan: dict, checks: list[dict]) -> None:
    try:
        from pypdf import PdfReader
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "PDF text verification needs pypdf: python -m pip install pypdf"
        ) from error

    pdf_path = ROOT / "plans" / plan["file"]
    reader = PdfReader(pdf_path)
    if len(reader.pages) != 2:
        raise AssertionError(f"{plan['file']}: expected 2 pages, found {len(reader.pages)}")

    answer_text = normalized(reader.pages[1].extract_text() or "")
    if plan["answer_sheet"] not in answer_text:
        raise AssertionError(f"{plan['file']}: answer sheet {plan['answer_sheet']} not found")

    for index, check in enumerate(checks):
        start = answer_text.find(check["id"])
        if start < 0:
            raise AssertionError(f"{plan['file']}: {check['id']} not found on page 2")
        if index + 1 < len(checks):
            end = answer_text.find(checks[index + 1]["id"], start + len(check["id"]))
        else:
            end_candidates = [
                answer_text.find(marker, start)
                for marker in ("PRICING QA INPUTS", "FIXED QA PRICING INPUTS")
            ]
            end_candidates = [position for position in end_candidates if position >= 0]
            end = min(end_candidates) if end_candidates else len(answer_text)
        if end < 0:
            end = len(answer_text)
        row = answer_text[start:end]
        if check["display"] not in row:
            raise AssertionError(
                f"{plan['file']}: {check['id']} row does not contain {check['display']!r}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify formulas, units, IDs, hashes, and optional PDF answer text."
    )
    parser.add_argument(
        "--verify-pdf-text",
        action="store_true",
        help="also extract page 2 of each PDF with pypdf and verify every displayed answer",
    )
    args = parser.parse_args()

    checks_doc = json.loads(CHECKS_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest_by_file = {item["file"]: item for item in manifest["plan_sets"]}

    failures: list[str] = []
    seen_ids: set[str] = set()
    formula_passes = 0
    pdf_passes = 0

    if checks_doc.get("schema_version") != 1:
        failures.append("quantity-checks.json must use schema_version 1")
    if len(checks_doc.get("plans", [])) != 5:
        failures.append("quantity-checks.json must contain exactly five plans")

    for plan in checks_doc.get("plans", []):
        file_name = plan["file"]
        plan_checks = plan.get("checks", [])
        source = manifest_by_file.get(file_name)
        pdf_path = ROOT / "plans" / file_name

        if source is None:
            failures.append(f"{file_name}: missing from source-manifest.json")
        elif not pdf_path.is_file():
            failures.append(f"{file_name}: published PDF is missing")
        else:
            actual_bytes = pdf_path.stat().st_size
            actual_hash = sha256(pdf_path)
            if actual_bytes != int(source["bytes"]):
                failures.append(
                    f"{file_name}: byte count {actual_bytes} != manifest {source['bytes']}"
                )
            elif actual_hash != source["sha256"]:
                failures.append(
                    f"{file_name}: SHA-256 {actual_hash} != manifest {source['sha256']}"
                )
            else:
                pdf_passes += 1

        for check in plan_checks:
            check_id = check["id"]
            if check_id in seen_ids:
                failures.append(f"duplicate check ID: {check_id}")
                continue
            seen_ids.add(check_id)

            try:
                actual = rounded(calculate(check["expression"]), int(check["decimals"]))
                expected = Decimal(check["expected"])
                display_value, display_unit = check["display"].rsplit(" ", 1)
                displayed = Decimal(display_value.replace(",", ""))
                if check["unit"] not in {"EA", "LF", "SF", "CY"}:
                    raise AssertionError(f"unsupported unit {check['unit']!r}")
                if display_unit != check["unit"]:
                    raise AssertionError(
                        f"display unit {display_unit!r} != declared unit {check['unit']!r}"
                    )
                if actual != expected or displayed != expected:
                    raise AssertionError(
                        f"computed {actual}, expected {expected}, displayed {displayed}"
                    )
                formula_passes += 1
            except Exception as error:  # report all row failures in one run
                failures.append(f"{check_id}: {error}")

        if args.verify_pdf_text and pdf_path.is_file():
            try:
                verify_pdf_text(plan, plan_checks)
            except Exception as error:
                failures.append(str(error))

    if len(seen_ids) != 42:
        failures.append(f"expected 42 unique check IDs, found {len(seen_ids)}")
    if set(manifest_by_file) != {plan["file"] for plan in checks_doc.get("plans", [])}:
        failures.append("plan file set does not exactly match source-manifest.json")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1

    mode = "formula/hash/text" if args.verify_pdf_text else "formula/hash"
    print(
        json.dumps(
            {
                "status": "passed",
                "mode": mode,
                "plans": len(checks_doc["plans"]),
                "pdf_hashes": pdf_passes,
                "quantity_checks": formula_passes,
                "unique_ids": len(seen_ids),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
