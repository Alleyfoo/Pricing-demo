#!/usr/bin/env python3
"""Validate that the scaffold is properly configured."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def check_file(path: Path, description: str) -> bool:
    """Check if a file exists."""
    if path.exists():
        print(f"  [OK] {description}: {path}")
        return True
    else:
        print(f"  [MISSING] {description}: {path}")
        return False


def check_csv_parse(path: Path) -> bool:
    """Check if CSV file is parseable."""
    import csv

    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) >= 1:
                print(f"  [OK] CSV parseable: {path} ({len(rows)} rows)")
                return True
            else:
                print(f"  [EMPTY] CSV empty: {path}")
                return True  # Empty is OK
    except Exception as e:
        print(f"  [ERROR] CSV parse failed: {path} ({e})")
        return False


def check_json_schema(path: Path) -> bool:
    """Check if JSON schema is valid."""
    try:
        with open(path, encoding="utf-8") as f:
            schema = json.load(f)
            if "$schema" in schema or "type" in schema:
                print(f"  [OK] Valid JSON schema: {path}")
                return True
            else:
                print(f"  [WARN] JSON file but may not be schema: {path}")
                return True
    except json.JSONDecodeError as e:
        print(f"  [ERROR] Invalid JSON: {path} ({e})")
        return False
    except Exception as e:
        print(f"  [ERROR] Schema check failed: {path} ({e})")
        return False


def check_placeholders() -> bool:
    """Check for un-replaced placeholders like Pricing Demo."""
    import re

    # scaffold.yaml is excluded - it contains placeholder definitions intentionally
    placeholder_files = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "agent.md",
    ]

    # Match specific placeholder patterns (word chars inside braces)
    placeholder_pattern = re.compile(r"\{\{\w+\}\}")

    found = False
    for path in placeholder_files:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        matches = placeholder_pattern.findall(content)
        if matches:
            print(f"  [PLACEHOLDER] Unreplaced placeholders in: {path}")
            print(f"    Found: {', '.join(set(matches[:3]))}")  # Show first 3 unique
            found = True

    if not found:
        print("  [OK] No unreplaced placeholders found")
    return not found


def main() -> int:
    """Run all validation checks."""
    print("Validating agentic-scaffold...")
    print()

    all_ok = True

    # Core files
    print("Core files:")
    all_ok &= check_file(PROJECT_ROOT / "README.md", "README")
    all_ok &= check_file(PROJECT_ROOT / "agent.md", "Agent startup guide")
    all_ok &= check_file(PROJECT_ROOT / "scaffold.yaml", "Scaffold config")

    # Scripts
    print()
    print("Scripts:")
    all_ok &= check_file(PROJECT_ROOT / "scripts" / "tracker.py", "Tracker CLI")
    all_ok &= check_file(
        PROJECT_ROOT / "scripts" / "validate_scaffold.py", "Validation script"
    )

    # Docs
    print()
    print("Documentation:")
    all_ok &= check_file(PROJECT_ROOT / "docs" / "README.md", "Docs hub")
    all_ok &= check_file(
        PROJECT_ROOT / "docs" / "getting-started.md", "Getting started guide"
    )
    all_ok &= check_file(
        PROJECT_ROOT / "docs" / "agents" / "task-workflow.md", "Task workflow"
    )

    # Tracker
    print()
    print("Tracker:")
    tracker_path = PROJECT_ROOT / "docs" / "project" / "tracker_active.csv"
    if check_file(tracker_path, "Active tracker"):
        check_csv_parse(tracker_path)
    all_ok &= check_file(
        PROJECT_ROOT / "docs" / "project" / "tasks" / "_template.md", "Task template"
    )

    # Memory
    print()
    print("Memory:")
    all_ok &= check_file(PROJECT_ROOT / "docs" / "memory" / "README.md", "Memory guide")

    # Schemas
    print()
    print("Schemas:")
    schemas = [
        "input.schema.json",
        "normalized_request.schema.json",
        "plan.schema.json",
        "output.schema.json",
        "run.schema.json",
    ]
    for schema in schemas:
        schema_path = PROJECT_ROOT / "schemas" / schema
        if check_file(schema_path, schema):
            all_ok &= check_json_schema(schema_path)

    # Placeholders
    print()
    print("Configuration:")
    all_ok &= check_placeholders()

    # Summary
    print()
    if all_ok:
        print("[PASS] Scaffold validation complete")
        return 0
    else:
        print("[WARN] Some files missing or issues found")
        print(
            "Run setup: edit scaffold.yaml, replace {{placeholders}}, create missing files"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
