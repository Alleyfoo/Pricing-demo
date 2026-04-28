# Full Example

> Complete scaffold with all features enabled.

## Files

```
full/
├── README.md
├── agent.md
├── scaffold.yaml
├── scripts/
│   ├── tracker.py
│   └── validate_scaffold.py
├── docs/
│   ├── README.md
│   ├── getting-started.md
│   ├── agents/
│   │   └── task-workflow.md
│   ├── project/
│   │   ├── tracker_active.csv
│   │   └── tasks/
│   │       ├── _template.md
│   │       ├── RESEARCH-001.md
│   │       └── FEAT-001.md
│   ├── memory/
│   │   └── README.md
│   └── architecture/
│       └── overview.md
└── schemas/
    ├── input.schema.json
    ├── plan.schema.json
    ├── output.schema.json
    └── run.schema.json
```

## What This Demonstrates

- Complete workflow with all scaffold features
- Research → Feature progression
- Memory usage
- Schema validation
- Architecture documentation

## Sample Tasks

### RESEARCH-001: Domain Exploration

**Goal:** Define boundaries and core entities.

**Plan:**
1. Domain glossary
2. Boundary analysis
3. Stakeholder review

### FEAT-001: Core Implementation

**Goal:** Build first slice based on research findings.

**Plan:**
1. Schema design
2. Parser implementation
3. CLI wiring

## Usage

```bash
# Validate setup
python scripts/validate_scaffold.py

# Check next priority
python scripts/tracker.py next

# View research task
python scripts/tracker.py detail RESEARCH-001
```

## When to Use This Pattern

- Production projects
- Team collaboration
- Complex multi-phase work
