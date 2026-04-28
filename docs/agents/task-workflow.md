# Task Workflow

> How work gets done in Pricing Demo.

## Task Lifecycle

```
Planned → Active → In Progress → Done → Reviewed
```

| Status | Meaning |
|--------|---------|
| **Planned** | Created, not started |
| **Active** | Selected for work, being read/understood |
| **In Progress** | Implementation underway |
| **Done** | Implementation complete, verification done |
| **Reviewed** | Audited/verified, task complete |
| **Blocked** | Cannot proceed (document blocker in task) |
| **Deferred** | Intentionally postponed |
| **Needs Fix** | Review found issues, back to In Progress |

## Creating Tasks

```bash
python scripts/tracker.py new FEAT-001 "Add user authentication"
```

This creates:
1. Entry in `docs/project/tracker_active.csv`
2. Task file at `docs/project/tasks/FEAT-001.md`

## Task ID Conventions

| Prefix | Type | Example |
|--------|------|---------|
| `FEAT-` | Feature | `FEAT-001` |
| `FIX-` | Bug fix | `FIX-001` |
| `RESEARCH-` | Research/Design | `RESEARCH-001` |
| `DEBT-` | Technical debt | `DEBT-001` |
| `EVAL-` | Evaluation | `EVAL-001` |
| `STUDIO-` | GUI/Editor work | `STUDIO-001` |
| `ROADMAP-` | Roadmap item | `ROADMAP-001` |
| `QA-` | Quality assurance | `QA-001` |

Auto-numbering: use prefix only
```bash
python scripts/tracker.py new FEAT "Add authentication"  # Creates FEAT-003 if last was FEAT-002
```

## Task File Structure

Every task file includes:

- **Header table:** Metadata (ID, Area, Type, Priority, Status, Owner, Created, Completed, Blocked By)
- **Goal:** One-line definition of done
- **Out of Scope:** Explicit non-goals
- **Source of Intent:** Why this exists
- **Files:** Created/modified files
- **Plan:** Slice table (Deliverable → Files → Verification → Exit Criteria)
- **Notes:** Implementation narrative
- **Verification:** Test commands and results
- **Review Checklist:** Pass/fail items

## Slice Planning

Break work into independently verifiable slices:

| Slice | Deliverable | Files | Verification | Exit Criteria |
|-------|-------------|-------|--------------|---------------|
| 1 | Schema defined | `schemas/input.schema.json` | Validates test JSON | Schema accepted |
| 2 | Parser implemented | `src/parser.py` | Unit tests pass | 80% coverage |
| 3 | CLI wired | `src/cli.py` | End-to-end test | Happy path works |

## Working a Task

1. **Read:** `docs/project/tracker_active.csv` → find your task
2. **Detail:** `python scripts/tracker.py detail FEAT-001` → read full context
3. **Start:** Update Status → `Active`
4. **Work:** Update **Notes** section as you go
5. **Verify:** Run tests, document in **Verification**
6. **Complete:** Status → `Done`, fill **Review Checklist**

## Review Process

For `solo` mode:

### Solo
- Self-review against checklist
- Update tracker to `Reviewed` when done

### Pair
- Self-review
- Second person reviews task file
- Update to `Reviewed` when both agree

### Team
- Self-review
- Team review session or PR review
- Update to `Reviewed` when team approves

## Blocked Tasks

When blocked:
1. Status → `Blocked`
2. In header table: `Blocked By: RESEARCH-002`
3. In **Notes**: Explain what's needed
4. Create blocker task if it doesn't exist

## Archiving

When `Reviewed`, tasks can be archived:
- Move row from `tracker_active.csv` to `tracker_archive.csv`
- Keep task file in `docs/project/tasks/`

## Tips

- Keep **Goal** one line — if you can't, split the task
- **Out of Scope** prevents mid-task scope creep
- **Source of Intent** helps when you forget why you started
- Update **Notes** as you work, not at the end
- **Verification** should be copy-pasteable commands with output
