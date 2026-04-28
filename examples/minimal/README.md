# Minimal Example

> Smallest functional use of the agentic scaffold.

## Files

```
minimal/
├── README.md
├── docs/
│   └── project/
│       ├── tracker_active.csv
│       └── tasks/
│           └── _template.md
└── scripts/
    └── tracker.py
```

## What This Demonstrates

- Single task creation
- Basic workflow without memory, schemas, or advanced features
- Minimal viable scaffold usage

## Usage

```bash
# Create a task
python scripts/tracker.py new FEAT-001 "My first feature"

# List open tasks
python scripts/tracker.py open
```

## When to Use This Pattern

- Quick prototypes
- Small personal projects
- Learning the scaffold
