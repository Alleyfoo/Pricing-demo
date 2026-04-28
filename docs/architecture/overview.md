# System Architecture

> High-level design of Pricing Demo.

## Overview

Pricing Demo uses a **data-driven, schema-led architecture** with these layers:

```
Input → Normalization → Planning → Execution → Output → Audit
```

## Layers

### 1. Input Layer
Validates external input against `input.schema.json`.

- CLI arguments
- API requests
- File imports

### 2. Normalization Layer
Resolves defaults, expands aliases, removes ambiguity.

Output: `normalized_request.schema.json` compliant object

### 3. Planning Layer
Converts request into execution plan.

Output: `plan.schema.json` compliant plan

### 4. Execution Layer
Runs the plan, produces results.

### 5. Output Layer
Formats and validates final output against `output.schema.json`.

### 6. Audit Layer
Captures what happened for reproducibility.

Output: `run.schema.json` compliant artifact bundle

## Data Flow

```
┌─────────┐     ┌─────────────┐     ┌─────────┐     ┌───────────┐
│  Input  │────▶│ Normalized  │────▶│  Plan   │────▶│ Execution │
│         │     │   Request   │     │         │     │           │
└─────────┘     └─────────────┘     └─────────┘     └─────┬─────┘
     │                                                    │
     │              ┌──────────────┐                      │
     └─────────────▶│  Validation  │◀─────────────────────┘
                    │   (schema)   │
                    └──────────────┘
                                          │
                                          ▼
                                    ┌─────────┐
                                    │ Output  │
                                    │   +     │────▶ User
                                    │  Audit  │
                                    └─────────┘
```

## Key Principles

1. **Schema boundaries:** Every layer has a defined JSON Schema contract
2. **Validation at boundaries:** Input, plan, and output are validated
3. **Immutable artifacts:** Each stage produces auditable artifacts
4. **Failure isolation:** Invalid input never reaches execution

## Directory Structure

```
pricing-tool-demo/
├── input/              # Input validation
├── normalization/      # Request resolution
├── planning/           # Plan generation
├── execution/          # Core logic
├── output/             # Result formatting
└── audit/              # Run recording
```

## Schemas

Located in `/schemas/`:

| Schema | Purpose |
|--------|---------|
| `input.schema.json` | Public API surface |
| `normalized_request.schema.json` | Internal canonical form |
| `plan.schema.json` | Execution plan |
| `output.schema.json` | User-visible results |
| `run.schema.json` | Audit bundle |

## Extension Points

- **Input adapters:** Add new input types (webhook, file watcher)
- **Plan strategies:** Alternative planning algorithms
- **Output formats:** Add serialization formats

## Technology Choices

- **Schemas:** JSON Schema (language-agnostic)
- **Validation:** jsonschema (Python), ajv (TypeScript), etc.
- **Persistence:** CSV + Markdown for project state, JSON for artifacts
- **Optional:** SQLite for complex relational state
