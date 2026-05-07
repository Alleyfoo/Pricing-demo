# Getting Started

This project is a Streamlit demo for service pricing and product operations.

## Prerequisites

- Python 3.11+
- PowerShell
- Git

## Run Locally

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## What To Review In The App

1. **Overview**: cockpit purpose, summary metrics, tab map, scope, and suggested demo path.
2. **Quote**: blended service-pricing recommendation and review flag.
3. **Data**: source-system and data-quality map.
4. **Product Check**: product-channel pricing setup validation.
5. **Product Health**: catalog quality, returns/refunds, obsolete stock, scrap candidates, and margin leakage.
6. **Governance**: classification-informed product-master contradictions, launch readiness, cost changes, and replacement gaps.
7. **Buckets**: A/B/C/D inventory velocity buckets.
8. **Stock Forecast**: projected demand and replenishment queue.
9. **Handoff**: JSON payload and simulated automation acknowledgement.

## Verification

Basic syntax check:

```powershell
python -m py_compile app.py
```

Basic local smoke check after starting Streamlit:

```powershell
(Invoke-WebRequest -Uri http://localhost:8501 -UseBasicParsing -TimeoutSec 20).StatusCode
```

Expected result:

```text
200
```
