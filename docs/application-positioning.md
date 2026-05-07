# Application Positioning

## Prototype framing

This is a Streamlit prototype for service pricing and product operations. It is not a production pricing engine, customs classifier, ERP replacement, or full enterprise data-governance platform.

The purpose is to show how a focused operating tool could help pricing, product, and campaign teams work through daily exceptions: quote recommendations, product setup issues, product health risks, governance conflicts, inventory buckets, and stock readiness. The app now opens on an Overview tab so the audience understands the cockpit before diving into any single workflow.

## What the prototype demonstrates

- Service quote automation from structured job inputs.
- An overview landing tab that explains the cockpit purpose, scope, tab map, and suggested demo path.
- Transparent pricing drivers: service type, region, season, complexity, materials, labour, risk, margin, and market pressure.
- A synthetic historical-data model combined with rule-based costing.
- Product pricing setup checks before catalog or campaign publishing.
- Product health queues for description quality, returns, refunds, obsolete stock, scrap candidates, and margin leakage.
- Product data governance checks where classification-style reference data is used to detect contradictions in local master data.
- Inventory velocity buckets for A fast movers, B steady movers, C slow movers, and D stale stock.
- Stock forecasting and replenishment review.
- JSON handoff payloads that show how exceptions could move into workflow tools.

## Suggested wording

I built a small Streamlit prototype to demonstrate how pricing and product operations could work as a daily operating cockpit. The point is not to calculate real prices or solve every data-governance problem. The point is to show the structure: which data is needed, which exceptions matter, how business rules can be made visible, and how an output could move into an approval or automation flow.

The service-pricing part combines two views. First, synthetic historical service-job data creates a price band. Second, transparent rule-based costing calculates a service estimate from labour, materials, complexity, risk, region, season, and margin. The final recommendation blends those views and flags cases for manual review.

The product-management part extends the same idea beyond pricing. It shows setup checks, product health, data-governance conflicts, inventory buckets, stock readiness, and workflow payloads. It is intentionally framed as an operating layer: useful for campaigns, category reviews, and daily exception handling, while larger-scale data integration remains a separate implementation topic.

## Data governance framing

The governance tab uses HS-style reference fields as validation signals, not as legally binding customs classification. For example, if a reference class implies a steel mounting article but the local product master says unknown material, missing origin, or an inconsistent unit of measure, the product is flagged for review.

This keeps the demo credible: it highlights contradictions and ownership gaps without claiming to automate specialist customs decisions.

## Honest caveats

- All historical, product, inventory, supplier, returns, and governance data is synthetic.
- The model demonstrates structure and workflow, not operational pricing accuracy.
- Product classification references are illustrative and should not be treated as customs advice.
- The pricing and product rules are simplified for a prototype.
- Production use would require real source systems, access controls, approval rules, audit logs, data quality ownership, and integration design.
- Scaling this beyond a focused operating cockpit is a separate architecture and data-platform discussion.

## Avoid saying

- It predicts real prices.
- It automatically classifies products for customs or tariff purposes.
- The machine-learning model is the main value by itself.
- The prototype replaces pricing, product, sales, supply-chain, or compliance expertise.
- It is a finished production system.
- The work is only a dashboard.

## Strong emphasis

The relevant point is business usability. A pricing or product manager needs to see where the data comes from, what drives the result, which exceptions matter today, who owns the next action, and how the output becomes part of a working quotation, campaign, catalog, or product-governance process.
