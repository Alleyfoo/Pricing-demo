# Project Memory

> Curated knowledge base for Pricing Demo.

## Purpose

Memory docs are **lookup surfaces**, not mandatory startup reading. They capture:

- Decisions and their context
- Patterns and conventions
- Known issues and workarounds
- Domain knowledge

## Organization

```
docs/memory/
├── README.md          # This file
├── INDEX.md           # Topic navigation (if memory_mode: index)
├── decisions/         # ADRs and decision records
├── patterns/          # Reusable patterns
├── known-issues/      # Bugs and workarounds
└── domain/            # Domain knowledge
```

## Adding Memory

1. Create file in appropriate subdirectory
2. Use date prefix for decisions: `2024-01-15-database-choice.md`
3. Link from INDEX.md if using index mode
4. Cross-reference from task files when relevant

## Memory vs Tasks

| | Memory | Tasks |
|--|--------|-------|
| **Content** | Knowledge, decisions, patterns | Work to do, work done |
| **Lifetime** | Long-term, evolves | Short-term, completes |
| **Scope** | Cross-cutting | Specific deliverable |
| **Format** | Narrative, reference | Structured, actionable |

## Usage for AI Assistants

- Check `memory/INDEX.md` when investigating a topic
- Read specific memory files, not the whole directory
- Add to memory when you learn something that will help future sessions
- Link memory files from task notes for context

## Example Memory Files

```markdown
# docs/memory/decisions/2024-01-15-database-choice.md

## Decision
Use SQLite for local storage.

## Context
Needed single-file, zero-config database.
Considered: SQLite, JSON files, CSV.

## Consequences
- Easy backup (single file)
- Limited concurrency (acceptable for desktop tool)
- Migration path: future versions can add Postgres adapter
```

```markdown
# docs/memory/patterns/schema-evolution.md

## Pattern
Version schemas in filenames: `input-v1.schema.json`

## Rationale
Allows backward compatibility without breaking existing data.

## Usage
- New features: bump minor version
- Breaking changes: bump major version, keep old schema alongside
```

## Maintenance

- Review annually for stale content
- Mark deprecated patterns with `> DEPRECATED: use X instead`
- Archive obsolete files to `docs/memory/archive/`
