# Service Pricing Automation Prototype

This is a Streamlit prototype for a service-pricing automation concept. It is built as a practical proof point for a Pricing & Cloud Automation Specialist application: how service quote data could be structured, calculated, reviewed, and handed off into automation.

The prototype is not a real pricing tool and does not predict actual prices. The historical data is synthetic, and the model demonstrates structure and workflow rather than operational pricing accuracy.

## Live Demo

> Deploy URL goes here after publishing to Streamlit Community Cloud.

## What It Shows

- Service quote automation from structured job inputs.
- Pricing drivers: service type, region, season, complexity, material estimate, labour hours, risk, and margin.
- Transparent rule-based service costing alongside a historical-data ML model.
- A recommended quote that blends historical reference data, calculation logic, and competitor market pricing.
- **Market Intel layer** — synthetic competitor price feed shows market position (above / at / below market) and pulls the recommendation toward market median based on a configurable weight.
- Manual review flag when model and catalog diverge by more than 18%.
- Simulated automation handoff — shows the outbound JSON payload and a mock agent acknowledgement response.
- A business-facing flow that sales and quotation teams could understand, test, and improve.

## Screenshots

Add screenshots here after running the app.

Suggested captures:

1. `docs/screenshots/price-suggestion.png` - price band, recommendation, and service calculation build-up.
2. `docs/screenshots/data-foundation.png` - data sources, quality checks, and automation targets.
3. `docs/screenshots/why-this-price.png` - pricing drivers and recommendation comparison.
4. `docs/screenshots/automation-plan.png` - JSON handoff and review rule output.

```md
![Price suggestion](docs/screenshots/price-suggestion.png)
![Data foundation](docs/screenshots/data-foundation.png)
![Why this price](docs/screenshots/why-this-price.png)
![Automation plan](docs/screenshots/automation-plan.png)
```

## How The Calculation Works

The app combines two pricing views.

First, it creates synthetic historical service-job data and trains a simple model to produce a low, mid, and high price band. This represents how historical project or quotation data could inform a pricing suggestion when real data is available.

Second, it calculates a transparent service estimate using rule-based costing:

```text
base service fee
+ materials estimate * material markup
+ labour hours * hourly rate
+ regional adjustment
+ seasonal adjustment
+ complexity premium
+ risk buffer
+ target margin
= service calculation price
```

The final recommendation blends the historical model and the rule-based service calculation. If the recommendation diverges materially from the model estimate, the app flags the quote for manual review.

## Why This Matters

The important part is not the machine learning model by itself. The value is in the operating model:

- knowing which data is needed,
- making pricing drivers visible,
- keeping calculation logic explainable,
- automating repeatable steps,
- preserving manual review where judgement is needed,
- and feeding sales outcomes back into future pricing decisions.

This matches the kind of work required in pricing and cloud automation: practical data modelling, service quote logic, workflow automation, and continuous improvement.

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

- Data is synthetic by design.
- Pricing logic is simplified for demonstration.
- The app should be connected to real CRM, ERP, project-cost, and sales-feedback data before any production use.
- The prototype is intended to communicate practical thinking around service pricing automation, not to claim finished pricing expertise or real-world price accuracy.

Additional positioning notes are in [docs/application-positioning.md](docs/application-positioning.md).
