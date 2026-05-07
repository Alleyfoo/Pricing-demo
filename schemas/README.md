# Schemas

This directory contains JSON Schema files that came from the project scaffold and can be used for future workflow or API contracts.

They are not currently required by the Streamlit app runtime. The app runs from [../app.py](../app.py) and generates synthetic demo data in memory.

## Files

| Schema | Intended use |
|--------|--------------|
| `input.schema.json` | Shape for a future external request payload |
| `normalized_request.schema.json` | Canonical internal request shape |
| `plan.schema.json` | Execution or workflow plan shape |
| `output.schema.json` | Result payload shape |
| `run.schema.json` | Audit/run metadata shape |

## Notes

If this prototype is later turned into an integrated service, these schemas can be revised around the real API and workflow boundaries. Until then, they are supporting project artifacts rather than the core app architecture.
