# Documentation Hub

Welcome to the Pricing Demo documentation.

## Quick Navigation

| I want to... | Go to |
|--------------|-------|
| Get started | [getting-started.md](getting-started.md) |
| Understand the workflow | [agents/task-workflow.md](agents/task-workflow.md) |
| Create a task | [agents/task-workflow.md#creating-tasks](agents/task-workflow.md) |
| See active work | [project/tracker_active.csv](project/tracker_active.csv) |
| Find project knowledge | [memory/README.md](memory/README.md) |

## Structure

```
docs/
├── README.md                 # This file
├── getting-started.md        # 10-minute tutorial
├── architecture/             # System design docs
│   └── overview.md
├── agents/                   # AI assistant guides
│   ├── task-workflow.md      # How work gets done
│   ├── reviewer.md           # Code review process
│   ├── source-restorer.md    # Source recovery
│   └── regression-hunter.md  # Test validation
├── project/                  # Active work tracking
│   ├── tracker_active.csv    # Slim task index
│   └── tasks/                # Per-task detail files
├── memory/                   # Project knowledge base
└── planning/                 # Research and decisions
```

## Conventions

- **Docs:** Markdown, lower-kebab-case filenames
- **Tasks:** `FEAT-001`, `FIX-001`, uppercase with zero-padding
- **Schemas:** `*.schema.json` for data contracts
- **Memory:** Lookup surfaces, not mandatory reading
