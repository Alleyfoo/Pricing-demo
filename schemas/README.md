# Schema System

> JSON Schema data contracts for Pricing Demo.

## Purpose

Schemas define the **shape of data** at system boundaries:

- Input validation
- Internal representations
- Output contracts
- Audit trails

## Schema Chain

```
Input → Normalized Request → Plan → Output → Run (Audit)
```

| Schema | Stage | Purpose |
|--------|-------|---------|
| `input.schema.json` | Entry | Public API surface, user input |
| `normalized_request.schema.json` | Internal | Canonical form, defaults applied |
| `plan.schema.json` | Planning | Execution strategy, work slices |
| `output.schema.json` | Exit | User-visible results |
| `run.schema.json` | Audit | Complete execution record |

## Using Schemas

### Python

```python
import json
import jsonschema

with open("schemas/input.schema.json") as f:
    schema = json.load(f)

# Validate
data = {"request_id": "req-123", "source": "cli", "payload": {}}
jsonschema.validate(data, schema)  # Raises ValidationError if invalid
```

### TypeScript

```typescript
import Ajv from "ajv";

const ajv = new Ajv();
const schema = require("./schemas/input.schema.json");
const validate = ajv.compile(schema);

const valid = validate(data);
if (!valid) console.log(validate.errors);
```

## Schema Versioning

- Major changes: `input-v2.schema.json` alongside `input.schema.json`
- Minor changes: Add optional fields (backward compatible)
- Breaking changes: Bump major version, keep old schema for compatibility

## Customization

Replace `pricing-tool-demo` in `$id` fields with your actual project identifier:

```json
"$id": "https://my-project.local/schemas/input.schema.json"
```
