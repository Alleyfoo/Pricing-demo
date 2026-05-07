# Pricing And Product Operations Demo

This is a Streamlit prototype for service pricing and product-management operations. It opens with an overview of the operating cockpit, then shows how quote recommendations, product setup checks, product health, data governance, inventory buckets, stock forecasting, and workflow handoffs could sit together.

The app uses synthetic data by design. It is not a real pricing engine, customs classifier, ERP/PIM replacement, or production data-governance system.

## Live Demo

> **[https://pricing-demo-tqkkfbfbw8p7unffnfgjft.streamlit.app](https://pricing-demo-tqkkfbfbw8p7unffnfgjft.streamlit.app)**

## What It Shows

- **Overview**: purpose of the cockpit, summary metrics, tab map, scope, and suggested demo path.
- **Quote**: recommended service quote from a blended historical-data model, transparent catalog calculation, and synthetic market signal.
- **Data**: source-system map, data quality checks, and automation targets.
- **History**: synthetic historical quotes, outlier checks, and price trends.
- **Why**: model drivers and pricing rationale.
- **Product Check**: price, validity-window, channel, and margin checks before publishing product pricing.
- **Product Health**: master-data quality, returns/refunds, obsolete stock, scrap candidates, and margin leakage.
- **Governance**: classification-informed validation that detects contradictions between reference data and local product master fields.
- **Buckets**: A/B/C/D inventory velocity buckets for fast, steady, slow, and stale stock.
- **Stock Forecast**: demand forecast, projected stock, reorder risk, and replenishment queue.
- **Handoff**: JSON payloads and simulated acknowledgement from an automation target.

## Scope

This demo is best understood as a focused operating tool:

- useful for daily exception review,
- campaign or category management,
- pricing and product workflow prototyping,
- and discussion of what should later be integrated or automated.

It is not positioned as a six-month data-platform program. A scaled production version would need governed source-system pipelines, ownership workflows, audit logs, access controls, and integrations back to ERP, PIM, CRM, inventory, returns, and ticketing systems.

## Run Locally

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Project Notes

- Data is synthetic.
- Pricing logic is simplified for demonstration.
- Classification-style product references are used only to detect data contradictions, not to provide customs advice.
- The prototype is intended to communicate practical workflow thinking, not to claim finished pricing, product-governance, or supply-chain automation.

Additional positioning notes are in [docs/application-positioning.md](docs/application-positioning.md).
