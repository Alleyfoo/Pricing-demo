# Getting Started

> 10-minute walkthrough of the agentic scaffold workflow.

## Prerequisites

- Python 3.11+ installed
- Git repository initialized (or this scaffold copied into an existing repo)

## Step 1: Configure the Scaffold (2 min)

Edit `scaffold.yaml` and replace all `{{placeholders}}`:

```yaml
project_name: "My Project"
project_slug: "my-project"
default_area: "Core"
review_mode: "solo"
capability_profile: "files_search_shell_edit"
workflow_mode: "docs_only"
memory_mode: "index"
schema_mode: "json-schema"
```

Replace placeholders in other files:
- `README.md`: `Pricing Demo`, etc.
- `agent.md`: `docs_only`, `files_search_shell_edit`

## Step 2: Validate Setup (1 min)

Run the validation script:

```bash
python scripts/validate_scaffold.py
```

You should see `[PASS] Scaffold validation complete`.

## Step 3: Create Your First Task (2 min)

Use the tracker CLI:

```bash
python scripts/tracker.py new RESEARCH-001 "Explore domain boundaries"
```

This creates:
- Entry in `docs/project/tracker_active.csv`
- Task file at `docs/project/tasks/RESEARCH-001.md`

## Step 4: Fill Out the Task (3 min)

Open `docs/project/tasks/RESEARCH-001.md` and fill in:

- **Goal:** One-line definition of done
- **Out of Scope:** What you're NOT doing
- **Source of Intent:** Why this task exists
- **Plan:** At least one slice with deliverable, files, verification

Example:

```markdown
## Goal

Define the boundaries and core entities of the problem domain.

## Out of Scope

- Implementation
- UI/UX design

## Source of Intent

Project charter: build a focused tool for X.

## Plan

| Slice | Deliverable | Files | Verification |
|-------|-------------|-------|--------------|
| 1 | Domain glossary | `docs/domain/glossary.md` | Review with stakeholder |
```

## Step 5: Mark Active and Work (2 min)

Update the tracker CSV:
- Change `Status` from `Planned` to `Active`

Work through your plan. Update the **Notes** section as you go:

```markdown
## Notes

2024-01-15: Defined core entities. Decided to scope out Y for now.
2024-01-16: Glossary reviewed. Minor tweaks to terminology.
```

## Step 6: Complete and Verify (2 min)

When done:

1. Run verification steps (tests, checks)
2. Fill **Verification** section with evidence:

```markdown
## Verification

```bash
python -m pytest tests/
```

```
3 passed, 0 failed
```
```

3. Update tracker: `Status` → `Done`
4. Fill **Review Checklist** in task file

## Next Steps

- Read [agents/task-workflow.md](agents/task-workflow.md) for full lifecycle
- Add knowledge to [memory/README.md](memory/README.md)
- Create next task: `python scripts/tracker.py new FEAT-001 "First implementation slice"`

## Common Commands

```bash
# List open tasks
python scripts/tracker.py open

# Show next priority task
python scripts/tracker.py next

# View task details
python scripts/tracker.py detail RESEARCH-001

# Statistics
python scripts/tracker.py stats
```

## Getting Help

If stuck:
1. Check `agent.md` for AI assistant startup guide
2. Review [agents/task-workflow.md](agents/task-workflow.md)
3. Validate scaffold: `python scripts/validate_scaffold.py`
