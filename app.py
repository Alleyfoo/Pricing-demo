import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

st.set_page_config(page_title="Pricing Demo", page_icon="💸", layout="wide")


@dataclass
class PriceModels:
    preprocessor: ColumnTransformer
    mid_model: GradientBoostingRegressor
    low_model: GradientBoostingRegressor
    high_model: GradientBoostingRegressor


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

        region_multiplier = {
            "Northeast": 1.15,
            "Southeast": 0.95,
            "Midwest": 1.00,
            "Southwest": 1.02,
            "West": 1.20,
        }[region]

        season_multiplier = {
            "Winter": 1.03,
            "Spring": 1.00,
            "Summer": 1.07,
            "Fall": 0.98,
        }[season]

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

    tab1, tab2, tab3 = st.tabs(["Price Suggestion", "Historical Analysis", "Why This Price"])

    with tab1:
        st.subheader("Suggested Price Band")
        c1, c2, c3 = st.columns(3)
        c1.metric("Low (P15)", f"${low:,.0f}")
        c2.metric("Mid", f"${mid:,.0f}")
        c3.metric("High (P85)", f"${high:,.0f}")

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
        st.plotly_chart(gauge, use_container_width=True)

    with tab2:
        st.subheader("Historical Pricing Analysis")

        fig_dist = px.box(
            df,
            x="job_type",
            y="final_price",
            color="region",
            title="Distribution of Final Prices by Job Type and Region",
        )
        st.plotly_chart(fig_dist, use_container_width=True)

        corr_df = df.copy()
        corr_df["month"] = corr_df["date"].dt.month
        corr_encoded = pd.get_dummies(corr_df[["complexity_score", "material_cost", "labour_hours", "final_price", "won", "month", "job_type", "region", "season"]], drop_first=True)
        corr = corr_encoded.corr(numeric_only=True)[["final_price"]].sort_values("final_price", ascending=False)
        st.dataframe(corr.style.background_gradient(cmap="Blues"), use_container_width=True)

        outliers = detect_outliers(df)
        st.markdown("**Outliers (|z-score| > 2.5 within job type + region groups)**")
        st.dataframe(outliers[["date", "job_type", "region", "final_price", "group_mean", "z_score"]].head(20), use_container_width=True)

        trend = df.set_index("date").resample("M")["final_price"].mean().reset_index()
        fig_trend = px.line(trend, x="date", y="final_price", title="Average Price Evolution Over Time")
        st.plotly_chart(fig_trend, use_container_width=True)

    with tab3:
        st.subheader("Why this suggested price?")
        fi = feature_importance_frame(models)

        fig_fi = px.bar(fi.sort_values("importance"), x="importance", y="feature", orientation="h", title="Model Feature Importance (Mid Model)")
        st.plotly_chart(fig_fi, use_container_width=True)

        st.markdown(
            """
            **Interpretation notes:**
            - Numeric drivers like `material_cost`, `labour_hours`, and `complexity_score` usually dominate.
            - Categorical context (job type, region, season) adjusts the recommendation.
            - Band range (P15 to P85) communicates uncertainty to help sales choose aggressive vs conservative quotes.
            """
        )

    with st.expander("Preview synthetic data"):
        st.dataframe(df.head(20), use_container_width=True)


if __name__ == "__main__":
    main()
