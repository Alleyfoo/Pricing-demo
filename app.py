import json
import hashlib
import math
import time as _time
from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder

try:
    from prophet import Prophet
except Exception:
    Prophet = None

st.set_page_config(page_title="Service Pricing Automation Demo", layout="wide")

# ── Design system CSS ─────────────────────────────────────────────────────────
st.html(
    """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,400,0,0&display=block" rel="stylesheet">
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
span[class*="material-symbols"],
i[class*="material-icons"],
.material-symbols-rounded,
.material-symbols-outlined,
.material-icons {
  font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
  font-weight: normal !important;
  font-style: normal !important;
  font-size: 20px !important;
  line-height: 1 !important;
  letter-spacing: normal !important;
  text-transform: none !important;
  white-space: nowrap !important;
  word-wrap: normal !important;
  direction: ltr !important;
  font-feature-settings: "liga" !important;
  font-variation-settings: "FILL" 0, "wght" 400, "GRAD" 0, "opsz" 24 !important;
  -webkit-font-feature-settings: "liga" !important;
  -webkit-font-smoothing: antialiased !important;
}
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
[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"] {
  font-family: var(--mono) !important;
  font-size: 12px !important;
  color: var(--teal-bright) !important;
}
[data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"] {
  display: none !important;
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
.status-pill { display: inline-flex; align-items: center; justify-content: center; min-width: 72px; font-family: var(--mono); font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; padding: 4px 8px; border: 1px solid currentColor; }
.status-ok { color: var(--teal-dim); background: var(--teal-soft); }
.status-warning { color: var(--signal); background: var(--signal-soft); }
.status-critical { color: #991B1B; background: #FEE2E2; }
.status-bucket-a { color: #0F766E; background: #CCFBF1; }
.status-bucket-b { color: #1B3F47; background: #EAE5DA; }
.status-bucket-c { color: #F97316; background: #FED7AA; }
.status-bucket-d { color: #991B1B; background: #FEE2E2; }
.bucket-lane { border: 1px solid var(--ink); margin-bottom: 12px; }
.bucket-lane-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; background: var(--paper-2); border-bottom: 1px solid var(--ink); padding: 10px 12px; }
.bucket-lane-title { font-family: var(--mono); font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink); }
.bucket-lane-meta { font-family: var(--mono); font-size: 10px; color: var(--ink-3); }
.bucket-sku { display: grid; grid-template-columns: minmax(170px, 1.4fr) repeat(3, minmax(72px, 0.6fr)); gap: 12px; align-items: center; padding: 10px 12px; border-bottom: 1px solid var(--paper-3); font-size: 13px; }
.bucket-sku:last-child { border-bottom: 0; }
.bucket-measure { font-family: var(--mono); font-size: 11px; color: var(--ink-3); }
.health-grid { display: grid; grid-template-columns: repeat(2, minmax(260px, 1fr)); gap: 16px; margin-bottom: 24px; }
.health-panel { border: 1px solid var(--ink); background: var(--paper); }
.health-panel-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 12px 14px; background: var(--paper-2); border-bottom: 1px solid var(--ink); }
.health-panel-title { font-family: var(--mono); font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink); }
.health-row { display: grid; grid-template-columns: minmax(150px, 1fr) 72px 96px; gap: 12px; align-items: start; padding: 11px 14px; border-bottom: 1px solid var(--paper-3); font-size: 13px; }
.health-row:last-child { border-bottom: 0; }
.health-score { font-family: var(--serif); font-size: 26px; line-height: 0.95; letter-spacing: -0.02em; color: var(--ink); }
.status-info { color: #1B3F47; background: #EAE5DA; }
.governance-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 1px; background: var(--ink); border: 1px solid var(--ink); margin: 0 0 24px; }
.governance-cell { background: var(--paper); padding: 16px 14px; min-height: 106px; }
.governance-cell strong { display: block; font-family: var(--serif); font-size: 30px; line-height: 0.95; letter-spacing: -0.02em; font-weight: 400; margin: 8px 0 4px; }
.governance-flow { display: grid; grid-template-columns: repeat(5, minmax(130px, 1fr)); gap: 1px; background: var(--ink); border: 1px solid var(--ink); margin-bottom: 24px; }
.governance-step { background: var(--paper-2); padding: 14px; min-height: 118px; }
.governance-step-num { font-family: var(--mono); font-size: 10px; color: var(--teal-dim); letter-spacing: 0.1em; text-transform: uppercase; }
.governance-step-title { font-weight: 600; font-size: 13px; margin: 8px 0 5px; color: var(--ink); }
.governance-step-copy { font-size: 12.5px; line-height: 1.4; color: var(--ink-3); margin: 0; }
.check-table { width: 100%; border-collapse: collapse; border: 1px solid var(--ink); font-size: 13px; }
.check-table th { background: var(--paper-2); font-family: var(--mono); font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-3); text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--ink); }
.check-table td { padding: 11px 12px; border-bottom: 1px solid var(--paper-3); vertical-align: top; }
.check-table tr:last-child td { border-bottom: 0; }
.check-muted { color: var(--ink-3); font-family: var(--mono); font-size: 11px; }
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


def build_product_pricing_checks(today: date | None = None) -> pd.DataFrame:
    if today is None:
        today = date.today()

    products = [
        {
            "item_id": "PM-100",
            "product": "Smart valve actuator",
            "category": "Controls",
            "cost": 118.00,
            "expected_price": 169.00,
            "expected_start": today - timedelta(days=4),
            "expected_end": today + timedelta(days=24),
            "channels": {
                "Local": (169.00, -4, 24),
                "Branch": (169.00, -4, 24),
                "Online": (171.00, -4, 24),
            },
        },
        {
            "item_id": "PM-220",
            "product": "Filter replacement kit",
            "category": "Maintenance",
            "cost": 42.50,
            "expected_price": 64.00,
            "expected_start": today - timedelta(days=2),
            "expected_end": today + timedelta(days=12),
            "channels": {
                "Local": (59.00, -2, 12),
                "Branch": (64.00, -2, 12),
                "Online": (64.00, -1, 12),
            },
        },
        {
            "item_id": "PM-340",
            "product": "Sensor calibration bundle",
            "category": "Service parts",
            "cost": 76.00,
            "expected_price": 112.00,
            "expected_start": today,
            "expected_end": today + timedelta(days=14),
            "channels": {
                "Local": (112.00, 0, 14),
                "Branch": (112.00, 0, -1),
                "Online": (109.00, 0, 14),
            },
        },
        {
            "item_id": "PM-480",
            "product": "Weekly promo thermostat",
            "category": "Campaign",
            "cost": 88.00,
            "expected_price": 119.00,
            "expected_start": today - timedelta(days=1),
            "expected_end": today + timedelta(days=6),
            "channels": {
                "Local": (119.00, -1, 6),
                "Branch": (125.00, -1, 6),
                "Online": (119.00, -8, -2),
            },
        },
    ]

    rows = []
    for product in products:
        for channel, (system_price, start_offset, end_offset) in product[
            "channels"
        ].items():
            rows.append(
                {
                    "item_id": product["item_id"],
                    "product": product["product"],
                    "category": product["category"],
                    "channel": channel,
                    "system_price": system_price,
                    "expected_price": product["expected_price"],
                    "system_start": today + timedelta(days=start_offset),
                    "system_end": today + timedelta(days=end_offset),
                    "expected_start": product["expected_start"],
                    "expected_end": product["expected_end"],
                    "cost": product["cost"],
                }
            )

    return validate_product_pricing(pd.DataFrame(rows), today)


def validate_product_pricing(df: pd.DataFrame, today: date | None = None) -> pd.DataFrame:
    if today is None:
        today = date.today()

    checked = df.copy()
    checked["price_gap_pct"] = (
        (checked["system_price"] - checked["expected_price"])
        / checked["expected_price"].replace(0, np.nan)
        * 100
    ).round(1)
    checked["price_ok"] = checked["price_gap_pct"].abs() <= 5
    checked["start_ok"] = checked["system_start"] == checked["expected_start"]
    checked["end_ok"] = checked["system_end"] == checked["expected_end"]
    checked["active_today"] = (
        pd.to_datetime(today) >= pd.to_datetime(checked["system_start"])
    ) & (pd.to_datetime(today) <= pd.to_datetime(checked["system_end"]))
    checked["margin_pct"] = (
        (checked["system_price"] - checked["cost"]) / checked["system_price"] * 100
    ).round(1)
    checked["margin_ok"] = checked["margin_pct"] >= 10
    checked["status"] = "OK"
    checked.loc[~checked["active_today"], "status"] = "Critical"
    warning = checked["status"].ne("Critical") & ~checked[
        ["price_ok", "start_ok", "end_ok", "margin_ok"]
    ].all(axis=1)
    checked.loc[warning, "status"] = "Warning"

    checked["issue"] = ""
    checked.loc[~checked["active_today"], "issue"] = "Not active today"
    checked.loc[
        checked["active_today"] & ~checked["price_ok"], "issue"
    ] = "Price differs from expected"
    checked.loc[
        checked["active_today"] & checked["price_ok"] & ~(checked["start_ok"] & checked["end_ok"]),
        "issue",
    ] = "Validity window mismatch"
    checked.loc[
        checked["active_today"]
        & checked["price_ok"]
        & checked["start_ok"]
        & checked["end_ok"]
        & ~checked["margin_ok"],
        "issue",
    ] = "Margin below floor"
    checked.loc[checked["issue"].eq(""), "issue"] = "Ready"
    return checked


def product_correction_payload(df: pd.DataFrame) -> dict:
    needs_fix = df[df["status"].ne("OK")]
    return {
        "control": "product_pricing_setup",
        "source": "synthetic product master",
        "records_checked": int(len(df)),
        "records_to_correct": int(len(needs_fix)),
        "actions": [
            {
                "item_id": row.item_id,
                "channel": row.channel,
                "issue": row.issue,
                "set_price": round(float(row.expected_price), 2),
                "set_start": str(row.expected_start),
                "set_end": str(row.expected_end),
            }
            for row in needs_fix.itertuples()
        ],
    }


@st.cache_data
def build_inventory_bucket_data(today: date | None = None) -> pd.DataFrame:
    if today is None:
        today = date.today()

    records = [
        {
            "item_id": "PM-100",
            "product": "Smart valve actuator",
            "category": "Controls",
            "current_stock": 420,
            "unit_cost": 118.00,
            "units_28d": 286,
            "units_90d": 820,
            "days_since_sale": 1,
            "margin_pct": 30.2,
        },
        {
            "item_id": "PM-220",
            "product": "Filter replacement kit",
            "category": "Maintenance",
            "current_stock": 280,
            "unit_cost": 42.50,
            "units_28d": 382,
            "units_90d": 1120,
            "days_since_sale": 0,
            "margin_pct": 33.6,
        },
        {
            "item_id": "PM-480",
            "product": "Weekly promo thermostat",
            "category": "Campaign",
            "current_stock": 140,
            "unit_cost": 88.00,
            "units_28d": 318,
            "units_90d": 650,
            "days_since_sale": 0,
            "margin_pct": 26.1,
        },
        {
            "item_id": "PM-340",
            "product": "Sensor calibration bundle",
            "category": "Service parts",
            "current_stock": 190,
            "unit_cost": 76.00,
            "units_28d": 168,
            "units_90d": 520,
            "days_since_sale": 2,
            "margin_pct": 32.1,
        },
        {
            "item_id": "PM-410",
            "product": "Hydronic balancing valve",
            "category": "Controls",
            "current_stock": 210,
            "unit_cost": 64.00,
            "units_28d": 126,
            "units_90d": 380,
            "days_since_sale": 3,
            "margin_pct": 29.0,
        },
        {
            "item_id": "PM-515",
            "product": "Condensate pump kit",
            "category": "Maintenance",
            "current_stock": 165,
            "unit_cost": 52.00,
            "units_28d": 94,
            "units_90d": 270,
            "days_since_sale": 6,
            "margin_pct": 27.4,
        },
        {
            "item_id": "PM-605",
            "product": "Pipe insulation sleeve",
            "category": "Consumables",
            "current_stock": 520,
            "unit_cost": 9.80,
            "units_28d": 82,
            "units_90d": 260,
            "days_since_sale": 5,
            "margin_pct": 38.7,
        },
        {
            "item_id": "PM-730",
            "product": "Expansion vessel bracket",
            "category": "Install parts",
            "current_stock": 240,
            "unit_cost": 18.50,
            "units_28d": 54,
            "units_90d": 190,
            "days_since_sale": 9,
            "margin_pct": 24.6,
        },
        {
            "item_id": "PM-760",
            "product": "Legacy controller faceplate",
            "category": "Legacy",
            "current_stock": 310,
            "unit_cost": 21.00,
            "units_28d": 22,
            "units_90d": 86,
            "days_since_sale": 18,
            "margin_pct": 18.8,
        },
        {
            "item_id": "PM-820",
            "product": "Special order gasket",
            "category": "Service parts",
            "current_stock": 95,
            "unit_cost": 14.00,
            "units_28d": 12,
            "units_90d": 48,
            "days_since_sale": 24,
            "margin_pct": 22.0,
        },
        {
            "item_id": "PM-900",
            "product": "Discontinued wall sensor",
            "category": "Legacy",
            "current_stock": 360,
            "unit_cost": 36.00,
            "units_28d": 4,
            "units_90d": 18,
            "days_since_sale": 72,
            "margin_pct": 11.5,
        },
        {
            "item_id": "PM-940",
            "product": "Obsolete mounting rail",
            "category": "Legacy",
            "current_stock": 440,
            "unit_cost": 7.50,
            "units_28d": 2,
            "units_90d": 9,
            "days_since_sale": 96,
            "margin_pct": 9.2,
        },
    ]

    df = pd.DataFrame(records)
    df["as_of"] = today
    df["avg_daily_units"] = (df["units_28d"] / 28).round(1)
    df["weekly_velocity"] = (df["avg_daily_units"] * 7).round(1)
    df["sell_through_28d"] = (
        df["units_28d"] / (df["current_stock"] + df["units_28d"]) * 100
    ).round(1)
    df["days_on_hand"] = (
        df["current_stock"] / df["avg_daily_units"].replace(0, np.nan)
    ).replace([np.inf, -np.inf], np.nan)
    df["days_on_hand"] = df["days_on_hand"].fillna(999).round(0).astype(int)
    df["inventory_value"] = (df["current_stock"] * df["unit_cost"]).round(0)
    df["bucket"] = "C"
    df["bucket_name"] = "C slow"
    df.loc[
        (df["avg_daily_units"] >= 7.0) | (df["sell_through_28d"] >= 45),
        ["bucket", "bucket_name"],
    ] = ["A", "A fast"]
    df.loc[
        df["bucket"].eq("C")
        & ((df["avg_daily_units"] >= 2.5) | (df["sell_through_28d"] >= 22)),
        ["bucket", "bucket_name"],
    ] = ["B", "B steady"]
    df.loc[
        (df["days_since_sale"] >= 60) | (df["units_28d"] <= 5),
        ["bucket", "bucket_name"],
    ] = ["D", "D stale"]
    df["action"] = df["bucket"].map(
        {
            "A": "Protect availability; avoid deep discounting",
            "B": "Review reorder point and price tests",
            "C": "Reduce buy quantity or bundle into service offers",
            "D": "Markdown, return, or remove from active catalog",
        }
    )
    return df.sort_values(["bucket", "weekly_velocity"], ascending=[True, False])


def inventory_bucket_payload(df: pd.DataFrame) -> dict:
    summary = (
        df.groupby("bucket")
        .agg(
            items=("item_id", "count"),
            stock_units=("current_stock", "sum"),
            inventory_value=("inventory_value", "sum"),
            weekly_velocity=("weekly_velocity", "sum"),
        )
        .reset_index()
    )
    return {
        "control": "inventory_velocity_buckets",
        "source": "synthetic inventory ledger",
        "bucket_rules": {
            "A": "Fast movers: high 28-day velocity or sell-through",
            "B": "Steady movers: predictable but lower velocity",
            "C": "Slow movers: low movement, still recently sold",
            "D": "Stale: no recent demand or 28-day units near zero",
        },
        "summary": [
            {
                "bucket": row.bucket,
                "items": int(row.items),
                "stock_units": int(row.stock_units),
                "inventory_value": int(row.inventory_value),
                "weekly_velocity": round(float(row.weekly_velocity), 1),
            }
            for row in summary.itertuples()
        ],
        "stale_items": [
            {
                "item_id": row.item_id,
                "product": row.product,
                "stock_units": int(row.current_stock),
                "inventory_value": int(row.inventory_value),
                "days_since_sale": int(row.days_since_sale),
                "action": row.action,
            }
            for row in df[df["bucket"].eq("D")].itertuples()
        ],
    }


@st.cache_data
def build_product_health_data(today: date | None = None) -> pd.DataFrame:
    if today is None:
        today = date.today()

    records = [
        {
            "item_id": "PM-100",
            "product": "Smart valve actuator",
            "category": "Controls",
            "lifecycle": "Active",
            "description_score": 92,
            "missing_fields": 0,
            "return_rate_pct": 2.1,
            "refund_pct": 0.7,
            "refund_value": 420,
            "return_reason": "Normal warranty mix",
            "days_since_sale": 1,
            "stock_units": 420,
            "unit_cost": 118.00,
            "margin_pct": 30.2,
            "discount_rate_pct": 6.0,
        },
        {
            "item_id": "PM-220",
            "product": "Filter replacement kit",
            "category": "Maintenance",
            "lifecycle": "Active",
            "description_score": 81,
            "missing_fields": 1,
            "return_rate_pct": 4.4,
            "refund_pct": 1.5,
            "refund_value": 760,
            "return_reason": "Wrong filter size selected",
            "days_since_sale": 0,
            "stock_units": 280,
            "unit_cost": 42.50,
            "margin_pct": 33.6,
            "discount_rate_pct": 8.0,
        },
        {
            "item_id": "PM-340",
            "product": "Sensor calibration bundle",
            "category": "Service parts",
            "lifecycle": "Active",
            "description_score": 68,
            "missing_fields": 2,
            "return_rate_pct": 9.8,
            "refund_pct": 4.6,
            "refund_value": 2200,
            "return_reason": "Compatibility unclear",
            "days_since_sale": 2,
            "stock_units": 190,
            "unit_cost": 76.00,
            "margin_pct": 32.1,
            "discount_rate_pct": 11.0,
        },
        {
            "item_id": "PM-480",
            "product": "Weekly promo thermostat",
            "category": "Campaign",
            "lifecycle": "Promo",
            "description_score": 74,
            "missing_fields": 1,
            "return_rate_pct": 11.4,
            "refund_pct": 5.2,
            "refund_value": 3180,
            "return_reason": "Feature expectation mismatch",
            "days_since_sale": 0,
            "stock_units": 140,
            "unit_cost": 88.00,
            "margin_pct": 26.1,
            "discount_rate_pct": 28.0,
        },
        {
            "item_id": "PM-410",
            "product": "Hydronic balancing valve",
            "category": "Controls",
            "lifecycle": "Active",
            "description_score": 88,
            "missing_fields": 0,
            "return_rate_pct": 3.6,
            "refund_pct": 1.1,
            "refund_value": 540,
            "return_reason": "Normal install variance",
            "days_since_sale": 3,
            "stock_units": 210,
            "unit_cost": 64.00,
            "margin_pct": 29.0,
            "discount_rate_pct": 7.5,
        },
        {
            "item_id": "PM-515",
            "product": "Condensate pump kit",
            "category": "Maintenance",
            "lifecycle": "Active",
            "description_score": 58,
            "missing_fields": 3,
            "return_rate_pct": 7.9,
            "refund_pct": 2.8,
            "refund_value": 1280,
            "return_reason": "Missing installation notes",
            "days_since_sale": 6,
            "stock_units": 165,
            "unit_cost": 52.00,
            "margin_pct": 27.4,
            "discount_rate_pct": 12.0,
        },
        {
            "item_id": "PM-730",
            "product": "Expansion vessel bracket",
            "category": "Install parts",
            "lifecycle": "Phase-out",
            "description_score": 76,
            "missing_fields": 1,
            "return_rate_pct": 5.7,
            "refund_pct": 2.2,
            "refund_value": 610,
            "return_reason": "Wrong fitment",
            "days_since_sale": 9,
            "stock_units": 240,
            "unit_cost": 18.50,
            "margin_pct": 24.6,
            "discount_rate_pct": 18.0,
        },
        {
            "item_id": "PM-760",
            "product": "Legacy controller faceplate",
            "category": "Legacy",
            "lifecycle": "Phase-out",
            "description_score": 49,
            "missing_fields": 4,
            "return_rate_pct": 13.6,
            "refund_pct": 6.4,
            "refund_value": 1850,
            "return_reason": "Legacy compatibility unclear",
            "days_since_sale": 18,
            "stock_units": 310,
            "unit_cost": 21.00,
            "margin_pct": 18.8,
            "discount_rate_pct": 22.0,
        },
        {
            "item_id": "PM-820",
            "product": "Special order gasket",
            "category": "Service parts",
            "lifecycle": "Active",
            "description_score": 63,
            "missing_fields": 2,
            "return_rate_pct": 6.2,
            "refund_pct": 2.4,
            "refund_value": 420,
            "return_reason": "Wrong dimensions selected",
            "days_since_sale": 24,
            "stock_units": 95,
            "unit_cost": 14.00,
            "margin_pct": 22.0,
            "discount_rate_pct": 9.0,
        },
        {
            "item_id": "PM-900",
            "product": "Discontinued wall sensor",
            "category": "Legacy",
            "lifecycle": "Discontinued",
            "description_score": 42,
            "missing_fields": 5,
            "return_rate_pct": 16.8,
            "refund_pct": 8.5,
            "refund_value": 2480,
            "return_reason": "Product substituted or unsupported",
            "days_since_sale": 72,
            "stock_units": 360,
            "unit_cost": 36.00,
            "margin_pct": 11.5,
            "discount_rate_pct": 34.0,
        },
        {
            "item_id": "PM-940",
            "product": "Obsolete mounting rail",
            "category": "Legacy",
            "lifecycle": "Obsolete",
            "description_score": 35,
            "missing_fields": 6,
            "return_rate_pct": 10.2,
            "refund_pct": 5.9,
            "refund_value": 720,
            "return_reason": "No matching replacement shown",
            "days_since_sale": 96,
            "stock_units": 440,
            "unit_cost": 7.50,
            "margin_pct": 9.2,
            "discount_rate_pct": 41.0,
        },
    ]

    df = pd.DataFrame(records)
    df["as_of"] = today
    df["inventory_value"] = (df["stock_units"] * df["unit_cost"]).round(0)
    df["master_data_issue"] = (df["description_score"] < 75) | (df["missing_fields"] > 0)
    df["returns_issue"] = (df["return_rate_pct"] >= 8) | (df["refund_pct"] >= 4)
    df["scrap_candidate"] = (
        df["lifecycle"].isin(["Discontinued", "Obsolete"])
        & (df["days_since_sale"] >= 60)
    )
    df["margin_issue"] = (df["margin_pct"] < 15) | (df["discount_rate_pct"] >= 30)
    df["scrap_value"] = np.where(df["scrap_candidate"], df["inventory_value"], 0)
    df["issue_count"] = df[
        ["master_data_issue", "returns_issue", "scrap_candidate", "margin_issue"]
    ].sum(axis=1)
    df["health_status"] = "OK"
    df.loc[df["issue_count"].between(1, 2), "health_status"] = "Review"
    df.loc[df["issue_count"].ge(3), "health_status"] = "Critical"
    df["recommended_action"] = "Monitor in normal product review"
    df.loc[df["master_data_issue"], "recommended_action"] = "Repair catalog fields and description"
    df.loc[df["returns_issue"], "recommended_action"] = "Investigate return reason and refund leakage"
    df.loc[df["margin_issue"], "recommended_action"] = "Reset margin floor or discount guardrail"
    df.loc[df["scrap_candidate"], "recommended_action"] = "Route to markdown, return, or scrap approval"
    return df.sort_values(["issue_count", "refund_value"], ascending=[False, False])


def product_health_payload(df: pd.DataFrame) -> dict:
    return {
        "control": "product_health_monitor",
        "source": "synthetic product operations ledger",
        "as_of": str(df["as_of"].iloc[0]),
        "summary": {
            "products_checked": int(len(df)),
            "master_data_issues": int(df["master_data_issue"].sum()),
            "returns_refunds_issues": int(df["returns_issue"].sum()),
            "scrap_candidates": int(df["scrap_candidate"].sum()),
            "margin_leakage_items": int(df["margin_issue"].sum()),
            "scrap_value": int(df["scrap_value"].sum()),
            "refund_value": int(df.loc[df["returns_issue"], "refund_value"].sum()),
        },
        "critical_items": [
            {
                "item_id": row.item_id,
                "product": row.product,
                "lifecycle": row.lifecycle,
                "issue_count": int(row.issue_count),
                "return_rate_pct": round(float(row.return_rate_pct), 1),
                "margin_pct": round(float(row.margin_pct), 1),
                "scrap_value": int(row.scrap_value),
                "action": row.recommended_action,
            }
            for row in df[df["health_status"].eq("Critical")].itertuples()
        ],
    }


@st.cache_data
def build_product_governance_data(today: date | None = None) -> pd.DataFrame:
    if today is None:
        today = date.today()

    records = [
        {
            "item_id": "PM-100",
            "product": "Smart valve actuator",
            "local_category": "Controls",
            "reference_class": "Valve and flow-control component",
            "reference_code": "8481.80",
            "local_material": "Steel",
            "reference_material": "Steel",
            "local_uom": "Each",
            "reference_packaging": "Each",
            "origin_master": "DE",
            "origin_supplier": "DE",
            "lifecycle": "Active",
            "launch_price": True,
            "launch_description": True,
            "launch_image": True,
            "launch_compliance": True,
            "launch_stock": True,
            "old_cost": 112.00,
            "new_cost": 118.00,
            "current_price": 169.00,
            "target_margin_pct": 24.0,
            "replacement_sku": "",
            "sales_quotes_old_sku": 0,
            "owner": "Product ops",
        },
        {
            "item_id": "PM-220",
            "product": "Filter replacement kit",
            "local_category": "Maintenance",
            "reference_class": "Replaceable filtering apparatus part",
            "reference_code": "8421.99",
            "local_material": "Paper media",
            "reference_material": "Paper media",
            "local_uom": "Kit",
            "reference_packaging": "Set/kit",
            "origin_master": "FI",
            "origin_supplier": "FI",
            "lifecycle": "Active",
            "launch_price": True,
            "launch_description": True,
            "launch_image": False,
            "launch_compliance": True,
            "launch_stock": True,
            "old_cost": 39.00,
            "new_cost": 42.50,
            "current_price": 64.00,
            "target_margin_pct": 28.0,
            "replacement_sku": "",
            "sales_quotes_old_sku": 0,
            "owner": "Catalog team",
        },
        {
            "item_id": "PM-340",
            "product": "Sensor calibration bundle",
            "local_category": "Service parts",
            "reference_class": "Electronic measuring instrument accessory",
            "reference_code": "9031.90",
            "local_material": "Mixed",
            "reference_material": "Electronic assembly",
            "local_uom": "Each",
            "reference_packaging": "Set/kit",
            "origin_master": "",
            "origin_supplier": "EE",
            "lifecycle": "Active",
            "launch_price": True,
            "launch_description": False,
            "launch_image": True,
            "launch_compliance": False,
            "launch_stock": True,
            "old_cost": 68.00,
            "new_cost": 76.00,
            "current_price": 112.00,
            "target_margin_pct": 30.0,
            "replacement_sku": "",
            "sales_quotes_old_sku": 0,
            "owner": "Compliance",
        },
        {
            "item_id": "PM-480",
            "product": "Weekly promo thermostat",
            "local_category": "Campaign",
            "reference_class": "Automatic regulating instrument",
            "reference_code": "9032.10",
            "local_material": "Plastic",
            "reference_material": "Electronic assembly",
            "local_uom": "Each",
            "reference_packaging": "Each",
            "origin_master": "CN",
            "origin_supplier": "CN",
            "lifecycle": "Promo",
            "launch_price": True,
            "launch_description": True,
            "launch_image": True,
            "launch_compliance": False,
            "launch_stock": True,
            "old_cost": 72.00,
            "new_cost": 88.00,
            "current_price": 119.00,
            "target_margin_pct": 25.0,
            "replacement_sku": "",
            "sales_quotes_old_sku": 0,
            "owner": "Campaign owner",
        },
        {
            "item_id": "PM-410",
            "product": "Hydronic balancing valve",
            "local_category": "Controls",
            "reference_class": "Valve and flow-control component",
            "reference_code": "8481.80",
            "local_material": "Brass",
            "reference_material": "Base metal",
            "local_uom": "Each",
            "reference_packaging": "Each",
            "origin_master": "IT",
            "origin_supplier": "IT",
            "lifecycle": "Active",
            "launch_price": True,
            "launch_description": True,
            "launch_image": True,
            "launch_compliance": True,
            "launch_stock": True,
            "old_cost": 58.00,
            "new_cost": 64.00,
            "current_price": 94.00,
            "target_margin_pct": 26.0,
            "replacement_sku": "",
            "sales_quotes_old_sku": 0,
            "owner": "Product ops",
        },
        {
            "item_id": "PM-515",
            "product": "Condensate pump kit",
            "local_category": "Maintenance",
            "reference_class": "Liquid pump assembly",
            "reference_code": "8413.70",
            "local_material": "Plastic",
            "reference_material": "Electromechanical assembly",
            "local_uom": "Each",
            "reference_packaging": "Set/kit",
            "origin_master": "PL",
            "origin_supplier": "CZ",
            "lifecycle": "Active",
            "launch_price": True,
            "launch_description": False,
            "launch_image": False,
            "launch_compliance": False,
            "launch_stock": True,
            "old_cost": 43.00,
            "new_cost": 52.00,
            "current_price": 72.00,
            "target_margin_pct": 27.0,
            "replacement_sku": "",
            "sales_quotes_old_sku": 0,
            "owner": "Catalog team",
        },
        {
            "item_id": "PM-730",
            "product": "Expansion vessel bracket",
            "local_category": "Install parts",
            "reference_class": "Base-metal mounting article",
            "reference_code": "7326.90",
            "local_material": "Steel",
            "reference_material": "Steel",
            "local_uom": "Each",
            "reference_packaging": "Each",
            "origin_master": "SE",
            "origin_supplier": "SE",
            "lifecycle": "Phase-out",
            "launch_price": True,
            "launch_description": True,
            "launch_image": True,
            "launch_compliance": True,
            "launch_stock": True,
            "old_cost": 15.50,
            "new_cost": 18.50,
            "current_price": 28.00,
            "target_margin_pct": 25.0,
            "replacement_sku": "PM-731",
            "sales_quotes_old_sku": 12,
            "owner": "Product ops",
        },
        {
            "item_id": "PM-760",
            "product": "Legacy controller faceplate",
            "local_category": "Legacy",
            "reference_class": "Plastic enclosure part",
            "reference_code": "3926.90",
            "local_material": "Aluminium",
            "reference_material": "Plastic",
            "local_uom": "Each",
            "reference_packaging": "Each",
            "origin_master": "",
            "origin_supplier": "CN",
            "lifecycle": "Phase-out",
            "launch_price": True,
            "launch_description": False,
            "launch_image": False,
            "launch_compliance": False,
            "launch_stock": True,
            "old_cost": 17.00,
            "new_cost": 21.00,
            "current_price": 31.00,
            "target_margin_pct": 24.0,
            "replacement_sku": "PM-761",
            "sales_quotes_old_sku": 28,
            "owner": "Lifecycle owner",
        },
        {
            "item_id": "PM-900",
            "product": "Discontinued wall sensor",
            "local_category": "Legacy",
            "reference_class": "Electronic sensor apparatus",
            "reference_code": "9026.80",
            "local_material": "Plastic",
            "reference_material": "Electronic assembly",
            "local_uom": "Each",
            "reference_packaging": "Each",
            "origin_master": "CN",
            "origin_supplier": "",
            "lifecycle": "Discontinued",
            "launch_price": False,
            "launch_description": False,
            "launch_image": False,
            "launch_compliance": False,
            "launch_stock": True,
            "old_cost": 29.00,
            "new_cost": 36.00,
            "current_price": 41.00,
            "target_margin_pct": 22.0,
            "replacement_sku": "",
            "sales_quotes_old_sku": 46,
            "owner": "Lifecycle owner",
        },
        {
            "item_id": "PM-940",
            "product": "Obsolete mounting rail",
            "local_category": "Legacy",
            "reference_class": "Base-metal mounting article",
            "reference_code": "7326.90",
            "local_material": "Unknown",
            "reference_material": "Steel",
            "local_uom": "Meter",
            "reference_packaging": "Each",
            "origin_master": "",
            "origin_supplier": "",
            "lifecycle": "Obsolete",
            "launch_price": False,
            "launch_description": False,
            "launch_image": False,
            "launch_compliance": False,
            "launch_stock": True,
            "old_cost": 6.20,
            "new_cost": 7.50,
            "current_price": 8.25,
            "target_margin_pct": 20.0,
            "replacement_sku": "PM-941",
            "sales_quotes_old_sku": 18,
            "owner": "Lifecycle owner",
        },
    ]

    df = pd.DataFrame(records)
    df["as_of"] = today
    launch_cols = [
        "launch_price",
        "launch_description",
        "launch_image",
        "launch_compliance",
        "launch_stock",
    ]
    df["launch_ready_score"] = (df[launch_cols].sum(axis=1) / len(launch_cols) * 100).round(0).astype(int)
    df["class_mismatch"] = ~df.apply(
        lambda row: str(row.local_category).lower() in str(row.reference_class).lower()
        or (
            row.local_category in ["Controls", "Campaign"]
            and any(term in row.reference_class.lower() for term in ["valve", "instrument"])
        )
        or (
            row.local_category in ["Install parts", "Legacy"]
            and any(term in row.reference_class.lower() for term in ["mounting", "enclosure", "sensor"])
        )
        or (
            row.local_category == "Maintenance"
            and any(term in row.reference_class.lower() for term in ["filter", "pump"])
        ),
        axis=1,
    )
    df["material_mismatch"] = ~df.apply(
        lambda row: row.local_material == row.reference_material
        or row.local_material in row.reference_material
        or row.reference_material in ["Base metal", "Electronic assembly", "Electromechanical assembly"],
        axis=1,
    )
    df["origin_issue"] = (
        df["origin_master"].eq("")
        | df["origin_supplier"].eq("")
        | df["origin_master"].ne(df["origin_supplier"])
    )
    df["packaging_mismatch"] = ~df.apply(
        lambda row: row.local_uom == row.reference_packaging
        or (row.local_uom == "Kit" and row.reference_packaging == "Set/kit"),
        axis=1,
    )
    df["cost_change_pct"] = ((df["new_cost"] - df["old_cost"]) / df["old_cost"] * 100).round(1)
    df["margin_after_cost_pct"] = ((df["current_price"] - df["new_cost"]) / df["current_price"] * 100).round(1)
    df["needs_reprice"] = (
        (df["cost_change_pct"].abs() >= 10)
        | (df["margin_after_cost_pct"] < df["target_margin_pct"])
    )
    df["replacement_gap"] = (
        df["lifecycle"].isin(["Phase-out", "Discontinued", "Obsolete"])
        & (df["sales_quotes_old_sku"] > 0)
        & (df["replacement_sku"].eq(""))
    )
    df["data_conflict_count"] = df[
        ["class_mismatch", "material_mismatch", "origin_issue", "packaging_mismatch"]
    ].sum(axis=1)
    df["governance_issue_count"] = df[
        [
            "class_mismatch",
            "material_mismatch",
            "origin_issue",
            "packaging_mismatch",
            "needs_reprice",
            "replacement_gap",
        ]
    ].sum(axis=1) + (df["launch_ready_score"] < 80).astype(int)
    df["governance_status"] = "OK"
    df.loc[df["governance_issue_count"].between(1, 2), "governance_status"] = "Review"
    df.loc[df["governance_issue_count"].ge(3), "governance_status"] = "Critical"
    df["workflow_stage"] = "Monitor"
    df.loc[df["launch_ready_score"] < 80, "workflow_stage"] = "Launch readiness"
    df.loc[df["needs_reprice"], "workflow_stage"] = "Reprice"
    df.loc[df["data_conflict_count"].gt(0), "workflow_stage"] = "Data stewardship"
    df.loc[df["replacement_gap"], "workflow_stage"] = "Lifecycle mapping"
    df["recommended_action"] = "No governance action needed"
    df.loc[df["launch_ready_score"] < 80, "recommended_action"] = "Complete launch checklist before channel publish"
    df.loc[df["needs_reprice"], "recommended_action"] = "Review supplier cost change and reset price floor"
    df.loc[df["data_conflict_count"].gt(0), "recommended_action"] = "Review local master data against classification reference"
    df.loc[df["replacement_gap"], "recommended_action"] = "Assign replacement SKU and block old-SKU quoting"
    return df.sort_values(["governance_issue_count", "cost_change_pct"], ascending=[False, False])


def product_governance_payload(df: pd.DataFrame) -> dict:
    return {
        "control": "product_data_governance",
        "source": "synthetic PIM, supplier, and classification reference checks",
        "classification_note": (
            "Reference codes are used to detect product-master contradictions; "
            "they are not treated as binding customs classifications."
        ),
        "as_of": str(df["as_of"].iloc[0]),
        "summary": {
            "products_checked": int(len(df)),
            "classification_conflicts": int(df["data_conflict_count"].gt(0).sum()),
            "launch_not_ready": int((df["launch_ready_score"] < 80).sum()),
            "reprice_needed": int(df["needs_reprice"].sum()),
            "replacement_gaps": int(df["replacement_gap"].sum()),
            "critical_items": int(df["governance_status"].eq("Critical").sum()),
        },
        "actions": [
            {
                "item_id": row.item_id,
                "product": row.product,
                "owner": row.owner,
                "stage": row.workflow_stage,
                "status": row.governance_status,
                "reference_code": row.reference_code,
                "launch_ready_score": int(row.launch_ready_score),
                "cost_change_pct": round(float(row.cost_change_pct), 1),
                "action": row.recommended_action,
            }
            for row in df[df["governance_status"].ne("OK")].itertuples()
        ],
    }


@st.cache_data
def build_stock_forecast_data(
    today: date | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if today is None:
        today = date.today()

    items = pd.DataFrame(
        [
            {
                "item_id": "PM-100",
                "product": "Smart valve actuator",
                "category": "Controls",
                "current_stock": 420,
                "reorder_point": 160,
                "incoming_qty": 260,
                "lead_time_days": 12,
                "supplier": "Nordic Components",
            },
            {
                "item_id": "PM-220",
                "product": "Filter replacement kit",
                "category": "Maintenance",
                "current_stock": 280,
                "reorder_point": 140,
                "incoming_qty": 180,
                "lead_time_days": 8,
                "supplier": "Field Supply Oy",
            },
            {
                "item_id": "PM-340",
                "product": "Sensor calibration bundle",
                "category": "Service parts",
                "current_stock": 190,
                "reorder_point": 90,
                "incoming_qty": 120,
                "lead_time_days": 16,
                "supplier": "Precision Labs",
            },
            {
                "item_id": "PM-480",
                "product": "Weekly promo thermostat",
                "category": "Campaign",
                "current_stock": 140,
                "reorder_point": 110,
                "incoming_qty": 220,
                "lead_time_days": 10,
                "supplier": "Comfort Devices",
            },
        ]
    )

    days = pd.date_range(today - timedelta(days=180), today - timedelta(days=1), freq="D")
    rows = []
    base_demand = {"PM-100": 9.5, "PM-220": 13.0, "PM-340": 6.0, "PM-480": 8.0}
    for item in items.itertuples():
        seed = int(hashlib.sha256(item.item_id.encode("utf-8")).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        for ds in days:
            weekday = 1.18 if ds.weekday() in (0, 1, 2) else 0.92
            trend = 1 + ((ds.date() - (today - timedelta(days=180))).days / 180) * 0.12
            campaign = 1.0
            if item.item_id == "PM-480" and ds >= pd.Timestamp(today - timedelta(days=28)):
                campaign = 1.45
            noise = rng.normal(0, 1.6)
            demand = max(0, base_demand[item.item_id] * weekday * trend * campaign + noise)
            rows.append(
                {
                    "ds": ds,
                    "y": round(float(demand), 2),
                    "item_id": item.item_id,
                    "product": item.product,
                }
            )

    return items, pd.DataFrame(rows)


@st.cache_data
def forecast_stock_for_item(
    item_id: str, current_stock: int, incoming_qty: int, lead_time_days: int, horizon: int = 45
) -> tuple[pd.DataFrame, str]:
    today = date.today()
    _, demand_history = build_stock_forecast_data(today)
    history = demand_history[demand_history["item_id"] == item_id][["ds", "y"]].copy()

    if Prophet is not None:
        model = Prophet(
            weekly_seasonality=True,
            daily_seasonality=False,
            yearly_seasonality=False,
            interval_width=0.8,
        )
        model.fit(history)
        future = model.make_future_dataframe(periods=horizon)
        forecast = model.predict(future).tail(horizon)
        forecast_df = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
        model_label = "Prophet"
    else:
        recent = history.tail(42).copy()
        baseline = float(recent["y"].rolling(14, min_periods=7).mean().iloc[-1])
        future_dates = pd.date_range(today, periods=horizon, freq="D")
        rows = []
        for ds in future_dates:
            weekday = 1.16 if ds.weekday() in (0, 1, 2) else 0.94
            yhat = max(0, baseline * weekday)
            rows.append(
                {
                    "ds": ds,
                    "yhat": yhat,
                    "yhat_lower": max(0, yhat * 0.78),
                    "yhat_upper": yhat * 1.22,
                }
            )
        forecast_df = pd.DataFrame(rows)
        model_label = "Fallback moving average"

    forecast_df["yhat"] = forecast_df["yhat"].clip(lower=0)
    forecast_df["yhat_lower"] = forecast_df["yhat_lower"].clip(lower=0)
    forecast_df["yhat_upper"] = forecast_df["yhat_upper"].clip(lower=0)

    projected = []
    stock = float(current_stock)
    incoming_date = pd.Timestamp(today + timedelta(days=lead_time_days))
    for row in forecast_df.itertuples():
        stock -= float(row.yhat)
        if pd.Timestamp(row.ds).normalize() == incoming_date.normalize():
            stock += incoming_qty
        projected.append(max(stock, 0))
    forecast_df["projected_stock"] = projected
    return forecast_df, model_label


def stock_status_label(reorder_days: int | None, stockout_days: int | None) -> str:
    if stockout_days is not None and stockout_days <= 14:
        return "Critical"
    if reorder_days is not None and reorder_days <= 21:
        return "Warning"
    return "OK"


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


@st.cache_resource
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
    seed_text = f"{job_type}:{region}".encode("utf-8")
    seed = int(hashlib.sha256(seed_text).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
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

    scenario_presets = {
        "Market-aligned": {
            "job_type": "HVAC",
            "region": "West",
            "season": "Summer",
            "complexity": 6.5,
            "materials": 3400,
            "labour": 52,
            "target_margin": 0.18,
            "market_weight": 10,
        },
        "Conservative": {
            "job_type": "Plumbing",
            "region": "Midwest",
            "season": "Spring",
            "complexity": 4.8,
            "materials": 2200,
            "labour": 36,
            "target_margin": 0.15,
            "market_weight": 20,
        },
        "Growth": {
            "job_type": "Electrical",
            "region": "Southeast",
            "season": "Fall",
            "complexity": 5.8,
            "materials": 2800,
            "labour": 44,
            "target_margin": 0.12,
            "market_weight": 30,
        },
        "Urgent service": {
            "job_type": "Renovation",
            "region": "Northeast",
            "season": "Winter",
            "complexity": 8.2,
            "materials": 7600,
            "labour": 96,
            "target_margin": 0.24,
            "market_weight": 5,
        },
    }
    preset_name = st.sidebar.selectbox(
        "Scenario preset", list(scenario_presets.keys()), index=0
    )
    preset = scenario_presets[preset_name]

    job_types = ["Electrical", "HVAC", "Plumbing", "Renovation", "Landscaping"]
    regions = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]
    seasons = ["Winter", "Spring", "Summer", "Fall"]

    job_type = st.sidebar.selectbox(
        "Job Type",
        job_types,
        index=job_types.index(preset["job_type"]),
    )
    region = st.sidebar.selectbox(
        "Region", regions, index=regions.index(preset["region"])
    )
    season = st.sidebar.selectbox(
        "Season", seasons, index=seasons.index(preset["season"])
    )
    complexity = st.sidebar.slider(
        "Complexity",
        min_value=1.0,
        max_value=10.0,
        value=preset["complexity"],
        step=0.1,
    )
    materials = st.sidebar.slider(
        "Materials estimate ($)",
        min_value=200,
        max_value=20000,
        value=preset["materials"],
        step=100,
    )
    labour = st.sidebar.slider(
        "Labour hours", min_value=4, max_value=300, value=preset["labour"], step=1
    )
    target_margin = st.sidebar.slider(
        "Target margin",
        min_value=0.05,
        max_value=0.35,
        value=preset["target_margin"],
        step=0.01,
        format="%.0f%%",
    )

    st.sidebar.markdown("### Market Intel")
    market_weight = st.sidebar.slider(
        "Competitor price weight",
        min_value=0,
        max_value=30,
        value=preset["market_weight"],
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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(
        [
            "Quote",
            "Data",
            "History",
            "Why",
            "Product Check",
            "Product Health",
            "Governance",
            "Buckets",
            "Stock Forecast",
            "Handoff",
        ]
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
            f'<span style="display:inline-block;margin-top:12px;font-family:var(--mono);font-size:10px;'
            f'letter-spacing:0.08em;text-transform:uppercase;color:#0F766E;background:#CCFBF1;'
            f'border:1px solid #0F766E;padding:4px 10px;">Synthetic data · not real prices</span>'
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

        st.markdown(
            f'<div style="display:grid;grid-template-columns:repeat(4,minmax(140px,1fr));'
            f'border:1px solid #0A1F24;border-top:0;margin-bottom:28px;">'
            f'<div style="padding:14px 16px;border-right:1px solid #DDD6C5;">'
            f'<span style="font-family:var(--mono);font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:#1B3F47;">Model mid</span>'
            f'<div style="font-family:var(--serif);font-size:28px;letter-spacing:-0.02em;">{_fmt(mid)}</div></div>'
            f'<div style="padding:14px 16px;border-right:1px solid #DDD6C5;">'
            f'<span style="font-family:var(--mono);font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:#1B3F47;">Catalog total</span>'
            f'<div style="font-family:var(--serif);font-size:28px;letter-spacing:-0.02em;">{_fmt(catalog_price.total)}</div></div>'
            f'<div style="padding:14px 16px;border-right:1px solid #DDD6C5;">'
            f'<span style="font-family:var(--mono);font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:#1B3F47;">Market median</span>'
            f'<div style="font-family:var(--serif);font-size:28px;letter-spacing:-0.02em;">{_fmt(market_median)}</div></div>'
            f'<div style="padding:14px 16px;">'
            f'<span style="font-family:var(--mono);font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:#1B3F47;">Decision rule</span>'
            f'<div style="font-family:var(--serif);font-size:28px;letter-spacing:-0.02em;">{"Review" if review_required else "Proceed"}</div>'
            f'<span style="font-family:var(--mono);font-size:10px;color:#1B3F47;">18% model-gap threshold</span></div>'
            f'</div>',
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
        st.plotly_chart(fig_comp, width="stretch")

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
            st.plotly_chart(fig_wf, width="stretch")

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
            f'<div class="card-item card-item-dark"><span class="eyebrow eyebrow-teal" style="color:#0F766E;">Final recommendation</span>'
            f'<p class="card-num card-num-dark">{_fmt(recommended_price)} <small style="font-size:0.5em;font-style:italic;color:#0F766E;">↗</small></p>'
            f'<span class="card-sub card-sub-dark">65/35 blend + {market_weight}% market pull</span></div>'
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
        st.dataframe(build_data_source_map(), width="stretch", hide_index=True)

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
            st.plotly_chart(fig_radar, width="stretch")

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
        st.plotly_chart(fig_dist, width="stretch")

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
        st.dataframe(out_df, width="stretch", hide_index=True)

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
        st.plotly_chart(fig_trend, width="stretch")

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
    # TAB 5 · PRODUCT CHECK
    # =========================================================================
    with tab5:
        product_checks = build_product_pricing_checks()
        status_counts = product_checks["status"].value_counts()
        ok_count = int(status_counts.get("OK", 0))
        warning_count = int(status_counts.get("Warning", 0))
        critical_count = int(status_counts.get("Critical", 0))
        records_checked = len(product_checks)
        pass_rate = ok_count / max(records_checked, 1) * 100

        st.markdown(
            '<span class="eyebrow">Product pricing control · master data setup</span>'
            "<h2>Before prices go live, <em>prove</em> they are right.</h2>"
            '<p style="font-size:13px;color:#1B3F47;max-width:560px;line-height:1.5;margin-bottom:24px;">'
            "This adapts the product-dashboard idea into the same automation story: compare expected "
            "product prices and validity windows against each sales channel, then route mismatches into "
            "a correction payload before publishing or importing.</p>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="card-grid">'
            f'<div class="card-item"><span class="eyebrow eyebrow-teal">Records checked</span>'
            f'<p class="card-num">{records_checked}</p><span class="card-sub">Product-channel rows</span></div>'
            f'<div class="card-item"><span class="eyebrow eyebrow-teal">OK</span>'
            f'<p class="card-num">{ok_count}</p><span class="card-sub">Ready to publish</span></div>'
            f'<div class="card-item"><span class="eyebrow eyebrow-teal">Warnings</span>'
            f'<p class="card-num">{warning_count}</p><span class="card-sub">Price/date mismatch</span></div>'
            f'<div class="card-item"><span class="eyebrow eyebrow-teal">Critical</span>'
            f'<p class="card-num">{critical_count}</p><span class="card-sub">Inactive today</span></div>'
            f"</div>",
            unsafe_allow_html=True,
        )

        left_check, right_check = st.columns([1.25, 1])
        with left_check:
            st.markdown(
                '<span class="eyebrow">Exception queue</span>',
                unsafe_allow_html=True,
            )
            visible = product_checks.copy()
            visible["Price"] = visible["system_price"].map(lambda x: f"${x:,.2f}")
            visible["Expected"] = visible["expected_price"].map(lambda x: f"${x:,.2f}")
            visible["Gap"] = visible["price_gap_pct"].map(lambda x: f"{x:+.1f}%")
            visible["Margin"] = visible["margin_pct"].map(lambda x: f"{x:.1f}%")
            visible["Window"] = visible.apply(
                lambda row: f"{row['system_start']} → {row['system_end']}", axis=1
            )
            visible["Expected window"] = visible.apply(
                lambda row: f"{row['expected_start']} → {row['expected_end']}",
                axis=1,
            )
            visible["severity"] = visible["status"].map(
                {"Critical": 0, "Warning": 1, "OK": 2}
            )
            table_rows = ""
            for _, row in visible.sort_values(["severity", "item_id"]).iterrows():
                status_class = {
                    "OK": "status-ok",
                    "Warning": "status-warning",
                    "Critical": "status-critical",
                }[row["status"]]
                table_rows += (
                    "<tr>"
                    f"<td><strong>{row['item_id']}</strong><br><span class='check-muted'>{row['product']}</span></td>"
                    f"<td>{row['channel']}</td>"
                    f"<td>{row['Price']}<br><span class='check-muted'>exp {row['Expected']} · {row['Gap']}</span></td>"
                    f"<td>{row['Window']}<br><span class='check-muted'>exp {row['Expected window']}</span></td>"
                    f"<td>{row['Margin']}</td>"
                    f"<td><span class='status-pill {status_class}'>{row['status']}</span><br><span class='check-muted'>{row['issue']}</span></td>"
                    "</tr>"
                )
            st.markdown(
                "<table class='check-table'><thead><tr>"
                "<th>Product</th><th>Channel</th><th>Price</th><th>Validity</th><th>Margin</th><th>Status</th>"
                f"</tr></thead><tbody>{table_rows}</tbody></table>",
                unsafe_allow_html=True,
            )

        with right_check:
            st.markdown(
                '<span class="eyebrow">Channel health</span>',
                unsafe_allow_html=True,
            )
            channel_status = (
                product_checks.groupby(["channel", "status"])
                .size()
                .reset_index(name="Records")
            )
            fig_product = px.bar(
                channel_status,
                x="channel",
                y="Records",
                color="status",
                color_discrete_map={
                    "OK": "#14B8A6",
                    "Warning": "#F97316",
                    "Critical": "#991B1B",
                },
                category_orders={"status": ["OK", "Warning", "Critical"]},
            )
            _apply_theme(fig_product)
            fig_product.update_layout(
                title_text="",
                height=300,
                legend=dict(
                    font=dict(family="Geist Mono, monospace", size=10),
                    title_text="",
                ),
                xaxis_title="",
                yaxis_title="Records",
            )
            st.plotly_chart(fig_product, width="stretch")

            st.markdown(
                '<div style="background:#EAE5DA;border:1px solid #0A1F24;padding:20px;margin-top:18px;">'
                '<span class="eyebrow" style="color:#0F766E;">Control rule</span>'
                f"<p style=\"font-family:'Instrument Serif',serif;font-size:34px;line-height:0.95;letter-spacing:-0.02em;margin:8px 0;\">"
                f"{pass_rate:.0f}% pass rate</p>"
                '<p style="font-size:13px;color:#1B3F47;line-height:1.5;margin:0;">'
                "Critical rows block publishing. Warning rows can be routed to a product manager "
                "for price/date correction before the campaign or catalog import continues.</p></div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<hr style='border:0;border-top:1px solid #0A1F24;margin:32px 0 24px;'>",
            unsafe_allow_html=True,
        )
        payload_col, process_col = st.columns([1, 1])
        with payload_col:
            st.markdown(
                '<span class="eyebrow" style="color:#0F766E;">Correction payload</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<pre class="code-block">{json.dumps(product_correction_payload(product_checks), indent=2)}</pre>',
                unsafe_allow_html=True,
            )

        with process_col:
            st.markdown(
                '<span class="eyebrow" style="color:#0F766E;">Where this fits</span>',
                unsafe_allow_html=True,
            )
            product_process = pd.DataFrame(
                [
                    {
                        "Step": "01",
                        "Control": "Load expected setup",
                        "Result": "Approved price and validity window",
                    },
                    {
                        "Step": "02",
                        "Control": "Compare channels",
                        "Result": "Local, Branch, Online checked",
                    },
                    {
                        "Step": "03",
                        "Control": "Block or correct",
                        "Result": "Critical and warning rows routed",
                    },
                    {
                        "Step": "04",
                        "Control": "Publish",
                        "Result": "Clean records continue to import",
                    },
                ]
            )
            st.dataframe(product_process, width="stretch", hide_index=True)

    # =========================================================================
    # TAB 6 · PRODUCT HEALTH
    # =========================================================================
    with tab6:
        health_df = build_product_health_data()
        master_issues = health_df[health_df["master_data_issue"]]
        returns_issues = health_df[health_df["returns_issue"]]
        scrap_candidates = health_df[health_df["scrap_candidate"]]
        margin_issues = health_df[health_df["margin_issue"]]
        critical_count = int(health_df["health_status"].eq("Critical").sum())
        review_count = int(health_df["health_status"].eq("Review").sum())
        refund_at_risk = float(returns_issues["refund_value"].sum())
        scrap_value = float(scrap_candidates["scrap_value"].sum())

        st.markdown(
            '<span class="eyebrow">Product health · operating exceptions</span>'
            "<h2>One queue for products that are hard to sell, costly to return, or ready to retire.</h2>"
            '<p style="font-size:13px;color:#1B3F47;max-width:660px;line-height:1.5;margin-bottom:24px;">'
            "This combines the product-management controls that usually sit around pricing: catalog "
            "description quality, returns and refund leakage, obsolete stock moving toward scrap, and "
            "margin erosion caused by discounting or stale cost-price alignment.</p>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="card-grid">'
            f'<div class="card-item"><span class="eyebrow eyebrow-teal">Products checked</span>'
            f'<p class="card-num">{len(health_df)}</p><span class="card-sub">{critical_count} critical · {review_count} review</span></div>'
            f'<div class="card-item"><span class="eyebrow eyebrow-teal">Master data issues</span>'
            f'<p class="card-num">{len(master_issues)}</p><span class="card-sub">Description or required field gaps</span></div>'
            f'<div class="card-item"><span class="eyebrow eyebrow-teal">Refund value flagged</span>'
            f'<p class="card-num">${refund_at_risk/1000:.1f}k</p><span class="card-sub">High return/refund products</span></div>'
            f'<div class="card-item"><span class="eyebrow eyebrow-teal">Scrap watch</span>'
            f'<p class="card-num">${scrap_value/1000:.1f}k</p><span class="card-sub">{len(scrap_candidates)} obsolete candidates</span></div>'
            f"</div>",
            unsafe_allow_html=True,
        )

        def health_panel(title: str, rows: pd.DataFrame, score: str, meta: str) -> str:
            body = (
                '<div class="health-row">'
                "<div><strong>No exceptions</strong><br><span class='check-muted'>Queue is clear</span></div>"
                '<div class="health-score">0</div>'
                '<div><span class="status-pill status-ok">OK</span></div>'
                "</div>"
            )
            if not rows.empty:
                body = ""
                for row in rows.head(4).itertuples():
                    status_class = (
                        "status-critical"
                        if row.health_status == "Critical"
                        else "status-warning"
                    )
                    body += (
                        '<div class="health-row">'
                        f"<div><strong>{row.item_id}</strong><br><span class='check-muted'>{row.product}</span></div>"
                        f'<div><span class="health-score">{score(row)}</span><br><span class="check-muted">{meta(row)}</span></div>'
                        f'<div><span class="status-pill {status_class}">{row.health_status}</span></div>'
                        "</div>"
                    )
            return (
                '<div class="health-panel">'
                '<div class="health-panel-head">'
                f'<span class="health-panel-title">{title}</span>'
                f'<span class="bucket-lane-meta">{len(rows)} items</span>'
                "</div>"
                f"{body}</div>"
            )

        panels = (
            health_panel(
                "Master data issues",
                master_issues.sort_values(["description_score", "missing_fields"]),
                lambda row: f"{int(row.description_score)}",
                lambda row: f"{int(row.missing_fields)} missing",
            )
            + health_panel(
                "Returns / refunds",
                returns_issues.sort_values("refund_value", ascending=False),
                lambda row: f"{row.return_rate_pct:.1f}%",
                lambda row: f"${row.refund_value/1000:.1f}k refunds",
            )
            + health_panel(
                "Obsolete / scrap",
                scrap_candidates.sort_values("scrap_value", ascending=False),
                lambda row: f"${row.scrap_value/1000:.1f}k",
                lambda row: f"{int(row.days_since_sale)}d no sale",
            )
            + health_panel(
                "Margin leakage",
                margin_issues.sort_values("margin_pct"),
                lambda row: f"{row.margin_pct:.1f}%",
                lambda row: f"{row.discount_rate_pct:.0f}% discount",
            )
        )
        st.markdown(f'<div class="health-grid">{panels}</div>', unsafe_allow_html=True)

        health_left, health_right = st.columns([1, 1])
        with health_left:
            issue_summary = pd.DataFrame(
                [
                    {
                        "Area": "Master data",
                        "Items": len(master_issues),
                        "Value": 0,
                    },
                    {
                        "Area": "Returns/refunds",
                        "Items": len(returns_issues),
                        "Value": refund_at_risk,
                    },
                    {
                        "Area": "Scrap watch",
                        "Items": len(scrap_candidates),
                        "Value": scrap_value,
                    },
                    {
                        "Area": "Margin leakage",
                        "Items": len(margin_issues),
                        "Value": float(margin_issues["inventory_value"].sum()),
                    },
                ]
            )
            fig_issues = px.bar(
                issue_summary,
                x="Area",
                y="Items",
                color="Area",
                text="Items",
                color_discrete_map={
                    "Master data": "#1B3F47",
                    "Returns/refunds": "#F97316",
                    "Scrap watch": "#991B1B",
                    "Margin leakage": "#14B8A6",
                },
            )
            _apply_theme(fig_issues)
            fig_issues.update_layout(
                title_text="Exception count by product-control area",
                height=330,
                showlegend=False,
                xaxis_title="",
                yaxis_title="Products",
            )
            st.plotly_chart(fig_issues, width="stretch")

        with health_right:
            fig_return_margin = px.scatter(
                health_df,
                x="return_rate_pct",
                y="margin_pct",
                size="refund_value",
                color="health_status",
                hover_name="product",
                hover_data={
                    "item_id": True,
                    "lifecycle": True,
                    "refund_value": ":$,.0f",
                    "discount_rate_pct": ":.1f",
                    "health_status": False,
                },
                color_discrete_map={
                    "OK": "#14B8A6",
                    "Review": "#F97316",
                    "Critical": "#991B1B",
                },
                category_orders={"health_status": ["OK", "Review", "Critical"]},
            )
            fig_return_margin.add_hline(
                y=15,
                line_color="#991B1B",
                line_dash="dash",
                annotation_text="Margin floor",
                annotation_font=dict(
                    family="Geist Mono, monospace", size=10, color="#991B1B"
                ),
            )
            fig_return_margin.add_vline(
                x=8,
                line_color="#F97316",
                line_dash="dash",
                annotation_text="Return threshold",
                annotation_font=dict(
                    family="Geist Mono, monospace", size=10, color="#F97316"
                ),
            )
            _apply_theme(fig_return_margin)
            fig_return_margin.update_layout(
                title_text="Returns against margin floor",
                height=330,
                legend=dict(
                    font=dict(family="Geist Mono, monospace", size=10),
                    title_text="",
                ),
                xaxis_title="Return rate %",
                yaxis_title="Margin %",
            )
            st.plotly_chart(fig_return_margin, width="stretch")

        st.markdown(
            "<hr style='border:0;border-top:1px solid #0A1F24;margin:32px 0 24px;'>",
            unsafe_allow_html=True,
        )
        health_queue_col, health_payload_col = st.columns([1.3, 1])
        with health_queue_col:
            st.markdown(
                '<span class="eyebrow">Unified action queue</span>',
                unsafe_allow_html=True,
            )
            queue = health_df[health_df["issue_count"].gt(0)][
                [
                    "health_status",
                    "item_id",
                    "product",
                    "lifecycle",
                    "description_score",
                    "return_rate_pct",
                    "refund_pct",
                    "margin_pct",
                    "scrap_value",
                    "recommended_action",
                ]
            ].rename(
                columns={
                    "health_status": "Status",
                    "item_id": "Item",
                    "product": "Product",
                    "lifecycle": "Lifecycle",
                    "description_score": "Description score",
                    "return_rate_pct": "Return %",
                    "refund_pct": "Refund %",
                    "margin_pct": "Margin %",
                    "scrap_value": "Scrap value",
                    "recommended_action": "Action",
                }
            )
            st.dataframe(queue, width="stretch", hide_index=True)

        with health_payload_col:
            st.markdown(
                '<span class="eyebrow" style="color:#0F766E;">Health payload</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<pre class="code-block">{json.dumps(product_health_payload(health_df), indent=2)}</pre>',
                unsafe_allow_html=True,
            )

    # =========================================================================
    # TAB 7 · GOVERNANCE
    # =========================================================================
    with tab7:
        governance_df = build_product_governance_data()
        conflicts = governance_df[governance_df["data_conflict_count"].gt(0)]
        launch_not_ready = governance_df[governance_df["launch_ready_score"] < 80]
        reprice_needed = governance_df[governance_df["needs_reprice"]]
        replacement_gaps = governance_df[governance_df["replacement_gap"]]
        critical_governance = governance_df[governance_df["governance_status"].eq("Critical")]

        st.markdown(
            '<span class="eyebrow">Product governance · classification-informed validation</span>'
            "<h2>Use reference data to find contradictions, then route the product to an owner.</h2>"
            '<p style="font-size:13px;color:#1B3F47;max-width:700px;line-height:1.5;margin-bottom:24px;">'
            "This does not claim to classify products for customs. It uses HS-style reference fields as "
            "a governance signal: if the reference class implies a steel mounting article but the local "
            "master says unknown material, meter unit, or missing origin, the product is held for review. "
            "The same view covers launch readiness, supplier cost changes, replacement mapping, and workflow ownership.</p>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="governance-strip">'
            f'<div class="governance-cell"><span class="eyebrow eyebrow-teal">Conflicts</span>'
            f'<strong>{len(conflicts)}</strong><span class="card-sub">Classification reference vs local master</span></div>'
            f'<div class="governance-cell"><span class="eyebrow eyebrow-teal">Launch not ready</span>'
            f'<strong>{len(launch_not_ready)}</strong><span class="card-sub">Missing price, content, compliance, or stock</span></div>'
            f'<div class="governance-cell"><span class="eyebrow eyebrow-teal">Reprice needed</span>'
            f'<strong>{len(reprice_needed)}</strong><span class="card-sub">Supplier cost or margin guardrail</span></div>'
            f'<div class="governance-cell"><span class="eyebrow eyebrow-teal">Replacement gaps</span>'
            f'<strong>{len(replacement_gaps)}</strong><span class="card-sub">Old SKUs still quoted</span></div>'
            f'<div class="governance-cell"><span class="eyebrow eyebrow-teal">Critical</span>'
            f'<strong>{len(critical_governance)}</strong><span class="card-sub">Needs owner action</span></div>'
            f"</div>",
            unsafe_allow_html=True,
        )

        flow_html = (
            '<div class="governance-flow">'
            '<div class="governance-step"><span class="governance-step-num">01 · ingest</span>'
            '<div class="governance-step-title">Read source signals</div>'
            '<p class="governance-step-copy">PIM, supplier file, pricing master, stock, and classification reference.</p></div>'
            '<div class="governance-step"><span class="governance-step-num">02 · compare</span>'
            '<div class="governance-step-title">Find contradictions</div>'
            '<p class="governance-step-copy">Material, category, origin, packaging, and lifecycle conflicts.</p></div>'
            '<div class="governance-step"><span class="governance-step-num">03 · score</span>'
            '<div class="governance-step-title">Score readiness</div>'
            '<p class="governance-step-copy">Launch checklist plus cost-change and substitution risk.</p></div>'
            '<div class="governance-step"><span class="governance-step-num">04 · assign</span>'
            '<div class="governance-step-title">Route owner</div>'
            '<p class="governance-step-copy">Catalog, compliance, lifecycle, campaign, or product operations.</p></div>'
            '<div class="governance-step"><span class="governance-step-num">05 · publish</span>'
            '<div class="governance-step-title">Release or hold</div>'
            '<p class="governance-step-copy">Clean products publish. Exceptions create a controlled handoff.</p></div>'
            "</div>"
        )
        st.markdown(flow_html, unsafe_allow_html=True)

        governance_left, governance_right = st.columns([1.15, 1])
        with governance_left:
            st.markdown(
                '<span class="eyebrow">Classification-informed data conflicts</span>',
                unsafe_allow_html=True,
            )
            conflict_rows = ""
            status_class_map = {
                "OK": "status-ok",
                "Review": "status-warning",
                "Critical": "status-critical",
            }
            for row in conflicts.head(8).itertuples():
                issues = []
                if row.class_mismatch:
                    issues.append("class")
                if row.material_mismatch:
                    issues.append("material")
                if row.origin_issue:
                    issues.append("origin")
                if row.packaging_mismatch:
                    issues.append("unit")
                conflict_rows += (
                    "<tr>"
                    f"<td><strong>{row.item_id}</strong><br><span class='check-muted'>{row.product}</span></td>"
                    f"<td>{row.local_category}<br><span class='check-muted'>{row.local_material} · {row.local_uom}</span></td>"
                    f"<td>{row.reference_class}<br><span class='check-muted'>{row.reference_code} · {row.reference_material} · {row.reference_packaging}</span></td>"
                    f"<td>{row.origin_master or 'Missing'} / {row.origin_supplier or 'Missing'}</td>"
                    f"<td><span class='status-pill {status_class_map[row.governance_status]}'>{row.governance_status}</span><br><span class='check-muted'>{', '.join(issues)}</span></td>"
                    "</tr>"
                )
            st.markdown(
                "<table class='check-table'><thead><tr>"
                "<th>Product</th><th>Local master</th><th>Reference signal</th><th>Origin</th><th>Status</th>"
                f"</tr></thead><tbody>{conflict_rows}</tbody></table>",
                unsafe_allow_html=True,
            )

        with governance_right:
            st.markdown(
                '<span class="eyebrow">Launch readiness vs cost change</span>',
                unsafe_allow_html=True,
            )
            fig_governance = px.scatter(
                governance_df,
                x="cost_change_pct",
                y="launch_ready_score",
                size="governance_issue_count",
                color="workflow_stage",
                hover_name="product",
                hover_data={
                    "item_id": True,
                    "reference_code": True,
                    "margin_after_cost_pct": ":.1f",
                    "sales_quotes_old_sku": True,
                    "workflow_stage": False,
                },
                color_discrete_map={
                    "Monitor": "#14B8A6",
                    "Launch readiness": "#F97316",
                    "Reprice": "#0F766E",
                    "Data stewardship": "#1B3F47",
                    "Lifecycle mapping": "#991B1B",
                },
            )
            fig_governance.add_hline(
                y=80,
                line_color="#F97316",
                line_dash="dash",
                annotation_text="Launch threshold",
                annotation_font=dict(
                    family="Geist Mono, monospace", size=10, color="#F97316"
                ),
            )
            fig_governance.add_vline(
                x=10,
                line_color="#991B1B",
                line_dash="dash",
                annotation_text="Cost-change review",
                annotation_font=dict(
                    family="Geist Mono, monospace", size=10, color="#991B1B"
                ),
            )
            _apply_theme(fig_governance)
            fig_governance.update_layout(
                title_text="Governance risk map",
                height=360,
                legend=dict(
                    font=dict(family="Geist Mono, monospace", size=10),
                    title_text="",
                ),
                xaxis_title="Supplier cost change %",
                yaxis_title="Launch readiness score",
            )
            st.plotly_chart(fig_governance, width="stretch")

        st.markdown(
            "<hr style='border:0;border-top:1px solid #0A1F24;margin:32px 0 24px;'>",
            unsafe_allow_html=True,
        )
        gov_queue_col, gov_payload_col = st.columns([1.3, 1])
        with gov_queue_col:
            st.markdown(
                '<span class="eyebrow">Owner workflow queue</span>',
                unsafe_allow_html=True,
            )
            workflow_queue = governance_df[governance_df["governance_status"].ne("OK")][
                [
                    "governance_status",
                    "item_id",
                    "product",
                    "owner",
                    "workflow_stage",
                    "launch_ready_score",
                    "cost_change_pct",
                    "margin_after_cost_pct",
                    "replacement_sku",
                    "sales_quotes_old_sku",
                    "recommended_action",
                ]
            ].rename(
                columns={
                    "governance_status": "Status",
                    "item_id": "Item",
                    "product": "Product",
                    "owner": "Owner",
                    "workflow_stage": "Stage",
                    "launch_ready_score": "Launch score",
                    "cost_change_pct": "Cost change %",
                    "margin_after_cost_pct": "Margin after cost %",
                    "replacement_sku": "Replacement",
                    "sales_quotes_old_sku": "Old-SKU quotes",
                    "recommended_action": "Action",
                }
            )
            st.dataframe(workflow_queue, width="stretch", hide_index=True)

        with gov_payload_col:
            st.markdown(
                '<span class="eyebrow" style="color:#0F766E;">Governance payload</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<pre class="code-block">{json.dumps(product_governance_payload(governance_df), indent=2)}</pre>',
                unsafe_allow_html=True,
            )

    # =========================================================================
    # TAB 8 · BUCKETS
    # =========================================================================
    with tab8:
        bucket_df = build_inventory_bucket_data()
        bucket_summary = (
            bucket_df.groupby(["bucket", "bucket_name"], as_index=False)
            .agg(
                items=("item_id", "count"),
                stock_units=("current_stock", "sum"),
                inventory_value=("inventory_value", "sum"),
                weekly_velocity=("weekly_velocity", "sum"),
            )
            .sort_values("bucket")
        )
        fast_items = bucket_df[bucket_df["bucket"].eq("A")]
        stale_items = bucket_df[bucket_df["bucket"].eq("D")]
        total_value = float(bucket_df["inventory_value"].sum())
        stale_value = float(stale_items["inventory_value"].sum())
        stale_share = stale_value / max(total_value, 1) * 100
        fast_velocity = float(fast_items["weekly_velocity"].sum())

        st.markdown(
            '<span class="eyebrow">Product bucketing · inventory velocity</span>'
            "<h2>A shows fast movers. B and C show the middle. D is <em>stale</em>.</h2>"
            '<p style="font-size:13px;color:#1B3F47;max-width:620px;line-height:1.5;margin-bottom:24px;">'
            "This tab turns the inventory ledger into operating buckets. The rule blends recent unit "
            "movement, sell-through, days on hand, and days since last sale so the demo can show where "
            "pricing should protect supply, test demand, or clear stale stock.</p>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="card-grid">'
            f'<div class="card-item"><span class="eyebrow eyebrow-teal">A bucket</span>'
            f'<p class="card-num">{len(fast_items)}</p><span class="card-sub">{fast_velocity:.0f} units/week · fast movers</span></div>'
            f'<div class="card-item"><span class="eyebrow eyebrow-teal">B bucket</span>'
            f'<p class="card-num">{int(bucket_summary.loc[bucket_summary["bucket"].eq("B"), "items"].sum())}</p><span class="card-sub">Steady movers to maintain</span></div>'
            f'<div class="card-item"><span class="eyebrow eyebrow-teal">C bucket</span>'
            f'<p class="card-num">{int(bucket_summary.loc[bucket_summary["bucket"].eq("C"), "items"].sum())}</p><span class="card-sub">Slow movers to manage</span></div>'
            f'<div class="card-item"><span class="eyebrow eyebrow-teal">D stale value</span>'
            f'<p class="card-num">${stale_value/1000:.1f}k</p><span class="card-sub">{stale_share:.0f}% of stock value</span></div>'
            f"</div>",
            unsafe_allow_html=True,
        )

        bucket_left, bucket_right = st.columns([1.2, 1])
        with bucket_left:
            st.markdown(
                '<span class="eyebrow">Bucket board</span>',
                unsafe_allow_html=True,
            )
            bucket_class = {
                "A": "status-bucket-a",
                "B": "status-bucket-b",
                "C": "status-bucket-c",
                "D": "status-bucket-d",
            }
            bucket_labels = {
                "A": "A fast movers",
                "B": "B steady movers",
                "C": "C slow movers",
                "D": "D stale stock",
            }
            bucket_html = ""
            for bucket in ["A", "B", "C", "D"]:
                subset = bucket_df[bucket_df["bucket"].eq(bucket)].sort_values(
                    "weekly_velocity", ascending=False
                )
                units = int(subset["current_stock"].sum())
                value = float(subset["inventory_value"].sum())
                bucket_html += (
                    '<div class="bucket-lane">'
                    '<div class="bucket-lane-head">'
                    f'<span class="bucket-lane-title"><span class="status-pill {bucket_class[bucket]}">{bucket}</span> {bucket_labels[bucket]}</span>'
                    f'<span class="bucket-lane-meta">{len(subset)} SKUs · {units:,} units · ${value/1000:.1f}k</span>'
                    "</div>"
                )
                for row in subset.itertuples():
                    bucket_html += (
                        '<div class="bucket-sku">'
                        f"<div><strong>{row.item_id}</strong><br><span class='check-muted'>{row.product}</span></div>"
                        f'<div><span class="bucket-measure">Velocity</span><br>{row.weekly_velocity:.1f}/wk</div>'
                        f'<div><span class="bucket-measure">On hand</span><br>{int(row.current_stock):,}</div>'
                        f'<div><span class="bucket-measure">Last sale</span><br>{int(row.days_since_sale)}d</div>'
                        "</div>"
                    )
                bucket_html += "</div>"
            st.markdown(bucket_html, unsafe_allow_html=True)

        with bucket_right:
            st.markdown(
                '<span class="eyebrow">Velocity vs stock value</span>',
                unsafe_allow_html=True,
            )
            fig_bucket = px.scatter(
                bucket_df,
                x="inventory_value",
                y="weekly_velocity",
                size="current_stock",
                color="bucket_name",
                hover_name="product",
                hover_data={
                    "item_id": True,
                    "current_stock": True,
                    "days_on_hand": True,
                    "days_since_sale": True,
                    "inventory_value": ":$,.0f",
                    "weekly_velocity": ":.1f",
                    "bucket_name": False,
                },
                color_discrete_map={
                    "A fast": "#14B8A6",
                    "B steady": "#1B3F47",
                    "C slow": "#F97316",
                    "D stale": "#991B1B",
                },
                category_orders={
                    "bucket_name": ["A fast", "B steady", "C slow", "D stale"]
                },
            )
            _apply_theme(fig_bucket)
            fig_bucket.update_layout(
                title_text="Stock tied up by movement bucket",
                height=360,
                legend=dict(
                    font=dict(family="Geist Mono, monospace", size=10),
                    title_text="",
                ),
                xaxis_title="Inventory value",
                yaxis_title="Units/week",
            )
            fig_bucket.update_xaxes(tickprefix="$", separatethousands=True)
            st.plotly_chart(fig_bucket, width="stretch")

            st.markdown(
                '<div style="background:#EAE5DA;border:1px solid #0A1F24;padding:20px;margin-top:18px;">'
                '<span class="eyebrow" style="color:#0F766E;">Bucket action</span>'
                "<p style=\"font-family:'Instrument Serif',serif;font-size:32px;line-height:0.95;letter-spacing:-0.02em;margin:8px 0;\">"
                "Clear D before buying more C</p>"
                '<p style="font-size:13px;color:#1B3F47;line-height:1.5;margin:0;">'
                "A items need availability protection. B items are stable enough for normal replenishment. "
                "C items need tighter buys or bundles. D items should be marked down, returned, or removed.</p></div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<hr style='border:0;border-top:1px solid #0A1F24;margin:32px 0 24px;'>",
            unsafe_allow_html=True,
        )
        bucket_table_col, bucket_payload_col = st.columns([1.25, 1])
        with bucket_table_col:
            st.markdown(
                '<span class="eyebrow">Bucket detail</span>',
                unsafe_allow_html=True,
            )
            detail = bucket_df[
                [
                    "bucket_name",
                    "item_id",
                    "product",
                    "category",
                    "current_stock",
                    "weekly_velocity",
                    "sell_through_28d",
                    "days_on_hand",
                    "days_since_sale",
                    "action",
                ]
            ].rename(
                columns={
                    "bucket_name": "Bucket",
                    "item_id": "Item",
                    "product": "Product",
                    "category": "Category",
                    "current_stock": "Stock",
                    "weekly_velocity": "Units/week",
                    "sell_through_28d": "28d sell-through %",
                    "days_on_hand": "Days on hand",
                    "days_since_sale": "Days since sale",
                    "action": "Action",
                }
            )
            st.dataframe(detail, width="stretch", hide_index=True)

        with bucket_payload_col:
            st.markdown(
                '<span class="eyebrow" style="color:#0F766E;">Bucket payload</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<pre class="code-block">{json.dumps(inventory_bucket_payload(bucket_df), indent=2)}</pre>',
                unsafe_allow_html=True,
            )

    # =========================================================================
    # TAB 9 · STOCK FORECAST
    # =========================================================================
    with tab9:
        stock_items, demand_history = build_stock_forecast_data()
        item_labels = {
            f"{row.product} ({row.item_id})": row.item_id for row in stock_items.itertuples()
        }

        st.markdown(
            '<span class="eyebrow">Product stock forecast · demand planning</span>'
            "<h2>Pricing only works if stock can <em>keep up</em>.</h2>"
            '<p style="font-size:13px;color:#1B3F47;max-width:580px;line-height:1.5;margin-bottom:24px;">'
            "This extends the product-management view from setup correctness into stock readiness. "
            "Historical daily demand is forecast with Prophet, then translated into projected stock "
            "against reorder point, lead time, and incoming replenishment.</p>",
            unsafe_allow_html=True,
        )

        selected_label = st.selectbox("Forecast product", list(item_labels.keys()))
        selected_id = item_labels[selected_label]
        selected_item = stock_items[stock_items["item_id"] == selected_id].iloc[0]
        stock_forecast, forecast_model = forecast_stock_for_item(
            selected_id,
            int(selected_item["current_stock"]),
            int(selected_item["incoming_qty"]),
            int(selected_item["lead_time_days"]),
        )

        below_reorder = stock_forecast[
            stock_forecast["projected_stock"] <= selected_item["reorder_point"]
        ]
        stockout = stock_forecast[stock_forecast["projected_stock"] <= 0]
        reorder_days = (
            int((below_reorder["ds"].iloc[0].date() - date.today()).days)
            if not below_reorder.empty
            else None
        )
        stockout_days = (
            int((stockout["ds"].iloc[0].date() - date.today()).days)
            if not stockout.empty
            else None
        )
        stock_status = stock_status_label(reorder_days, stockout_days)
        status_class = {
            "OK": "status-ok",
            "Warning": "status-warning",
            "Critical": "status-critical",
        }[stock_status]
        avg_demand = demand_history[demand_history["item_id"] == selected_id]["y"].tail(28).mean()

        st.markdown(
            f'<div class="card-grid">'
            f'<div class="card-item"><span class="eyebrow eyebrow-teal">Current stock</span>'
            f'<p class="card-num">{int(selected_item["current_stock"])}</p><span class="card-sub">Units on hand</span></div>'
            f'<div class="card-item"><span class="eyebrow eyebrow-teal">Reorder point</span>'
            f'<p class="card-num">{int(selected_item["reorder_point"])}</p><span class="card-sub">Control threshold</span></div>'
            f'<div class="card-item"><span class="eyebrow eyebrow-teal">Avg demand</span>'
            f'<p class="card-num">{avg_demand:.1f}</p><span class="card-sub">Units/day · last 28 days</span></div>'
            f'<div class="card-item"><span class="eyebrow eyebrow-teal">Stock status</span>'
            f'<p class="card-num" style="font-size:34px;"><span class="status-pill {status_class}">{stock_status}</span></p>'
            f'<span class="card-sub">{forecast_model} · 45-day horizon</span></div>'
            f"</div>",
            unsafe_allow_html=True,
        )

        if Prophet is None:
            st.warning(
                "Prophet is not installed in the current environment, so this preview is using a moving-average fallback. "
                "The deployed app will use Prophet when `prophet` is installed from requirements."
            )

        chart_left, chart_right = st.columns([1, 1])
        with chart_left:
            hist = demand_history[demand_history["item_id"] == selected_id].tail(90)
            fig_demand = go.Figure()
            fig_demand.add_trace(
                go.Scatter(
                    x=hist["ds"],
                    y=hist["y"],
                    mode="lines",
                    line=dict(color="#1B3F47", width=1.5),
                    name="Actual demand",
                )
            )
            fig_demand.add_trace(
                go.Scatter(
                    x=stock_forecast["ds"],
                    y=stock_forecast["yhat_upper"],
                    mode="lines",
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
            fig_demand.add_trace(
                go.Scatter(
                    x=stock_forecast["ds"],
                    y=stock_forecast["yhat_lower"],
                    mode="lines",
                    fill="tonexty",
                    fillcolor="rgba(20,184,166,0.18)",
                    line=dict(width=0),
                    name="Forecast interval",
                )
            )
            fig_demand.add_trace(
                go.Scatter(
                    x=stock_forecast["ds"],
                    y=stock_forecast["yhat"],
                    mode="lines",
                    line=dict(color="#14B8A6", width=2.4),
                    name="Forecast demand",
                )
            )
            _apply_theme(fig_demand)
            fig_demand.update_layout(
                title_text="Daily demand forecast",
                height=340,
                legend=dict(font=dict(family="Geist Mono, monospace", size=10)),
                xaxis_title="",
                yaxis_title="Units/day",
            )
            st.plotly_chart(fig_demand, width="stretch")

        with chart_right:
            fig_stock = go.Figure()
            fig_stock.add_trace(
                go.Scatter(
                    x=stock_forecast["ds"],
                    y=stock_forecast["projected_stock"],
                    mode="lines",
                    fill="tozeroy",
                    fillcolor="rgba(45,212,191,0.16)",
                    line=dict(color="#0A1F24", width=2.2),
                    name="Projected stock",
                )
            )
            fig_stock.add_hline(
                y=selected_item["reorder_point"],
                line_color="#F97316",
                line_dash="dash",
                annotation_text=f"Reorder point {int(selected_item['reorder_point'])}",
                annotation_font=dict(
                    family="Geist Mono, monospace", size=10, color="#F97316"
                ),
            )
            incoming_date = pd.Timestamp(
                date.today() + timedelta(days=int(selected_item["lead_time_days"]))
            )
            fig_stock.add_shape(
                type="line",
                x0=incoming_date,
                x1=incoming_date,
                y0=0,
                y1=1,
                xref="x",
                yref="paper",
                line=dict(color="#14B8A6", width=1.5, dash="dot"),
            )
            fig_stock.add_annotation(
                x=incoming_date,
                y=1,
                xref="x",
                yref="paper",
                text=f"Incoming +{int(selected_item['incoming_qty'])}",
                showarrow=False,
                yshift=12,
                font=dict(family="Geist Mono, monospace", size=10, color="#14B8A6"),
            )
            _apply_theme(fig_stock)
            fig_stock.update_layout(
                title_text="Projected stock position",
                height=340,
                showlegend=False,
                xaxis_title="",
                yaxis_title="Units",
            )
            st.plotly_chart(fig_stock, width="stretch")

        st.markdown(
            "<hr style='border:0;border-top:1px solid #0A1F24;margin:24px 0;'>",
            unsafe_allow_html=True,
        )

        queue_rows = []
        for item in stock_items.itertuples():
            item_forecast, item_model = forecast_stock_for_item(
                item.item_id,
                int(item.current_stock),
                int(item.incoming_qty),
                int(item.lead_time_days),
            )
            item_reorder = item_forecast[item_forecast["projected_stock"] <= item.reorder_point]
            item_stockout = item_forecast[item_forecast["projected_stock"] <= 0]
            item_reorder_days = (
                int((item_reorder["ds"].iloc[0].date() - date.today()).days)
                if not item_reorder.empty
                else None
            )
            item_stockout_days = (
                int((item_stockout["ds"].iloc[0].date() - date.today()).days)
                if not item_stockout.empty
                else None
            )
            item_status = stock_status_label(item_reorder_days, item_stockout_days)
            queue_rows.append(
                {
                    "Item": item.item_id,
                    "Product": item.product,
                    "Supplier": item.supplier,
                    "Current stock": item.current_stock,
                    "Reorder point": item.reorder_point,
                    "Reorder in": (
                        f"{item_reorder_days} days" if item_reorder_days is not None else ">45 days"
                    ),
                    "Incoming": f"{item.incoming_qty} units in {item.lead_time_days} days",
                    "Status": item_status,
                }
            )

        queue_df = pd.DataFrame(queue_rows)
        severity_order = {"Critical": 0, "Warning": 1, "OK": 2}
        queue_df["Sort"] = queue_df["Status"].map(severity_order)
        queue_df = queue_df.sort_values(["Sort", "Item"]).drop(columns=["Sort"])

        queue_col, payload_col = st.columns([1.25, 1])
        with queue_col:
            st.markdown(
                '<span class="eyebrow">Replenishment queue</span>',
                unsafe_allow_html=True,
            )
            st.dataframe(queue_df, width="stretch", hide_index=True)

        with payload_col:
            stock_payload = {
                "control": "stock_forecast",
                "model": forecast_model,
                "horizon_days": 45,
                "selected_item": selected_id,
                "status": stock_status,
                "reorder_in_days": reorder_days,
                "stockout_in_days": stockout_days,
                "recommended_action": (
                    "Expedite replenishment or cap promotion demand"
                    if stock_status == "Critical"
                    else (
                        "Prepare purchase order before reorder threshold"
                        if stock_status == "Warning"
                        else "No replenishment action needed in forecast window"
                    )
                ),
            }
            st.markdown(
                '<span class="eyebrow" style="color:#0F766E;">Planning payload</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<pre class="code-block">{json.dumps(stock_payload, indent=2)}</pre>',
                unsafe_allow_html=True,
            )

    # =========================================================================
    # TAB 10 · HANDOFF
    # =========================================================================
    with tab10:
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
        st.dataframe(process, width="stretch", hide_index=True)

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
        st.dataframe(df.head(20), width="stretch")


if __name__ == "__main__":
    main()
