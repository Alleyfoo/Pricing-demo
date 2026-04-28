#!/usr/bin/env python3
"""Task management CLI for the hybrid tracker system."""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
ACTIVE_TRACKER = PROJECT_ROOT / "docs" / "project" / "tracker_active.csv"
ARCHIVE_TRACKER = PROJECT_ROOT / "docs" / "project" / "tracker_archive.csv"
TASKS_DIR = PROJECT_ROOT / "docs" / "project" / "tasks"
TEMPLATE_FILE = TASKS_DIR / "_template.md"
SCAFFOLD_YAML = PROJECT_ROOT / "scaffold.yaml"


def _get_default_area() -> str:
    """Read default_area from scaffold.yaml, fallback to 'Core'."""
    try:
        import re

        if SCAFFOLD_YAML.exists():
            content = SCAFFOLD_YAML.read_text(encoding="utf-8")
            # Match default_area: "value" or default_area: value
            match = re.search(r'default_area:\s*"?([^"\n]+)"?', content)
            if match:
                value = match.group(1).strip()
                # If it's still a placeholder, fallback
                if not value.startswith("{{"):
                    return value
    except Exception:
        pass
    return "Core"


def _read_active() -> list[dict[str, str]]:
    """Read active tracker CSV."""
    if not ACTIVE_TRACKER.exists():
        return []
    with open(ACTIVE_TRACKER, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_active(rows: list[dict[str, str]]) -> None:
    """Write active tracker CSV."""
    ACTIVE_TRACKER.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        # Write header only
        with open(ACTIVE_TRACKER, "w", newline="", encoding="utf-8") as f:
            f.write("ID,Area,Type,Priority,Status,Title\n")
        return
    fieldnames = ["ID", "Area", "Type", "Priority", "Status", "Title"]
    with open(ACTIVE_TRACKER, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _next_id(prefix: str) -> str:
    """Find next available number for a prefix."""
    rows = _read_active()
    numbers = []
    for row in rows:
        id_val = row.get("ID", "")
        if id_val.startswith(prefix + "-"):
            try:
                num = int(id_val.split("-")[1])
                numbers.append(num)
            except (IndexError, ValueError):
                continue
    next_num = max(numbers, default=0) + 1
    return f"{prefix}-{next_num:03d}"


def _create_task_file(task_id: str, title: str) -> Path:
    """Create a new task markdown file from template."""
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    task_file = TASKS_DIR / f"{task_id}.md"

    template_content = (
        _TEMPLATE
        if not TEMPLATE_FILE.exists()
        else TEMPLATE_FILE.read_text(encoding="utf-8")
    )

    # Replace placeholders
    content = template_content.replace("{ID}", task_id).replace("{Title}", title)
    content = content.replace("{Area}", _get_default_area())
    content = content.replace(
        "YYYY-MM-DD", datetime.now(timezone.utc).strftime("%Y-%m-%d")
    )

    task_file.write_text(content, encoding="utf-8")
    return task_file


def cmd_new(args: argparse.Namespace) -> int:
    """Create a new task."""
    # Auto-number if prefix only
    task_id = args.id
    if "-" not in task_id:
        task_id = _next_id(task_id.upper())

    rows = _read_active()

    # Check for duplicates
    if any(r.get("ID") == task_id for r in rows):
        print(f"Error: Task {task_id} already exists", file=sys.stderr)
        return 1

    # Add to tracker
    default_area = _get_default_area()
    new_row = {
        "ID": task_id,
        "Area": default_area,
        "Type": _infer_type(task_id),
        "Priority": "Medium",
        "Status": "Planned",
        "Title": args.title,
    }
    rows.append(new_row)
    _write_active(rows)

    # Create task file
    task_file = _create_task_file(task_id, args.title)

    print(f"Created task: {task_id}")
    print(f"  Title: {args.title}")
    print(f"  File: {task_file}")
    return 0


def _infer_type(task_id: str) -> str:
    """Infer task type from ID prefix."""
    prefix = task_id.split("-")[0].upper()
    type_map = {
        "FEAT": "Feature",
        "FIX": "Fix",
        "RESEARCH": "Research",
        "DEBT": "Debt",
        "EVAL": "Evaluation",
        "STUDIO": "Task",
        "ROADMAP": "Roadmap",
        "QA": "QA",
    }
    return type_map.get(prefix, "Task")


def cmd_open(args: argparse.Namespace) -> int:
    """List open tasks."""
    rows = _read_active()
    open_rows = [
        r for r in rows if r.get("Status") not in ("Done", "Reviewed", "Archived")
    ]

    if not open_rows:
        print("No open tasks.")
        return 0

    print(f"{'ID':<12} {'Status':<12} {'Priority':<10} {'Title'}")
    print("-" * 60)
    for row in open_rows:
        print(
            f"{row['ID']:<12} {row['Status']:<12} {row.get('Priority', '-'):<10} {row['Title']}"
        )
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    """Show highest priority actionable task."""
    rows = _read_active()
    candidates = [
        r for r in rows if r.get("Status") in ("Planned", "Active", "In Progress")
    ]

    if not candidates:
        print(
            "No actionable tasks. Create one with: tracker.py new FEAT-001 'Description'"
        )
        return 0

    # Sort by priority
    priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    candidates.sort(key=lambda r: priority_order.get(r.get("Priority", "Medium"), 2))

    top = candidates[0]
    print(f"Next task: {top['ID']}")
    print(f"  Title: {top['Title']}")
    print(f"  Status: {top['Status']}")
    print(f"  Priority: {top.get('Priority', 'Medium')}")

    task_file = TASKS_DIR / f"{top['ID']}.md"
    if task_file.exists():
        print(f"  File: {task_file}")

    return 0


def cmd_detail(args: argparse.Namespace) -> int:
    """Show task details."""
    task_file = TASKS_DIR / f"{args.id}.md"
    if not task_file.exists():
        print(f"Task file not found: {task_file}", file=sys.stderr)
        return 1

    print(task_file.read_text(encoding="utf-8"))
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Show tracker statistics."""
    rows = _read_active()

    status_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}

    for row in rows:
        status = row.get("Status") or "Unknown"
        task_type = row.get("Type") or "Unknown"
        priority = row.get("Priority") or "Medium"
        status_counts[status] = status_counts.get(status, 0) + 1
        type_counts[task_type] = type_counts.get(task_type, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    print(f"Total tasks: {len(rows)}")
    print()
    print("By Status:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    print()
    print("By Type:")
    for t, count in sorted(type_counts.items()):
        print(f"  {t}: {count}")
    print()
    print("By Priority:")
    for p in ["Critical", "High", "Medium", "Low"]:
        if p in priority_counts:
            print(f"  {p}: {priority_counts[p]}")

    return 0


# Template content for new task files
_TEMPLATE = """# {ID}: {Title}

| Field | Value |
|-------|-------|
| Area | {Area} |
| Type | Feature |
| Priority | Medium |
| Status | Planned |
| Owner | AI |
| Created | YYYY-MM-DD |
| Completed | |
| Blocked By | |

## Goal

One-line goal. What does "done" look like?

## Out of Scope

- Explicit non-goals to prevent scope creep

## Source of Intent

- Why this task exists

## Files

- Files to be created or modified

## Plan

| Slice | Deliverable | Files | Verification |
|-------|-------------|-------|--------------|
| 1 | Initial setup | | |

## Notes

Implementation narrative, decisions, deviations.

## Verification

Test commands and results.

## Review Checklist

- [ ] Implementation complete
- [ ] Source of intent linked
- [ ] Tests passing
- [ ] Final status updated in tracker
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Task management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # new
    new_parser = subparsers.add_parser("new", help="Create new task")
    new_parser.add_argument(
        "id", help="Task ID (e.g., FEAT-001 or just FEAT for auto-number)"
    )
    new_parser.add_argument("title", help="Task title")

    # open
    subparsers.add_parser("open", help="List open tasks")

    # next
    subparsers.add_parser("next", help="Show next priority task")

    # detail
    detail_parser = subparsers.add_parser("detail", help="Show task details")
    detail_parser.add_argument("id", help="Task ID")

    # stats
    subparsers.add_parser("stats", help="Show statistics")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    # Map to functions
    commands = {
        "new": cmd_new,
        "open": cmd_open,
        "next": cmd_next,
        "detail": cmd_detail,
        "stats": cmd_stats,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
