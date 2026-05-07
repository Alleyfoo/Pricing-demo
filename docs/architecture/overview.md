# Architecture Overview

This repository is intentionally small. The app is a Streamlit prototype that demonstrates operating workflows, not a production data platform.

## Runtime Shape

```text
Synthetic demo data
        ↓
Validation and scoring helpers
        ↓
Streamlit tabs
        ↓
Charts, queues, tables, and JSON payloads
```

Most implementation lives in [../../app.py](../../app.py). The app builds synthetic datasets in memory, computes pricing and product-operation signals, and renders them as business-facing tabs.

## Main Areas

| Area | Purpose |
|------|---------|
| Quote pricing | Service quote recommendation, pricing drivers, market signal, and review rule |
| Product setup | Product-channel price, validity, and margin checks |
| Product health | Description quality, returns/refunds, obsolete stock, scrap candidates, and margin leakage |
| Governance | Reference-data contradictions, launch readiness, cost-change review, replacement mapping, and ownership |
| Buckets | A/B/C/D inventory velocity classification |
| Stock forecast | Demand forecast, projected stock, reorder risk, and replenishment queue |
| Handoff | JSON payloads that demonstrate workflow integration points |

## Data Approach

All data is synthetic and generated inside the app. This keeps the demo portable and safe to run without credentials or source-system access.

In a production version, the synthetic data builders would be replaced by governed inputs from systems such as:

- CRM or quoting tools
- ERP and cost history
- PIM or product master
- supplier files
- inventory and demand history
- returns and refund data
- workflow or ticketing systems

## Scaling Boundary

The prototype is best framed as a daily operating cockpit. It can prove which exceptions matter and which workflows are useful.

Scaling it would be a separate architecture topic involving:

- scheduled pipelines,
- data ownership and quality rules,
- access control,
- audit logs,
- approval workflows,
- production APIs,
- and integration back to source systems.

## Verification

Use this for a basic code check:

```powershell
python -m py_compile app.py
```

When the app is running, a local smoke check should return HTTP `200`:

```powershell
(Invoke-WebRequest -Uri http://localhost:8501 -UseBasicParsing -TimeoutSec 20).StatusCode
```
