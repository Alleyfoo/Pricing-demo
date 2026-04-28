# AI Assistant Startup Guide

## Start Here

When starting a new session, read these files in order:

1. [`README.md`](README.md) — Project overview and quick start
2. [`scaffold.yaml`](scaffold.yaml) — Project configuration (placeholders, modes)
3. [`docs/getting-started.md`](docs/getting-started.md) — 10-minute tutorial
4. [`docs/project/tracker_active.csv`](docs/project/tracker_active.csv) — Active task index

## Operating Rules

### Task Management
- Use the tracker: `python scripts/tracker.py --new {ID} "{TITLE}"`
- Read full task context: `docs/project/tasks/{ID}.md`
- Update status in both CSV and task file when starting/completing

### File Conventions
- Tasks: `FEAT-001`, `FIX-001`, `RESEARCH-001`, etc. (uppercase, zero-padded)
- Docs: lower-kebab-case (`task-workflow.md`)
- Schemas: `*.schema.json`

### Memory System
- Curated knowledge: `docs/memory/` — lookup surfaces, not mandatory reading
- Session notes: add to task files, not root files
- Cross-references: use `memory/INDEX.md` for topic navigation

### Workflow Mode

Check `scaffold.yaml` for the configured `workflow_mode`:

| Mode | Behavior |
|------|----------|
| `docs_only` | Read workflow markdown, execute manually |
| `ide_executable` | Workflow files may have `// turbo` annotations for IDE execution |

## Capabilities Profile

Check `scaffold.yaml` for the configured `capability_profile`.

Standard profile is `files_search_shell_edit`:
- Read files
- Search/grep codebase
- Edit/write files
- Run shell commands

## Getting Help

- **Create task:** `python scripts/tracker.py new FEAT-001 "Description"`
- **List open:** `python scripts/tracker.py open`
- **Next priority:** `python scripts/tracker.py next`
- **Task detail:** `python scripts/tracker.py detail FEAT-001`

## First Task Checklist

- [ ] Read `docs/getting-started.md`
- [ ] Check `docs/project/tracker_active.csv` for existing work
- [ ] Create first task using tracker CLI
- [ ] Fill out task template in `docs/project/tasks/{ID}.md`
- [ ] Validate scaffold: `python scripts/validate_scaffold.py`
