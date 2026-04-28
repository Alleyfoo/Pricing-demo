# BUILD-001: Assemble Pricing Demo with agentic scaffold

| Field | Value |
|-------|-------|
| Area | App |
| Type | Feature |
| Priority | Medium |
| Status | Done |
| Owner | AI |
| Created | 2026-04-28 |
| Completed | 2026-04-28 |
| Blocked By | |

## Goal

Pricing Demo is cloned into the workspace, wrapped with the agentic scaffold, dependencies install cleanly, scaffold validation passes, and the Streamlit app runs locally.

## Out of Scope

- Product feature changes beyond assembling and validating the existing demo.

## Source of Intent

- User request: take scaffolding from `https://github.com/Alleyfoo/agentic-scaffold`, pull project from `https://github.com/Alleyfoo/Pricing-demo`, and build it.

## Files

- `app.py`
- `requirements.txt`
- `README.md`
- `agent.md`
- `scaffold.yaml`
- `docs/`
- `schemas/`
- `scripts/`
- `.gitignore`

## Prior Art

- Related tasks, research, rejected approaches

## Plan

| Slice | Deliverable | Files | Verification | Exit Criteria |
|-------|-------------|-------|--------------|---------------|
| 1 | Clone Pricing Demo | Root project files | `git status --short --branch` | Project present |
| 2 | Add and configure scaffold | `agent.md`, `scaffold.yaml`, `docs/`, `schemas/`, `scripts/` | `python scripts/validate_scaffold.py` | Scaffold validates |
| 3 | Install and run app | `.venv`, `requirements.txt`, `app.py` | Streamlit endpoint check | HTTP 200 |

## Notes

Kept the Pricing Demo README as the root project README and added scaffold workflow files around it. Replaced scaffold placeholders with Pricing Demo values, removed sample test tasks, and fixed scaffold validation so JSON schema parse failures and unreplaced placeholders affect the exit code.

## Verification

Commands run:

```bash
.\.venv\Scripts\python scripts\validate_scaffold.py
@'
import app
df = app.generate_synthetic_data(50)
models = app.build_models(df)
row = df[['job_type', 'region', 'complexity_score', 'material_cost', 'labour_hours', 'season']].head(1)
print(df.shape)
print(tuple(round(x, 2) for x in app.predict_band(models, row)))
'@ | .\.venv\Scripts\python -
Invoke-WebRequest -UseBasicParsing http://localhost:8501 -TimeoutSec 10
```

```
Scaffold validation: [PASS]
Smoke test: (50, 9), prediction band produced
Streamlit endpoint: HTTP 200
```

## Review Checklist

- [x] Implementation complete
- [x] Source of intent linked
- [x] Tests passing
- [x] Source check: ORIGINAL
- [x] Reviewer verdict: PASS
- [x] Regression hunter: LOW
- [x] Final status updated in tracker_active.csv
