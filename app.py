import json
import math
import time as _time
from dataclasses import dataclass

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder

st.set_page_config(page_title="Pricing Demo", layout="wide")

# ── Design system CSS ─────────────────────────────────────────────────────────
st.html(
    """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<style>
:root {
  --ink:        #0A1F24;
  --ink-2:      #122E35;
  --ink-3:      #1B3F47;
  --paper:      #F4F1EA;
  --paper-2:    #EAE5DA;
  --paper-3:    #DDD6C5;
  --teal:       #14B8A6;
  --teal-bright:#2DD4BF;
  --teal-dim:   #0F766E;
  --teal-soft:  #CCFBF1;
  --signal:     #F97316;
  --signal-soft:#FED7AA;
  --gold:       #C9A24A;
  --serif:      "Instrument Serif", "Times New Roman", serif;
  --sans:       "Geist", "Inter", system-ui, sans-serif;
  --mono:       "Geist Mono", "JetBrains Mono", ui-monospace, monospace;
}

/* ── Reset Streamlit chrome ── */
html, body {
  font-family: var(--sans) !important;
  background: var(--paper) !important;
  color: var(--ink) !important;
  -webkit-font-smoothing: antialiased;
}
.stApp { background: var(--paper) !important; }
header[data-testid="stHeader"] { background: var(--paper) !important; border-bottom: 1px solid var(--ink); }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--ink) !important;
  border-right: 1px solid var(--ink-3) !important;
}
[data-testid="stSidebar"] * { color: var(--paper) !important; font-family: var(--sans) !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  font-family: var(--mono) !important;
  font-size: 11px !important;
  font-weight: 500 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: var(--paper-3) !important;
  margin: 24px 0 8px !important;
}
[data-testid="stSidebar"] label {
  font-family: var(--sans) !important;
  font-size: 13px !important;
  color: var(--paper) !important;
}
[data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"],
[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"] {
  font-family: var(--mono) !important;
  font-size: 12px !important;
  color: var(--teal-bright) !important;
}
[data-testid="stSidebar"] .stSlider > div > div > div {
  background: var(--teal-bright) !important;
}
[data-testid="stSidebar"] select,
[data-testid="stSidebar"] input {
  background: var(--ink-2) !important;
  color: var(--paper) !important;
  border: 1px solid var(--ink-3) !important;
  border-radius: 0 !important;
  font-family: var(--sans) !important;
  font-size: 13px !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
  background: var(--ink-2) !important;
  border: 1px solid var(--ink-3) !important;
  border-radius: 0 !important;
  color: var(--paper) !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
  background: var(--ink-2) !important;
  border: 1px solid var(--ink-3) !important;
  border-radius: 0 !important;
}

/* ── Tabs (top nav) ── */
[data-testid="stTabs"] [role="tablist"] {
  border: 1px solid var(--ink) !important;
  border-radius: 0 !important;
  background: transparent !important;
  gap: 0 !important;
  padding: 0 !important;
}
[data-testid="stTabs"] [role="tab"] {
  font-family: var(--mono) !important;
  font-size: 10.5px !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  color: var(--ink) !important;
  background: transparent !important;
  border: 0 !important;
  border-right: 1px solid var(--ink) !important;
  border-radius: 0 !important;
  padding: 10px 16px !important;
}
[data-testid="stTabs"] [role="tab"]:last-child { border-right: 0 !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  background: var(--ink) !important;
  color: var(--paper) !important;
}
[data-testid="stTabs"] [role="tab"]:hover {
  background: var(--ink-3) !important;
  color: var(--paper) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none !important; }
[data-testid="stTabContent"] { padding-top: 0 !important; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
  background: var(--paper) !important;
  border: 1px solid var(--ink) !important;
  border-radius: 0 !important;
  padding: 20px 20px 16px !important;
}
[data-testid="stMetricLabel"] {
  font-family: var(--mono) !important;
  font-size: 10px !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: var(--teal-dim) !important;
}
[data-testid="stMetricValue"] {
  font-family: var(--serif) !important;
  font-size: 40px !important;
  letter-spacing: -0.03em !important;
  color: var(--ink) !important;
  line-height: 1 !important;
}
[data-testid="stMetricDelta"] { font-family: var(--mono) !important; font-size: 11px !important; }

/* ── Dataframes / tables ── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--ink) !important;
  border-radius: 0 !important;
}
[data-testid="stDataFrame"] th {
  background: var(--paper-2) !important;
  font-family: var(--mono) !important;
  font-size: 10.5px !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  color: var(--ink-3) !important;
  border-bottom: 1px solid var(--ink) !important;
}
[data-testid="stDataFrame"] td {
  font-size: 13px !important;
  border-bottom: 1px solid var(--paper-3) !important;
}

/* ── Headings in main ── */
h1 {
  font-family: var(--serif) !important;
  font-size: clamp(48px, 5.4vw, 78px) !important;
  line-height: 0.95 !important;
  letter-spacing: -0.025em !important;
  font-weight: 400 !important;
  color: var(--ink) !important;
  margin: 0 0 18px !important;
}
h1 em { font-style: italic; color: var(--teal-dim); }
h2 {
  font-family: var(--serif) !important;
  font-size: clamp(28px, 3vw, 42px) !important;
  line-height: 1 !important;
  letter-spacing: -0.02em !important;
  font-weight: 400 !important;
  color: var(--ink) !important;
}
h2 em { font-style: italic; color: var(--teal-dim); }
h3 {
  font-family: var(--serif) !important;
  font-size: 22px !important;
  font-weight: 400 !important;
  color: var(--ink) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
  border: 1px solid var(--ink) !important;
  border-radius: 0 !important;
  background: var(--paper-2) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-thumb { background: var(--ink-3); border-radius: 3px; }

/* ── Helper utility classes ── */
.eyebrow {
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ink-3);
  display: block;
  margin-bottom: 10px;
}
.eyebrow-teal { color: var(--teal-dim) !important; }
.hero-price {
  font-family: var(--serif);
  font-size: clamp(64px, 9vw, 120px);
  line-height: 0.9;
  letter-spacing: -0.05em;
  font-weight: 400;
  color: var(--ink);
  margin: 4px 0 8px;
}
.currency { font-size: 0.4em; font-style: italic; color: var(--teal-dim); vertical-align: super; margin-right: 2px; }
.cents { font-size: 0.3em; color: var(--ink-3); vertical-align: super; }
.section-dark {
  background: var(--ink);
  color: var(--paper);
  padding: 32px;
  margin: 0 -1rem;
}
.card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1px; background: var(--ink); border: 1px solid var(--ink); margin-bottom: 32px; }
.card-item { background: var(--paper); padding: 20px 18px; }
.card-item-dark { background: var(--ink-2); }
.card-num { font-family: var(--serif); font-size: 36px; line-height: 0.95; letter-spacing: -0.03em; margin: 0 0 4px; font-weight: 400; color: var(--ink); }
.card-num-dark { color: var(--paper); }
.card-sub { font-family: var(--mono); font-size: 11px; color: var(--ink-3); letter-spacing: 0.04em; }
.card-sub-dark { color: var(--paper-3); }
.waterfall-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--paper-3); font-size: 14px; }
.waterfall-row-total { border-bottom: 1px solid var(--ink); border-top: 1px solid var(--ink); padding: 16px 0; }
.waterfall-num { font-family: var(--mono); font-size: 10px; color: var(--ink-3); width: 28px; }
.waterfall-name { flex: 1; font-weight: 500; padding: 0 12px; }
.waterfall-amt { font-family: var(--mono); font-size: 13px; font-weight: 500; }
.fi-bar-wrap { display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid var(--paper-3); }
.fi-name { font-family: var(--mono); font-size: 12px; width: 220px; flex-shrink: 0; }
.fi-track { flex: 1; height: 6px; background: var(--paper-3); position: relative; overflow: hidden; }
.fi-fill { position: absolute; left: 0; top: 0; bottom: 0; background: var(--teal); }
.fi-pct { font-family: var(--mono); font-size: 12px; width: 48px; text-align: right; }
.pill { display: inline-block; font-family: var(--mono); font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; padding: 3px 8px; border-radius: 999px; }
.pill-signal { color: var(--signal); background: var(--signal-soft); }
.pill-teal { color: var(--teal-dim); background: var(--teal-soft); }
.code-block { background: var(--ink); color: var(--paper); padding: 24px 28px; font-family: var(--mono); font-size: 12.5px; line-height: 1.65; white-space: pre; overflow-x: auto; border: 1px solid var(--ink); border-radius: 0; }
.brand-mark { font-family: var(--serif); font-size: 22px; letter-spacing: -0.02em; }
.brand-mark em { color: var(--teal-bright); font-style: italic; }
.topbar-meta { font-family: var(--mono); font-size: 10px; letter-spacing: 0.06em; color: var(--ink-3); }
.dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--teal); margin-right: 5px; vertical-align: middle; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
.band-container { position: relative; height: 80px; background: linear-gradient(to right, var(--paper-3) 0%, var(--paper-3) 8%, var(--teal-soft) 22%, var(--teal) 50%, var(--teal-soft) 78%, var(--paper-3) 92%, var(--paper-3) 100%); border-top: 1px solid var(--ink); border-bottom: 1px solid var(--ink); margin: 32px 0 48px; }
</style>
"""
)


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
        item["base_fee"]
        + materials * item["material_markup"]
        + labour * item["hourly_rate"]
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
            "review_required": bool(abs(recommended_price - mid) / max(mid, 1) > 0.18),
        },
        "handoff": {
            "target": automation_target,
            "next_step": "Create quote draft and route for sales review",
        },
    }


@st.cache_data
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

        raw_price = 1200 + material_cost * 1.18 + labour_hours * 115 + complexity * 450
        noisy_price = (
            raw_price
            * region_multiplier
            * season_multiplier
            * complexity_multiplier
            * trend_multiplier
        )
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


@st.cache_data
def build_models(df: pd.DataFrame) -> PriceModels:
    X = df[
        [
            "job_type",
            "region",
            "complexity_score",
            "material_cost",
            "labour_hours",
            "season",
        ]
    ]
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

    return PriceModels(
        preprocessor=preprocessor,
        mid_model=mid_model,
        low_model=low_model,
        high_model=high_model,
    )


def detect_outliers(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby(["job_type", "region"])["final_price"]
    stats = grp.agg(group_mean="mean", group_std="std").reset_index()
    merged = df.merge(stats, on=["job_type", "region"], how="left")
    merged["z_score"] = (merged["final_price"] - merged["group_mean"]) / merged[
        "group_std"
    ].replace(0, np.nan)
    return merged[(merged["z_score"].abs() > 2.5)].sort_values(
        "z_score", key=np.abs, ascending=False
    )


def feature_importance_frame(models: PriceModels) -> pd.DataFrame:
    names = models.preprocessor.get_feature_names_out()
    importance = models.mid_model.feature_importances_
    fi = pd.DataFrame({"feature": names, "importance": importance}).sort_values(
        "importance", ascending=False
    )
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


def generate_competitor_prices(
    job_type: str, region: str, our_price: float
) -> pd.DataFrame:
    rng = np.random.default_rng(abs(hash(job_type + region)) % (2**32))
    base = our_price * rng.uniform(0.78, 1.22)
    competitors = [
        {"Competitor": "Alpha Services", "price": base * rng.uniform(0.88, 1.05)},
        {"Competitor": "Bright & Co", "price": base * rng.uniform(0.82, 1.12)},
        {"Competitor": "CoreTrade", "price": base * rng.uniform(0.90, 1.08)},
        {"Competitor": "Delta Works", "price": base * rng.uniform(0.85, 1.15)},
        {"Competitor": "Everest Field Svc", "price": base * rng.uniform(0.93, 1.10)},
    ]
    df = pd.DataFrame(competitors)
    df["price"] = df["price"].round(0)
    df["vs_us"] = ((df["price"] - our_price) / our_price * 100).round(1)
    return df


def _fmt(n: float) -> str:
    return f"${n:,.0f}"


def _signed(n: float) -> str:
    sign = "+" if n >= 0 else "−"
    return f"{sign} ${abs(n):,.0f}"


def _plotly_theme() -> dict:
    return dict(
        paper_bgcolor="#F4F1EA",
        plot_bgcolor="#F4F1EA",
        font_family="Geist, Inter, system-ui, sans-serif",
        font_color="#0A1F24",
        title_font_family="Instrument Serif, Times New Roman, serif",
        title_font_size=22,
        title_font_color="#0A1F24",
        colorway=["#14B8A6", "#0F766E", "#2DD4BF", "#CCFBF1", "#0A1F24"],
    )


def _apply_theme(fig: go.Figure, dark: bool = False) -> go.Figure:
    bg = "#0A1F24" if dark else "#F4F1EA"
    fg = "#F4F1EA" if dark else "#0A1F24"
    grid = "#1B3F47" if dark else "#DDD6C5"
    fig.update_layout(
        paper_bgcolor=bg,
        plot_bgcolor=bg,
        font_family="Geist, Inter, system-ui, sans-serif",
        font_color=fg,
        title_font_family="Instrument Serif, Times New Roman, serif",
        title_font_size=22,
        title_font_color=fg,
        margin=dict(l=40, r=20, t=48, b=40),
        xaxis=dict(
            gridcolor=grid,
            linecolor=grid,
            tickfont_family="Geist Mono, monospace",
            tickfont_size=10,
        ),
        yaxis=dict(
            gridcolor=grid,
            linecolor=grid,
            tickfont_family="Geist Mono, monospace",
            tickfont_size=10,
        ),
    )
    return fig


def main():
    # ── Sidebar ───────────────────────────────────────────────────────────────
    st.sidebar.markdown(
        '<div class="brand-mark">Pricing<em>·</em>Demo</div>'
        '<div style="font-family:var(--mono);font-size:10px;letter-spacing:0.1em;'
        "text-transform:uppercase;color:#DDD6C5;margin-top:2px;margin-bottom:18px;"
        'padding-bottom:18px;border-bottom:1px solid #1B3F47;">v0.4</div>',
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("### New Job Inputs")
    row_count = st.sidebar.slider(
        "Synthetic rows", min_value=500, max_value=1000, value=900, step=50
    )

    df = generate_synthetic_data(n_rows=row_count)
    models = build_models(df)

    job_type = st.sidebar.selectbox(
        "Job Type",
        ["Electrical", "HVAC", "Plumbing", "Renovation", "Landscaping"],
        index=1,
    )
    region = st.sidebar.selectbox(
        "Region", ["Northeast", "Southeast", "Midwest", "Southwest", "West"], index=4
    )
    season = st.sidebar.selectbox(
        "Season", ["Winter", "Spring", "Summer", "Fall"], index=2
    )
    complexity = st.sidebar.slider(
        "Complexity", min_value=1.0, max_value=10.0, value=6.5, step=0.1
    )
    materials = st.sidebar.slider(
        "Materials estimate ($)", min_value=200, max_value=20000, value=3400, step=100
    )
    labour = st.sidebar.slider(
        "Labour hours", min_value=4, max_value=300, value=52, step=1
    )
    target_margin = st.sidebar.slider(
        "Target margin",
        min_value=0.05,
        max_value=0.35,
        value=0.18,
        step=0.01,
        format="%.0f%%",
    )

    st.sidebar.markdown("### Market Intel")
    market_weight = st.sidebar.slider(
        "Competitor price weight",
        min_value=0,
        max_value=30,
        value=10,
        step=5,
        format="%d%%",
        help="How much competitor market data pulls the recommendation (0 = ignore, 30 = strong pull)",
    )

    st.sidebar.markdown("### Handoff")
    automation_target = st.sidebar.selectbox(
        "Automation target",
        ["Power Automate", "n8n", "Azure Function", "Manual review queue"],
        index=1,
    )

    st.sidebar.markdown(
        '<div style="margin-top:24px;padding-top:16px;border-top:1px solid #1B3F47;'
        'font-family:var(--mono);font-size:10px;letter-spacing:0.05em;color:#DDD6C5;line-height:1.6;">'
        f"Synthetic data · {row_count} rows<br>Last trained 04·29·2026<br>Model · GBM quantile band</div>",
        unsafe_allow_html=True,
    )

    # ── Compute ───────────────────────────────────────────────────────────────
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
        catalog, job_type, region, season, complexity, materials, labour, target_margin
    )
    base_recommended = (mid * 0.65) + (catalog_price.total * 0.35)
    comp_df = generate_competitor_prices(job_type, region, base_recommended)
    market_median = float(comp_df["price"].median())
    mw = market_weight / 100.0
    recommended_price = base_recommended * (1 - mw) + market_median * mw
    market_spread_pct = (base_recommended - market_median) / max(market_median, 1) * 100
    if market_spread_pct > 5:
        market_position = "ABOVE MARKET"
        pos_color = "#F97316"
        pos_bg = "#FED7AA"
    elif market_spread_pct < -5:
        market_position = "BELOW MARKET"
        pos_color = "#14B8A6"
        pos_bg = "#CCFBF1"
    else:
        market_position = "AT MARKET"
        pos_color = "#0F766E"
        pos_bg = "#CCFBF1"
    review_required = abs(recommended_price - mid) / max(mid, 1) > 0.18
    confidence = "Mixed" if review_required else "High"

    # ── Topbar ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:space-between;'
        'padding:18px 0 18px;border-bottom:1px solid #0A1F24;margin-bottom:0;">'
        '<span style="font-family:var(--mono);font-size:11px;letter-spacing:0.14em;text-transform:uppercase;">'
        "<strong>Pricing Demo</strong> &nbsp;/&nbsp; Service quote sandbox</span>"
        '<span class="topbar-meta"><span class="dot"></span>LIVE &nbsp;&nbsp; RUN · #2026-04-29-A</span>'
        "</div>",
        unsafe_allow_html=True,
    )

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Quote", "Data", "History", "Why", "Handoff"]
    )

    # =========================================================================
    # TAB 1 · QUOTE
    # =========================================================================
    with tab1:
        # Hero section
        st.markdown(
            '<span class="eyebrow">Recommended quote · blended model</span>'
            "<h1>A defensible price, <em>not</em> a guess.</h1>",
            unsafe_allow_html=True,
        )

        rec_int = f"{int(recommended_price):,}"
        review_label = "Required" if review_required else "Not required"
        st.markdown(
            f'<div style="display:flex;align-items:flex-end;justify-content:space-between;'
            f'border-bottom:1px solid #0A1F24;padding-bottom:24px;margin-bottom:0;flex-wrap:wrap;gap:16px;">'
            f'<div style="max-width:520px;">'
            f'<p style="font-size:15px;line-height:1.55;color:#1B3F47;margin:0;">'
            f"Two views of the same job — a historical-data band trained on synthetic prior service quotes, "
            f"plus a transparent rule-based catalog calculation. The recommendation is a weighted blend — "
            f"with a manual review flag when the two views disagree by more than 18%.</p>"
            f"</div>"
            f'<div style="text-align:right;flex-shrink:0;">'
            f'<span style="font-family:var(--mono);font-size:10px;letter-spacing:0.12em;text-transform:uppercase;'
            f'color:#1B3F47;display:block;margin-bottom:4px;">Recommended</span>'
            f"<div style=\"font-family:'Instrument Serif',serif;font-size:clamp(52px,6vw,96px);"
            f'line-height:0.9;letter-spacing:-0.04em;font-weight:400;color:#0A1F24;">'
            f'<span style="font-size:0.38em;font-style:italic;color:#0F766E;vertical-align:super;margin-right:2px;">$</span>'
            f"{rec_int}"
            f'<span style="font-size:0.28em;color:#1B3F47;vertical-align:super;">.00</span>'
            f"</div>"
            f'<div style="font-family:var(--mono);font-size:11px;letter-spacing:0.08em;text-transform:uppercase;'
            f'color:#1B3F47;margin-top:10px;display:flex;gap:20px;justify-content:flex-end;">'
            f'Confidence&nbsp;<strong style="color:#0A1F24;">{confidence}</strong>'
            f'&nbsp;&nbsp;Review&nbsp;<strong style="color:#0A1F24;">{review_label}</strong>'
            f"</div></div></div>",
            unsafe_allow_html=True,
        )

        # Band strip
        span = max(high - low, 1)
        rec_pct = 12 + max(0, min(1, (recommended_price - low) / span)) * 76
        low_pct, mid_pct, high_pct = 12, 50, 88
        st.markdown(
            f'<div style="padding:24px 0 8px;">'
            f'<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:12px;">'
            f'<h2 style="margin:0;font-size:20px;"><em>Price band</em> · low · mid · high</h2>'
            f'<span class="eyebrow" style="margin:0;">P15 → P85 quantile band from gradient-boosted model</span>'
            f"</div>"
            f'<div style="height:36px;"></div>'
            f'<div class="band-container">'
            f'<div style="position:absolute;top:-22px;left:{low_pct}%;transform:translateX(-50%);'
            f'font-family:var(--mono);font-size:10px;letter-spacing:0.08em;text-transform:uppercase;color:#1B3F47;white-space:nowrap;">P15 LOW</div>'
            f'<div style="position:absolute;top:-22px;left:{mid_pct}%;transform:translateX(-50%);'
            f'font-family:var(--mono);font-size:10px;letter-spacing:0.08em;text-transform:uppercase;color:#1B3F47;white-space:nowrap;">P50 MID</div>'
            f'<div style="position:absolute;top:-22px;left:{high_pct}%;transform:translateX(-50%);'
            f'font-family:var(--mono);font-size:10px;letter-spacing:0.08em;text-transform:uppercase;color:#1B3F47;white-space:nowrap;">P85 HIGH</div>'
            f'<div style="position:absolute;top:-1px;bottom:-1px;left:{low_pct}%;width:1px;background:#0A1F24;"></div>'
            f'<div style="position:absolute;top:-1px;bottom:-1px;left:{mid_pct}%;width:1px;background:#0A1F24;"></div>'
            f'<div style="position:absolute;top:-1px;bottom:-1px;left:{high_pct}%;width:1px;background:#0A1F24;"></div>'
            f'<div style="position:absolute;top:-8px;bottom:-8px;left:{rec_pct:.1f}%;width:3px;background:#0A1F24;">'
            f'<div style="position:absolute;top:-32px;left:50%;transform:translateX(-50%);background:#0A1F24;color:#F4F1EA;'
            f'padding:4px 10px;font-family:var(--mono);font-size:10px;letter-spacing:0.1em;white-space:nowrap;">'
            f"RECOMMENDED {_fmt(recommended_price)}</div></div>"
            f'<div style="position:absolute;bottom:-22px;left:{low_pct}%;transform:translateX(-50%);'
            f'font-family:var(--mono);font-size:11px;font-weight:600;color:#0A1F24;white-space:nowrap;">{_fmt(low)}</div>'
            f'<div style="position:absolute;bottom:-22px;left:{mid_pct}%;transform:translateX(-50%);'
            f'font-family:var(--mono);font-size:11px;font-weight:600;color:#0A1F24;white-space:nowrap;">{_fmt(mid)}</div>'
            f'<div style="position:absolute;bottom:-22px;left:{high_pct}%;transform:translateX(-50%);'
            f'font-family:var(--mono);font-size:11px;font-weight:600;color:#0A1F24;white-space:nowrap;">{_fmt(high)}</div>'
            f'</div><div style="height:40px;"></div></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            # ── Market intel ──────────────────────────────────────────────────────
            f'<div style="border:1px solid #0A1F24;margin:24px 0 0;">'
            f'<div style="display:flex;align-items:center;justify-content:space-between;'
            f'padding:16px 20px;border-bottom:1px solid #0A1F24;background:#EAE5DA;">'
            f'<span style="font-family:var(--mono);font-size:11px;letter-spacing:0.12em;text-transform:uppercase;">'
            f"Market Intel · {job_type} · {region}</span>"
            f'<span style="display:inline-flex;align-items:center;gap:10px;">'
            f'<span style="font-family:var(--mono);font-size:10px;letter-spacing:0.08em;text-transform:uppercase;'
            f'padding:3px 10px;color:{pos_color};background:{pos_bg};border:1px solid {pos_color};">'
            f"{market_position}</span>"
            f'<span style="font-family:var(--mono);font-size:11px;color:#1B3F47;">'
            f'{"+" if market_spread_pct >= 0 else ""}{market_spread_pct:.1f}% vs market median</span>'
            f"</span></div>"
            f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:0;">'
            f'<div style="padding:16px 20px;border-right:1px solid #DDD6C5;">'
            f'<span style="font-family:var(--mono);font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:#1B3F47;display:block;margin-bottom:4px;">Market median</span>'
            f"<span style=\"font-family:'Instrument Serif',serif;font-size:28px;letter-spacing:-0.02em;\">{_fmt(market_median)}</span>"
            f"</div>"
            f'<div style="padding:16px 20px;border-right:1px solid #DDD6C5;">'
            f'<span style="font-family:var(--mono);font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:#1B3F47;display:block;margin-bottom:4px;">Market low</span>'
            f'<span style="font-family:\'Instrument Serif\',serif;font-size:28px;letter-spacing:-0.02em;">{_fmt(comp_df["price"].min())}</span>'
            f"</div>"
            f'<div style="padding:16px 20px;border-right:1px solid #DDD6C5;">'
            f'<span style="font-family:var(--mono);font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:#1B3F47;display:block;margin-bottom:4px;">Market high</span>'
            f'<span style="font-family:\'Instrument Serif\',serif;font-size:28px;letter-spacing:-0.02em;">{_fmt(comp_df["price"].max())}</span>'
            f"</div>"
            f'<div style="padding:16px 20px;">'
            f'<span style="font-family:var(--mono);font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:#1B3F47;display:block;margin-bottom:4px;">Competitor weight</span>'
            f"<span style=\"font-family:'Instrument Serif',serif;font-size:28px;letter-spacing:-0.02em;\">{market_weight}%</span>"
            f"</div>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Competitor bar chart
        comp_sorted = comp_df.sort_values("price")
        fig_comp = go.Figure()
        bar_colors_comp = [
            (
                "#0A1F24"
                if abs(row["vs_us"]) <= 5
                else ("#F97316" if row["vs_us"] < 0 else "#14B8A6")
            )
            for _, row in comp_sorted.iterrows()
        ]
        fig_comp.add_trace(
            go.Bar(
                x=comp_sorted["Competitor"],
                y=comp_sorted["price"],
                marker_color=bar_colors_comp,
                text=[
                    f'{_fmt(p)}<br>{"+" if v >= 0 else ""}{v:.1f}%'
                    for p, v in zip(comp_sorted["price"], comp_sorted["vs_us"])
                ],
                textposition="outside",
                textfont=dict(family="Geist Mono, monospace", size=10, color="#0A1F24"),
                showlegend=False,
            )
        )
        fig_comp.add_hline(
            y=recommended_price,
            line_color="#0A1F24",
            line_width=2,
            line_dash="dash",
            annotation_text=f"Our price {_fmt(recommended_price)}",
            annotation_font=dict(
                family="Geist Mono, monospace", size=10, color="#0A1F24"
            ),
            annotation_position="top right",
        )
        fig_comp.add_hline(
            y=market_median,
            line_color="#14B8A6",
            line_width=1.5,
            line_dash="dot",
            annotation_text=f"Market median {_fmt(market_median)}",
            annotation_font=dict(
                family="Geist Mono, monospace", size=10, color="#14B8A6"
            ),
            annotation_position="bottom right",
        )
        fig_comp.update_layout(
            paper_bgcolor="#F4F1EA",
            plot_bgcolor="#F4F1EA",
            font_family="Geist, Inter, system-ui, sans-serif",
            font_color="#0A1F24",
            margin=dict(l=10, r=10, t=40, b=10),
            height=300,
            xaxis=dict(
                linecolor="#DDD6C5",
                tickfont=dict(family="Geist Mono, monospace", size=10),
            ),
            yaxis=dict(
                gridcolor="#DDD6C5",
                tickprefix="$",
                tickformat=",.0f",
                tickfont=dict(family="Geist Mono, monospace", size=10),
            ),
            bargap=0.4,
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        st.markdown(
            "<hr style='border:0;border-top:1px solid #0A1F24;margin:8px 0 32px;'>",
            unsafe_allow_html=True,
        )

        # Waterfall section
        st.markdown(
            '<span class="eyebrow">Hero · catalog build-up</span>'
            "<h2>Every dollar on the quote, <em>accounted for</em>.</h2>"
            '<p style="font-size:13px;color:#1B3F47;max-width:480px;line-height:1.5;margin-bottom:24px;">'
            "The rule-based view. No black box — line items map to base fee, materials, labour, "
            "regional and seasonal factors, complexity, risk buffer, and target margin.</p>",
            unsafe_allow_html=True,
        )

        wf_col, chart_col = st.columns([1, 1.4])
        with wf_col:
            item = catalog.loc[catalog["job_type"] == job_type].iloc[0]
            base_fee = float(item["base_fee"])
            rows_wf = [
                ("01", "Base fee", base_fee, False),
                (
                    "02",
                    "Materials × markup",
                    catalog_price.subtotal
                    - base_fee
                    - catalog_price.regional_adjustment
                    - catalog_price.seasonal_adjustment
                    - catalog_price.complexity_premium
                    - catalog_price.risk_buffer
                    - (float(item["hourly_rate"]) * labour),
                    False,
                ),
                (
                    "03",
                    "Labour × hourly rate",
                    float(item["hourly_rate"]) * labour,
                    False,
                ),
                ("04", "Regional adjustment", catalog_price.regional_adjustment, True),
                ("05", "Seasonal adjustment", catalog_price.seasonal_adjustment, True),
                ("06", "Complexity premium", catalog_price.complexity_premium, True),
                ("07", "Risk buffer", catalog_price.risk_buffer, True),
                (
                    f"08",
                    f"Target margin ({int(target_margin*100)}%)",
                    catalog_price.margin,
                    True,
                ),
            ]
            html_rows = ""
            for num, name, amt, signed in rows_wf:
                amt_str = _signed(amt) if signed else _fmt(amt)
                html_rows += (
                    f'<div class="waterfall-row">'
                    f'<span class="waterfall-num">{num}</span>'
                    f'<span class="waterfall-name">{name}</span>'
                    f'<span class="waterfall-amt">{amt_str}</span></div>'
                )
            html_rows += (
                f'<div class="waterfall-row waterfall-row-total">'
                f'<span class="waterfall-num" style="font-size:18px;font-family:var(--serif);font-style:italic;">∑</span>'
                f'<span class="waterfall-name" style="font-family:var(--serif);font-size:20px;font-style:italic;">Catalog total</span>'
                f'<span class="waterfall-amt" style="font-family:var(--serif);font-size:24px;">{_fmt(catalog_price.total)}</span></div>'
            )
            st.markdown(html_rows, unsafe_allow_html=True)

        with chart_col:
            mat_line = materials * float(item["material_markup"])
            lab_line = labour * float(item["hourly_rate"])
            wf_items = [
                ("Base", base_fee, "pos"),
                ("Materials", mat_line, "pos"),
                ("Labour", lab_line, "pos"),
                (
                    "Region",
                    catalog_price.regional_adjustment,
                    "add" if catalog_price.regional_adjustment >= 0 else "sub",
                ),
                (
                    "Season",
                    catalog_price.seasonal_adjustment,
                    "add" if catalog_price.seasonal_adjustment >= 0 else "sub",
                ),
                ("Complex.", catalog_price.complexity_premium, "add"),
                ("Risk", catalog_price.risk_buffer, "add"),
                ("Margin", catalog_price.margin, "add"),
                ("Total", catalog_price.total, "total"),
            ]
            running = 0.0
            bar_bases, bar_vals, bar_colors, bar_labels, x_labels = [], [], [], [], []
            color_map = {
                "pos": "#14B8A6",
                "add": "#CCFBF1",
                "sub": "#FED7AA",
                "total": "#0A1F24",
            }
            for i, (label, val, typ) in enumerate(wf_items):
                if typ == "total":
                    bar_bases.append(0)
                    bar_vals.append(val)
                    bar_colors.append("#0A1F24")
                elif typ in ("pos", "add"):
                    bar_bases.append(running)
                    bar_vals.append(abs(val))
                    running += val
                    bar_colors.append("#0A1F24" if i == 0 else color_map[typ])
                else:
                    bar_bases.append(running + val)
                    bar_vals.append(abs(val))
                    running += val
                    bar_colors.append(color_map[typ])
                bar_labels.append(f"${abs(val):,.0f}")
                x_labels.append(f"{i+1:02d} {label}")

            fig_wf = go.Figure()
            fig_wf.add_trace(
                go.Bar(
                    x=x_labels,
                    y=bar_bases,
                    marker_color="rgba(0,0,0,0)",
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
            fig_wf.add_trace(
                go.Bar(
                    x=x_labels,
                    y=bar_vals,
                    marker_color=bar_colors,
                    text=bar_labels,
                    textposition="outside",
                    textfont=dict(
                        family="Geist Mono, monospace", size=10, color="#0A1F24"
                    ),
                    showlegend=False,
                )
            )
            fig_wf.update_layout(
                barmode="stack",
                height=380,
                paper_bgcolor="#F4F1EA",
                plot_bgcolor="#F4F1EA",
                font_family="Geist, Inter, system-ui, sans-serif",
                font_color="#0A1F24",
                margin=dict(l=10, r=10, t=20, b=10),
                xaxis=dict(
                    tickfont=dict(family="Geist Mono, monospace", size=10),
                    linecolor="#DDD6C5",
                ),
                yaxis=dict(
                    tickfont=dict(family="Geist Mono, monospace", size=10),
                    gridcolor="#DDD6C5",
                    tickprefix="$",
                    tickformat=",.0f",
                ),
                bargap=0.35,
            )
            st.plotly_chart(fig_wf, use_container_width=True)

        # Dark summary cards
        st.markdown(
            "<hr style='border:0;border-top:1px solid #0A1F24;margin:32px 0 0;'>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="background:#0A1F24;color:#F4F1EA;padding:32px 0;margin:0;">'
            '<span class="eyebrow" style="color:#2DD4BF;display:block;margin-bottom:8px;">Two views, one answer</span>'
            '<h2 style="color:#F4F1EA;margin:0 0 8px;">Reconciling the model and the <em style="color:#2DD4BF;">catalog</em>.</h2>'
            '<p style="font-size:13px;color:#DDD6C5;max-width:500px;margin:0 0 24px;">'
            "The recommendation is 65% model, 35% catalog. If the gap exceeds 18% of the model mid, "
            "the quote is auto-routed to manual review.</p>"
            f'<div class="card-grid">'
            f'<div class="card-item card-item-dark"><span class="eyebrow eyebrow-teal" style="color:#0F766E;">P15 · Low</span>'
            f'<p class="card-num card-num-dark">{_fmt(low)}</p>'
            f'<span class="card-sub card-sub-dark">Aggressive · win-likely</span></div>'
            f'<div class="card-item card-item-dark"><span class="eyebrow eyebrow-teal" style="color:#0F766E;">P50 · Model mid</span>'
            f'<p class="card-num card-num-dark">{_fmt(mid)}</p>'
            f'<span class="card-sub card-sub-dark">Centered · historical</span></div>'
            f'<div class="card-item card-item-dark"><span class="eyebrow eyebrow-teal" style="color:#0F766E;">Catalog total</span>'
            f'<p class="card-num card-num-dark">{_fmt(catalog_price.total)}</p>'
            f'<span class="card-sub card-sub-dark">Rule-based · transparent</span></div>'
            f'<div class="card-item card-item-dark"><span class="eyebrow eyebrow-teal" style="color:#0F766E;">Blend (65/35)</span>'
            f'<p class="card-num card-num-dark">{_fmt(recommended_price)} <small style="font-size:0.5em;font-style:italic;color:#0F766E;">↗</small></p>'
            f'<span class="card-sub card-sub-dark">Recommended quote</span></div>'
            f"</div></div>",
            unsafe_allow_html=True,
        )

    # =========================================================================
    # TAB 2 · DATA
    # =========================================================================
    with tab2:
        st.markdown(
            '<span class="eyebrow">Data foundation</span>'
            "<h2>Pricing is <em>only</em> as good as its joins.</h2>"
            '<p style="font-size:13px;color:#1B3F47;max-width:520px;line-height:1.5;margin-bottom:24px;">'
            "Five sources, one shared key (quote ID). Where the join is weak, the score is weak. "
            "Where the score is weak, manual review takes the wheel.</p>",
            unsafe_allow_html=True,
        )
        st.dataframe(build_data_source_map(), use_container_width=True, hide_index=True)

        st.markdown(
            "<hr style='border:0;border-top:1px solid #0A1F24;margin:32px 0 0;'>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="background:#0A1F24;padding:32px 28px 8px;">'
            '<span class="eyebrow" style="color:#2DD4BF;display:block;margin-bottom:8px;">Data readiness · live</span>'
            '<h2 style="color:#F4F1EA;margin:0;">Where the system <em style="color:#2DD4BF;">flies</em> — and where it limps.</h2>'
            "</div>",
            unsafe_allow_html=True,
        )

        radar_col, quote_col = st.columns([1, 1])
        with radar_col:
            source_scores = pd.DataFrame(
                [
                    {"Area": "Availability", "Score": 82},
                    {"Area": "Joinability", "Score": 68},
                    {"Area": "Freshness", "Score": 74},
                    {"Area": "Ownership", "Score": 61},
                    {"Area": "Automation", "Score": 70},
                ]
            )
            fig_radar = go.Figure()
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=source_scores["Score"].tolist()
                    + [source_scores["Score"].iloc[0]],
                    theta=source_scores["Area"].tolist()
                    + [source_scores["Area"].iloc[0]],
                    fill="toself",
                    fillcolor="rgba(45,212,191,0.2)",
                    line=dict(color="#2DD4BF", width=2),
                    mode="lines+markers",
                    marker=dict(color="#2DD4BF", size=6),
                )
            )
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="#0A1F24",
                    radialaxis=dict(
                        range=[0, 100],
                        gridcolor="#1B3F47",
                        tickfont=dict(color="#DDD6C5", size=9),
                        linecolor="#1B3F47",
                    ),
                    angularaxis=dict(
                        gridcolor="#1B3F47",
                        linecolor="#1B3F47",
                        tickfont=dict(
                            color="#F4F1EA", size=11, family="Geist Mono, monospace"
                        ),
                    ),
                ),
                paper_bgcolor="#0A1F24",
                plot_bgcolor="#0A1F24",
                font_color="#F4F1EA",
                margin=dict(l=40, r=40, t=20, b=20),
                height=340,
                showlegend=False,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with quote_col:
            st.markdown(
                '<div style="padding:32px 0 24px;">'
                "<p style=\"font-family:'Instrument Serif',serif;font-size:26px;line-height:1.15;"
                'font-style:italic;color:#0A1F24;margin:0 0 16px;">'
                '"The model is a side dish. The data plumbing is the meal."</p>'
                '<p style="font-size:14px;color:#1B3F47;line-height:1.6;">'
                "Practical next step: connect opportunity, delivered-cost, and catalog data around "
                "one shared key — the quote ID. That makes the pricing auditable enough for sales use "
                "and structured enough for automation.</p></div>",
                unsafe_allow_html=True,
            )

    # =========================================================================
    # TAB 3 · HISTORY
    # =========================================================================
    with tab3:
        st.markdown(
            '<span class="eyebrow">Historical analysis · 900 quotes · 2022–2025</span>'
            "<h2>Where prices <em>actually</em> land.</h2>"
            '<p style="font-size:13px;color:#1B3F47;max-width:520px;line-height:1.5;margin-bottom:24px;">'
            "Final-price distributions per job type, across regions. Wider boxes = more variance = "
            "more reason for manual review.</p>",
            unsafe_allow_html=True,
        )

        fig_dist = px.box(
            df,
            x="job_type",
            y="final_price",
            color="region",
            labels={
                "job_type": "Job Type",
                "final_price": "Final Price ($)",
                "region": "Region",
            },
            color_discrete_sequence=[
                "#14B8A6",
                "#0F766E",
                "#2DD4BF",
                "#CCFBF1",
                "#C9A24A",
            ],
        )
        _apply_theme(fig_dist)
        fig_dist.update_layout(
            legend=dict(
                font=dict(family="Geist Mono, monospace", size=10), title_text=""
            ),
            title_text="",
        )
        st.plotly_chart(fig_dist, use_container_width=True)

        st.markdown(
            "<hr style='border:0;border-top:1px solid #DDD6C5;margin:16px 0 24px;'>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<h3 style=\"font-family:'Instrument Serif',serif;font-size:28px;font-weight:400;"
            'letter-spacing:-0.02em;margin:0 0 16px;">Outliers · |z| &gt; 2.5</h3>',
            unsafe_allow_html=True,
        )
        outliers = detect_outliers(df)
        out_df = (
            outliers[
                ["date", "job_type", "region", "final_price", "group_mean", "z_score"]
            ]
            .head(10)
            .copy()
        )
        out_df["date"] = out_df["date"].dt.strftime("%Y-%m-%d")
        out_df["final_price"] = out_df["final_price"].map(lambda x: f"${x:,.0f}")
        out_df["group_mean"] = out_df["group_mean"].map(lambda x: f"${x:,.0f}")
        out_df["z_score"] = out_df["z_score"].map(lambda x: f"{x:+.2f}")
        st.dataframe(out_df, use_container_width=True, hide_index=True)

        st.markdown(
            "<hr style='border:0;border-top:1px solid #0A1F24;margin:32px 0 0;'>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="background:#0A1F24;color:#F4F1EA;padding:32px 0 24px;">'
            '<span class="eyebrow" style="color:#2DD4BF;display:block;margin-bottom:8px;">Trend · monthly mean price</span>'
            '<h2 style="color:#F4F1EA;margin:0 0 24px;">Up and to the <em style="color:#2DD4BF;">right</em>.</h2>'
            "</div>",
            unsafe_allow_html=True,
        )
        trend = df.set_index("date").resample("ME")["final_price"].mean().reset_index()
        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Scatter(
                x=trend["date"],
                y=trend["final_price"],
                fill="tozeroy",
                fillcolor="rgba(45,212,191,0.15)",
                line=dict(color="#2DD4BF", width=2.2),
                mode="lines",
            )
        )
        _apply_theme(fig_trend, dark=True)
        fig_trend.update_layout(
            yaxis=dict(tickprefix="$", tickformat=",.0f", gridcolor="#1B3F47"),
            xaxis=dict(gridcolor="#1B3F47"),
            showlegend=False,
            height=320,
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # =========================================================================
    # TAB 4 · WHY
    # =========================================================================
    with tab4:
        st.markdown(
            '<span class="eyebrow">Why this price · interpretability</span>'
            "<h2>The model isn't <em>opinionated</em>. It's just adding things up.</h2>"
            '<p style="font-size:13px;color:#1B3F47;max-width:520px;line-height:1.5;margin-bottom:24px;">'
            "Feature importances from the gradient-boosted mid-price model. "
            "Numeric drivers dominate; categorical context tilts the result.</p>",
            unsafe_allow_html=True,
        )

        fi = feature_importance_frame(models)
        fi_max = fi["importance"].max()

        why_left, why_right = st.columns([1.1, 1])
        with why_left:
            html_fi = ""
            for _, row in fi.iterrows():
                pct = row["importance"] / fi_max * 100
                html_fi += (
                    f'<div class="fi-bar-wrap">'
                    f'<span class="fi-name">{row["feature"]}</span>'
                    f'<div class="fi-track"><div class="fi-fill" style="width:{pct:.0f}%;"></div></div>'
                    f'<span class="fi-pct">{row["importance"]*100:.1f}%</span>'
                    f"</div>"
                )
            st.markdown(html_fi, unsafe_allow_html=True)

        with why_right:
            st.markdown(
                '<div style="background:#EAE5DA;padding:24px;border:1px solid #0A1F24;">'
                "<h3 style=\"font-family:'Instrument Serif',serif;font-size:20px;font-weight:400;"
                'font-style:italic;margin:0 0 12px;">How to read this</h3>'
                '<div style="border-bottom:1px solid #DDD6C5;padding:10px 0;font-size:13.5px;line-height:1.5;">'
                "<strong>i. Numeric drivers carry the weight.</strong><br>"
                "Materials, hours, complexity together explain ~62%. Sense check these inputs first.</div>"
                '<div style="border-bottom:1px solid #DDD6C5;padding:10px 0;font-size:13.5px;line-height:1.5;">'
                "<strong>ii. Categorical context tilts.</strong><br>"
                "Job type and region don't set the price — they bend it.</div>"
                '<div style="border-bottom:1px solid #DDD6C5;padding:10px 0;font-size:13.5px;line-height:1.5;">'
                "<strong>iii. The band is the message.</strong><br>"
                "P15→P85 communicates uncertainty. Use Low for must-win, High where you have leverage.</div>"
                '<div style="padding:10px 0;font-size:13.5px;line-height:1.5;">'
                "<strong>iv. Disagreement triggers review.</strong><br>"
                "If model and catalog drift &gt;18%, the quote is held for sales judgment — by design.</div>"
                "</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<hr style='border:0;border-top:1px solid #DDD6C5;margin:32px 0 24px;'>",
            unsafe_allow_html=True,
        )
        comp_c1, comp_c2, comp_c3 = st.columns(3)
        comp_c1.metric("ML mid price", _fmt(mid))
        comp_c2.metric("Catalog rule price", _fmt(catalog_price.total))
        comp_c3.metric("Blended recommendation", _fmt(recommended_price))

    # =========================================================================
    # TAB 5 · HANDOFF
    # =========================================================================
    with tab5:
        st.markdown(
            '<span class="eyebrow">Automation handoff · JSON payload</span>'
            "<h2>From a <em>recommendation</em> to a workflow step.</h2>"
            '<p style="font-size:13px;color:#1B3F47;max-width:520px;line-height:1.5;margin-bottom:24px;">'
            "Structured payload routed to the chosen automation target. Review flag is computed "
            "server-side; sales never has to decide whether to escalate.</p>",
            unsafe_allow_html=True,
        )

        h1, h2, h3 = st.columns(3)
        h1.metric("Target", automation_target)
        h2.metric("Review", "Required" if review_required else "Not required")
        h3.metric("Quote draft", _fmt(recommended_price))

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
        json_str = json.dumps(payload, indent=2)

        out_col, in_col = st.columns(2)

        with out_col:
            st.markdown(
                '<span class="eyebrow" style="color:#0F766E;">Outbound · pricing service → agent</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<pre class="code-block">{json_str}</pre>',
                unsafe_allow_html=True,
            )

        with in_col:
            st.markdown(
                '<span class="eyebrow" style="color:#0F766E;">Inbound · agent response</span>',
                unsafe_allow_html=True,
            )

            if st.button("Simulate agent response", type="primary"):
                with st.spinner("Agent processing…"):
                    _time.sleep(1.2)

                next_step = (
                    "Route to sales manager for review — gap exceeds 18% threshold"
                    if review_required
                    else f"Create quote draft in CRM · assigned to sales rep · status: pending_send"
                )
                action = "ESCALATE_TO_REVIEW" if review_required else "CREATE_DRAFT"
                agent_response = {
                    "agent": automation_target,
                    "status": "acknowledged",
                    "quote_id": f"QT-{job_type[:3].upper()}-{int(recommended_price):06d}",
                    "action": action,
                    "recommended_price": round(recommended_price, 2),
                    "review_required": bool(review_required),
                    "next_step": next_step,
                    "crm_record": {
                        "opportunity_stage": (
                            "Quote sent" if not review_required else "Pending approval"
                        ),
                        "job_type": job_type,
                        "region": region,
                        "assigned_to": "sales_rep@company.com",
                    },
                    "feedback_hook": "POST /quotes/{quote_id}/outcome  →  triggers model retrain",
                    "timestamp": "2026-04-29T08:00:00Z",
                }
                agent_str = json.dumps(agent_response, indent=2)
                status_color = "#F97316" if review_required else "#2DD4BF"
                status_label = "REVIEW REQUIRED" if review_required else "DRAFT CREATED"
                st.markdown(
                    f'<div style="font-family:var(--mono);font-size:10px;letter-spacing:0.12em;'
                    f"text-transform:uppercase;color:{status_color};margin-bottom:8px;"
                    f'padding:6px 12px;border:1px solid {status_color};display:inline-block;">'
                    f"{status_label}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<pre class="code-block">{agent_str}</pre>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<pre class="code-block" style="color:#1B3F47;border-color:#1B3F47;">'
                    "// Waiting for trigger…\n"
                    "// Agent will receive the outbound payload\n"
                    "// and return a structured acknowledgement.\n"
                    "</pre>",
                    unsafe_allow_html=True,
                )

        st.markdown(
            "<hr style='border:0;border-top:1px solid #0A1F24;margin:32px 0 0;'>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="background:#0A1F24;color:#F4F1EA;padding:32px 0 24px;">'
            '<span class="eyebrow" style="color:#2DD4BF;display:block;margin-bottom:8px;">Lifecycle</span>'
            '<h2 style="color:#F4F1EA;margin:0 0 24px;">Collect · Price · Review · <em style="color:#2DD4BF;">Learn</em>.</h2>'
            "</div>",
            unsafe_allow_html=True,
        )
        process = pd.DataFrame(
            [
                {
                    "Step": "01",
                    "Stage": "Collect",
                    "Owner": "CRM / ERP",
                    "Output": "Normalized quote request",
                    "SLA": "< 30s",
                },
                {
                    "Step": "02",
                    "Stage": "Price",
                    "Owner": "Pricing service",
                    "Output": "ML band + catalog total + recommended",
                    "SLA": "< 2s",
                },
                {
                    "Step": "03",
                    "Stage": "Review",
                    "Owner": "Sales (conditional)",
                    "Output": "Approved or adjusted quote",
                    "SLA": "< 4h",
                },
                {
                    "Step": "04",
                    "Stage": "Learn",
                    "Owner": "Analytics",
                    "Output": "Win/loss + delivered margin → retrain",
                    "SLA": "weekly",
                },
            ]
        )
        st.dataframe(process, use_container_width=True, hide_index=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="background:#0A1F24;color:#DDD6C5;padding:28px 0;margin-top:0;'
        "font-family:var(--mono);font-size:11px;letter-spacing:0.06em;"
        'display:flex;justify-content:space-between;border-top:1px solid #1B3F47;">'
        "<span>Pricing Demo · Service quote sandbox</span>"
        "<span>Synthetic data · for demonstration use only · 04·2026</span></div>",
        unsafe_allow_html=True,
    )

    with st.expander("Preview synthetic data"):
        st.dataframe(df.head(20), use_container_width=True)


if __name__ == "__main__":
    main()
