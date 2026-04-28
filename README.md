# Pricing Demo (Synthetic)

Proof-of-concept Streamlit app that goes end-to-end from synthetic historical project data to a price suggestion tool.

## What this demonstrates
- Synthetic project history generation with realistic pricing patterns.
- Exploratory analysis (distribution, correlations, outliers, trend).
- Interpretable ML model that suggests a low/mid/high price band.
- Streamlit UI for practical use by sales/pre-sales users.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Notes
- Data is synthetic by design.
- Model is intentionally simple and interpretable (gradient boosting + feature importance).
