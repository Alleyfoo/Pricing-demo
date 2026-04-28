import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder

st.set_page_config(page_title="Pricing Demo", page_icon="💸", layout="wide")


@dataclass
class PriceModels:
    preprocessor: ColumnTransformer
    mid_model: GradientBoostingRegressor
    low_model: GradientBoostingRegressor
    high_model: GradientBoostingRegressor


@dataclass
class CatalogPrice:
    subtotal: float
    regional_adjustment: float
    seasonal_adjustment: float
    complexity_premium: float
    risk_buffer: float
    margin: float
    total: float


REGION_MULTIPLIERS = {
    "Northeast": 1.15,
    "Southeast": 0.95,
    "Midwest": 1.00,
    "Southwest": 1.02,
    "West": 1.20,
}

SEASON_MULTIPLIERS = {
    "Winter": 1.03,
    "Spring": 1.00,
    "Summer": 1.07,
    "Fall": 0.98,
}


def build_price_catalog() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "job_type": "Electrical",
                "base_fee": 950,
                "hourly_rate": 118,
                "material_markup": 1.22,
                "risk_rate": 0.07,
            },
            {
                "job_type": "Plumbing",
                "base_fee": 900,
                "hourly_rate": 112,
                "material_markup": 1.20,
                "risk_rate": 0.06,
            },
            {
                "job_type": "HVAC",
                "base_fee": 1250,
                "hourly_rate": 124,
                "material_markup": 1.24,
                "risk_rate": 0.08,
            },
            {
                "job_type": "Renovation",
                "base_fee": 1600,
                "hourly_rate": 132,
                "material_markup": 1.18,
                "risk_rate": 0.11,
            },
            {
                "job_type": "Landscaping",
                "base_fee": 760,
                "hourly_rate": 105,
                "material_markup": 1.17,
                "risk_rate": 0.05,
            },
        ]
    )


def calculate_catalog_price(
    catalog: pd.DataFrame,
    job_type: str,
    region: str,
    season: str,
    complexity: float,
    materials: float,
    labour: float,
    target_margin: float,
) -> CatalogPrice:
    item = catalog.loc[catalog["job_type"] == job_type].iloc[0]
    base_and_work = (
        item["base_fee"] + materials * item["material_markup"] + labour * item["hourly_rate"]
    )
    regional_adjustment = base_and_work * (REGION_MULTIPLIERS[region] - 1)
    seasonal_adjustment = base_and_work * (SEASON_MULTIPLIERS[season] - 1)
    complexity_premium = base_and_work * max(complexity - 5, 0) * 0.035
    risk_buffer = base_and_work * item["risk_rate"] * (1 + complexity / 12)
    subtotal = (
        base_and_work
        + regional_adjustment
        + seasonal_adjustment
        + complexity_premium
        + risk_buffer
    )
    margin = subtotal * target_margin
    return CatalogPrice(
        subtotal=float(subtotal),
        regional_adjustment=float(regional_adjustment),
        seasonal_adjustment=float(seasonal_adjustment),
        complexity_premium=float(complexity_premium),
        risk_buffer=float(risk_buffer),
        margin=float(margin),
        total=float(subtotal + margin),
    )


def build_data_source_map() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Source": "CRM opportunities",
                "Pricing use": "Win/loss, customer segment, quote stage",
                "Quality check": "Missing close reasons and stale stages",
                "Automation target": "Salesforce/Dynamics export or API",
            },
            {
                "Source": "ERP/project history",
                "Pricing use": "Actual materials, hours, delivered margin",
                "Quality check": "Project codes and cost category mapping",
                "Automation target": "Scheduled Azure Data Factory load",
            },
            {
                "Source": "Price catalog",
                "Pricing use": "Base fees, labour rates, markup rules",
                "Quality check": "Owner, validity date, approval status",
                "Automation target": "SharePoint/List/SQL controlled table",
            },
            {
                "Source": "Supplier costs",
                "Pricing use": "Material price movements and availability",
                "Quality check": "Currency, effective date, duplicate SKUs",
                "Automation target": "n8n webhook or vendor file drop",
            },
            {
                "Source": "Sales feedback",
                "Pricing use": "Override reasons and competitor pressure",
                "Quality check": "Free-text normalization",
                "Automation target": "Power Automate approval loop",
            },
        ]
    )


def automation_payload(
    job_type: str,
    region: str,
    season: str,
    complexity: float,
    materials: float,
    labour: float,
    low: float,
    mid: float,
    high: float,
    catalog_price: CatalogPrice,
    recommended_price: float,
    automation_target: str,
) -> dict:
    return {
        "quote_request": {
            "job_type": job_type,
            "region": region,
            "season": season,
            "complexity_score": round(complexity, 1),
            "material_cost": materials,
            "labour_hours": labour,
        },
        "pricing_result": {
            "ml_band": {
                "low_p15": round(low, 2),
                "mid": round(mid, 2),
                "high_p85": round(high, 2),
            },
            "catalog_total": round(catalog_price.total, 2),
            "recommended_price": round(recommended_price, 2),
            "review_required": abs(recommended_price - mid) / max(mid, 1) > 0.18,
        },
        "handoff": {
            "target": automation_target,
            "next_step": "Create quote draft and route for sales review",
        },
    }


def generate_synthetic_data(n_rows: int = 900, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    job_types = ["Electrical", "Plumbing", "HVAC", "Renovation", "Landscaping"]
    regions = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]
    seasons = ["Winter", "Spring", "Summer", "Fall"]

    dates = pd.date_range("2022-01-01", "2025-12-31", freq="D")

    rows = []
    for _ in range(n_rows):
        job_type = rng.choice(job_types)
        region = rng.choice(regions)
        complexity = np.clip(rng.normal(5.5, 2.0), 1, 10)
        material_cost = np.clip(rng.normal(2500, 1400), 300, 12000)

        base_hours = {
            "Electrical": 32,
            "Plumbing": 28,
            "HVAC": 36,
            "Renovation": 52,
            "Landscaping": 24,
        }[job_type]

        labour_hours = np.clip(
            rng.normal(base_hours + complexity * 3.5 + material_cost / 500, 8), 6, 280
        )

        date = rng.choice(dates)
        month = pd.Timestamp(date).month
        if month in [12, 1, 2]:
            season = "Winter"
        elif month in [3, 4, 5]:
            season = "Spring"
        elif month in [6, 7, 8]:
            season = "Summer"
        else:
            season = "Fall"

        region_multiplier = REGION_MULTIPLIERS[region]
        season_multiplier = SEASON_MULTIPLIERS[season]

        complexity_multiplier = 1 + (complexity - 5) * 0.06
        trend_multiplier = 1 + (pd.Timestamp(date).year - 2022) * 0.04

        raw_price = (
            1200
            + material_cost * 1.18
            + labour_hours * 115
            + complexity * 450
        )
        noisy_price = raw_price * region_multiplier * season_multiplier * complexity_multiplier * trend_multiplier
        final_price = max(800, noisy_price + rng.normal(0, 2500))

        price_position = final_price / (material_cost + labour_hours * 90 + 1000)
        win_probability = 1 / (1 + math.exp((price_position - 2.2) * 1.5))
        win_probability = np.clip(win_probability + rng.normal(0, 0.08), 0.03, 0.97)
        won = rng.random() < win_probability

        rows.append(
            {
                "date": pd.Timestamp(date),
                "job_type": job_type,
                "region": region,
                "complexity_score": round(float(complexity), 2),
                "material_cost": round(float(material_cost), 2),
                "labour_hours": round(float(labour_hours), 1),
                "season": season,
                "final_price": round(float(final_price), 2),
                "won": int(won),
            }
        )

    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def build_models(df: pd.DataFrame) -> PriceModels:
    X = df[["job_type", "region", "complexity_score", "material_cost", "labour_hours", "season"]]
    y = df["final_price"]

    categorical = ["job_type", "region", "season"]
    numeric = ["complexity_score", "material_cost", "labour_hours"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("num", "passthrough", numeric),
        ]
    )

    X_t = preprocessor.fit_transform(X)

    mid_model = GradientBoostingRegressor(random_state=42)
    low_model = GradientBoostingRegressor(loss="quantile", alpha=0.15, random_state=42)
    high_model = GradientBoostingRegressor(loss="quantile", alpha=0.85, random_state=42)

    mid_model.fit(X_t, y)
    low_model.fit(X_t, y)
    high_model.fit(X_t, y)

    return PriceModels(preprocessor=preprocessor, mid_model=mid_model, low_model=low_model, high_model=high_model)


def detect_outliers(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby(["job_type", "region"])["final_price"]
    stats = grp.agg(group_mean="mean", group_std="std").reset_index()
    merged = df.merge(stats, on=["job_type", "region"], how="left")
    merged["z_score"] = (merged["final_price"] - merged["group_mean"]) / merged["group_std"].replace(0, np.nan)
    return merged[(merged["z_score"].abs() > 2.5)].sort_values("z_score", key=np.abs, ascending=False)


def feature_importance_frame(models: PriceModels) -> pd.DataFrame:
    names = models.preprocessor.get_feature_names_out()
    importance = models.mid_model.feature_importances_
    fi = pd.DataFrame({"feature": names, "importance": importance}).sort_values("importance", ascending=False)
    return fi.head(12)


def predict_band(models: PriceModels, row: pd.DataFrame):
    x_t = models.preprocessor.transform(row)
    low = float(models.low_model.predict(x_t)[0])
    mid = float(models.mid_model.predict(x_t)[0])
    high = float(models.high_model.predict(x_t)[0])

    if low > high:
        low, high = high, low
    mid = np.clip(mid, low, high)
    return low, mid, high


def main():
    st.title("💸 Pricing Demo — Synthetic Historical to Price Suggestion")
    st.caption("Proof-of-thinking app: synthetic data → analysis → interpretable suggested price band")

    st.sidebar.header("New Job Inputs")
    row_count = st.sidebar.slider("Synthetic historical rows", min_value=500, max_value=1000, value=900, step=50)

    df = generate_synthetic_data(n_rows=row_count)
    models = build_models(df)

    job_type = st.sidebar.selectbox("Job Type", sorted(df["job_type"].unique()))
    region = st.sidebar.selectbox("Region", sorted(df["region"].unique()))
    complexity = st.sidebar.slider("Complexity", min_value=1.0, max_value=10.0, value=5.5, step=0.1)
    materials = st.sidebar.number_input("Materials Estimate ($)", min_value=200, max_value=20000, value=3000, step=100)
    labour = st.sidebar.slider("Labour Hours", min_value=4, max_value=300, value=40, step=1)
    season = st.sidebar.selectbox("Season", ["Winter", "Spring", "Summer", "Fall"])
    target_margin = st.sidebar.slider("Target Margin", min_value=0.05, max_value=0.35, value=0.18, step=0.01)
    automation_target = st.sidebar.selectbox(
        "Automation Target",
        ["Power Automate", "n8n", "Azure Function", "Manual review queue"],
    )

    input_row = pd.DataFrame(
        [
            {
                "job_type": job_type,
                "region": region,
                "complexity_score": complexity,
                "material_cost": materials,
                "labour_hours": labour,
                "season": season,
            }
        ]
    )

    low, mid, high = predict_band(models, input_row)
    catalog = build_price_catalog()
    catalog_price = calculate_catalog_price(
        catalog,
        job_type,
        region,
        season,
        complexity,
        materials,
        labour,
        target_margin,
    )
    recommended_price = (mid * 0.65) + (catalog_price.total * 0.35)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Price Suggestion",
            "Data Foundation",
            "Historical Analysis",
            "Why This Price",
            "Automation Plan",
        ]
    )

    with tab1:
        st.subheader("Suggested Price Band")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Low (P15)", f"${low:,.0f}")
        c2.metric("Mid", f"${mid:,.0f}")
        c3.metric("High (P85)", f"${high:,.0f}")
        c4.metric("Recommended", f"${recommended_price:,.0f}")

        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=mid,
                number={"prefix": "$", "valueformat": ",.0f"},
                gauge={
                    "axis": {"range": [low * 0.85, high * 1.15]},
                    "steps": [
                        {"range": [low, mid], "color": "#b6e3ff"},
                        {"range": [mid, high], "color": "#9bd7ff"},
                    ],
                    "threshold": {"line": {"color": "#0a66c2", "width": 4}, "value": mid},
                },
                title={"text": "Recommended Mid Price"},
            )
        )
        st.plotly_chart(gauge, width="stretch")

        st.subheader("Catalog build-up")
        breakdown = pd.DataFrame(
            [
                {"Component": "Catalog subtotal", "Amount": catalog_price.subtotal},
                {"Component": "Regional adjustment", "Amount": catalog_price.regional_adjustment},
                {"Component": "Seasonal adjustment", "Amount": catalog_price.seasonal_adjustment},
                {"Component": "Complexity premium", "Amount": catalog_price.complexity_premium},
                {"Component": "Risk buffer", "Amount": catalog_price.risk_buffer},
                {"Component": "Target margin", "Amount": catalog_price.margin},
            ]
        )
        fig_breakdown = px.bar(
            breakdown,
            x="Component",
            y="Amount",
            title="Transparent catalog calculation behind the recommendation",
        )
        st.plotly_chart(fig_breakdown, width="stretch")
        st.dataframe(catalog, width="stretch", hide_index=True)

    with tab2:
        st.subheader("Data sources and pricing logic")
        st.dataframe(build_data_source_map(), width="stretch", hide_index=True)

        source_scores = pd.DataFrame(
            [
                {"Area": "Availability", "Score": 82},
                {"Area": "Joinability", "Score": 68},
                {"Area": "Freshness", "Score": 74},
                {"Area": "Business ownership", "Score": 61},
                {"Area": "Automation readiness", "Score": 70},
            ]
        )
        fig_scores = px.line_polar(
            source_scores,
            r="Score",
            theta="Area",
            line_close=True,
            range_r=[0, 100],
            title="Data readiness snapshot",
        )
        fig_scores.update_traces(fill="toself")
        st.plotly_chart(fig_scores, width="stretch")

        st.markdown(
            """
            **Practical next step:** connect opportunity, delivered-cost, and catalog data around one shared key:
            quote or project ID. That makes the model auditable enough for sales use and structured enough for
            automation.
            """
        )

    with tab3:
        st.subheader("Historical Pricing Analysis")

        fig_dist = px.box(
            df,
            x="job_type",
            y="final_price",
            color="region",
            title="Distribution of Final Prices by Job Type and Region",
        )
        st.plotly_chart(fig_dist, width="stretch")

        corr_df = df.copy()
        corr_df["month"] = corr_df["date"].dt.month
        corr_encoded = pd.get_dummies(corr_df[["complexity_score", "material_cost", "labour_hours", "final_price", "won", "month", "job_type", "region", "season"]], drop_first=True)
        corr = corr_encoded.corr(numeric_only=True)[["final_price"]].sort_values("final_price", ascending=False)
        st.dataframe(corr.style.background_gradient(cmap="Blues"), width="stretch")

        outliers = detect_outliers(df)
        st.markdown("**Outliers (|z-score| > 2.5 within job type + region groups)**")
        st.dataframe(outliers[["date", "job_type", "region", "final_price", "group_mean", "z_score"]].head(20), width="stretch")

        trend = df.set_index("date").resample("ME")["final_price"].mean().reset_index()
        fig_trend = px.line(trend, x="date", y="final_price", title="Average Price Evolution Over Time")
        st.plotly_chart(fig_trend, width="stretch")

    with tab4:
        st.subheader("Why this suggested price?")
        fi = feature_importance_frame(models)

        fig_fi = px.bar(fi.sort_values("importance"), x="importance", y="feature", orientation="h", title="Model Feature Importance (Mid Model)")
        st.plotly_chart(fig_fi, width="stretch")

        st.markdown(
            """
            **Interpretation notes:**
            - Numeric drivers like `material_cost`, `labour_hours`, and `complexity_score` usually dominate.
            - Categorical context (job type, region, season) adjusts the recommendation.
            - Band range (P15 to P85) communicates uncertainty to help sales choose aggressive vs conservative quotes.
            """
        )

        comparison = pd.DataFrame(
            [
                {"Signal": "ML mid price", "Amount": mid},
                {"Signal": "Catalog rule price", "Amount": catalog_price.total},
                {"Signal": "Blended recommendation", "Amount": recommended_price},
            ]
        )
        st.dataframe(comparison, width="stretch", hide_index=True)

    with tab5:
        st.subheader("Automation handoff")
        payload = automation_payload(
            job_type,
            region,
            season,
            complexity,
            materials,
            labour,
            low,
            mid,
            high,
            catalog_price,
            recommended_price,
            automation_target,
        )
        p1, p2, p3 = st.columns(3)
        p1.metric("Target", automation_target)
        p2.metric("Review required", "Yes" if payload["pricing_result"]["review_required"] else "No")
        p3.metric("Quote draft", f"${recommended_price:,.0f}")

        process = pd.DataFrame(
            [
                {"Step": 1, "Stage": "Collect", "Owner": "CRM/ERP", "Output": "Normalized quote request"},
                {"Step": 2, "Stage": "Price", "Owner": "Pricing model", "Output": "ML band + catalog price"},
                {"Step": 3, "Stage": "Review", "Owner": "Sales", "Output": "Approved or adjusted quote"},
                {"Step": 4, "Stage": "Learn", "Owner": "Analytics", "Output": "Win/loss and margin feedback"},
            ]
        )
        st.dataframe(process, width="stretch", hide_index=True)
        st.json(payload)

    with st.expander("Preview synthetic data"):
        st.dataframe(df.head(20), width="stretch")


if __name__ == "__main__":
    main()
