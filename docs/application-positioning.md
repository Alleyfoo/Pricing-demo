# Caverion Application Positioning

## Prototype framing

This prototype is a service-pricing automation concept. It is not a product-price calculator and it does not attempt to predict real Caverion prices.

The purpose is to show a practical way to structure service quote automation: connect relevant data, expose pricing drivers, combine historical reference data with transparent rule-based costing, and prepare the result for automation or manual review.

## What the prototype demonstrates

- Service quote automation from structured job inputs.
- Data structures for service type, region, season, complexity, materials, labour hours, historical outcome, and quote result.
- Pricing drivers that can be inspected instead of hidden behind a black box.
- Transparent calculation logic using labour, materials, risk, regional factors, seasonality, complexity, and margin.
- Historical data and rule-based costing used together.
- JSON handoff for Power Automate, n8n, Azure Functions, or a manual review queue.
- Manual review rules when the recommendation differs materially from the historical model or rule-based estimate.
- A business-facing workflow that sales or bid teams could understand and improve.

## Suggested wording

I built a small prototype to demonstrate how service quote automation could work in practice. The idea is not to calculate real Caverion prices, but to show the structure: what data is needed, how pricing drivers can be made visible, and how a quote recommendation could move into an automation flow.

The prototype combines two views. First, it uses synthetic historical service-job data to show how previous jobs could inform a price band. Second, it uses a transparent rule-based service calculation with labour, material costs, complexity, risk, region, season, and margin. The final recommendation blends those views and flags cases for manual review when the result needs human judgement.

I also included a JSON handoff concept, because the value is not only in the calculation. The result needs to move into a practical process: quote drafting, sales review, approval, and feedback back into the data model. That reflects how I would approach pricing and cloud automation work: start from the business process, structure the data, build a transparent model, automate the repeatable parts, and leave clear review points where judgement is needed.

## Honest caveats

- The historical data is synthetic.
- The model demonstrates structure and workflow, not actual pricing accuracy.
- The pricing logic is intentionally simplified for a prototype.
- It should be adapted to real data sources, approval rules, and commercial logic before operational use.
- My pricing experience is developing through practical modelling, data analysis, and automation work rather than from a previous formal pricing-specialist role.

## Avoid saying

- It predicts real Caverion prices.
- The machine learning model is the main value by itself.
- The prototype replaces pricing expertise or sales judgement.
- It is a finished production pricing engine.
- The work is mainly a software demo.

## Strong emphasis

The relevant point is business usability: a pricing specialist needs to understand where the data comes from, what drives the result, which rules are transparent, which cases need manual review, and how the output becomes part of a working sales and quotation process.
