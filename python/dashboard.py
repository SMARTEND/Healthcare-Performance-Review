"""
Healthcare Analytics Project — Live Interactive Dashboard
Run with:  streamlit run python/dashboard.py
"""

import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Healthcare Performance Review",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

BLUE_DARK  = "#1F4E79"
BLUE_MID   = "#2E75B6"
BLUE_LIGHT = "#9DC3E6"
ACCENT_RED = "#C00000"
ACCENT_AMB = "#ED7D31"
GRAY       = "#7F7F7F"
BLUE_SEQ   = [BLUE_DARK, BLUE_MID, BLUE_LIGHT, "#5B9BD5", "#BDD7EE"]

# Categorical palette — one distinct color per segment
PALETTE_CAT = ["#2E75B6", "#ED7D31", "#70AD47", "#7030A0", "#C00000", "#00B0F0"]

AGE_COLOR_MAP = {
    "18–34": "#2E75B6",
    "35–49": "#ED7D31",
    "50–64": "#70AD47",
    "65–79": "#7030A0",
    "80+":   "#C00000",
}

INS_COLOR_MAP = {
    "Aetna":            "#2E75B6",
    "Blue Cross":       "#ED7D31",
    "Cigna":            "#70AD47",
    "Medicare":         "#7030A0",
    "UnitedHealthcare": "#C00000",
}

ADM_COLOR_MAP = {
    "Elective":  "#2E75B6",
    "Urgent":    "#ED7D31",
    "Emergency": "#C00000",
}

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "healthcare_dataset.csv")

# ----------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["Date of Admission"] = pd.to_datetime(df["Date of Admission"])
    df["Discharge Date"]    = pd.to_datetime(df["Discharge Date"])
    df["LOS Days"]  = (df["Discharge Date"] - df["Date of Admission"]).dt.days
    df["Year"]      = df["Date of Admission"].dt.year
    df["YearMonth"] = df["Date of Admission"].dt.to_period("M").astype(str)
    df["Age Group"] = pd.cut(
        df["Age"],
        bins=[0, 34, 49, 64, 79, 120],
        labels=["18–34", "35–49", "50–64", "65–79", "80+"],
    )
    return df

df_full = load_data()

# ----------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------
st.sidebar.image(
    "https://img.icons8.com/color/96/hospital.png", width=60
)
st.sidebar.title("Filters")

years = sorted(df_full["Year"].unique())
sel_years = st.sidebar.multiselect("Year", years, default=years)

conditions = sorted(df_full["Medical Condition"].unique())
sel_conditions = st.sidebar.multiselect("Medical Condition", conditions, default=conditions)

insurers = sorted(df_full["Insurance Provider"].unique())
sel_insurers = st.sidebar.multiselect("Insurance Provider", insurers, default=insurers)

adm_types = sorted(df_full["Admission Type"].unique())
sel_adm = st.sidebar.multiselect("Admission Type", adm_types, default=adm_types)

df = df_full[
    df_full["Year"].isin(sel_years) &
    df_full["Medical Condition"].isin(sel_conditions) &
    df_full["Insurance Provider"].isin(sel_insurers) &
    df_full["Admission Type"].isin(sel_adm)
]

st.sidebar.markdown("---")
st.sidebar.caption(
    "Source: Kaggle Healthcare Dataset (synthetic)  \n"
    "55,500 records · May 2019 – May 2024"
)

# -----------------------------------------------------------------------
# YoY reference — 2023 vs 2022 (last two full years), non-year filters
# -----------------------------------------------------------------------
_nm = (
    df_full["Medical Condition"].isin(sel_conditions) &
    df_full["Insurance Provider"].isin(sel_insurers) &
    df_full["Admission Type"].isin(sel_adm)
)
_df23 = df_full[_nm & (df_full["Year"] == 2023)]
_df22 = df_full[_nm & (df_full["Year"] == 2022)]
_has_yoy = len(_df23) > 0 and len(_df22) > 0


def _yoy(cur, prior):
    if not _has_yoy or prior == 0:
        return None
    return f"{(cur - prior) / abs(prior) * 100:+.1f}% vs 2022"


def _section(title):
    st.markdown(
        f"<div style='background:{BLUE_DARK};color:white;padding:8px 16px;"
        f"border-radius:6px;margin:20px 0 8px;font-weight:600;font-size:14px'>"
        f"{title}</div>",
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.markdown(
    f"""
    <div style='background:{BLUE_DARK};padding:20px 28px;border-radius:8px;margin-bottom:16px'>
        <h2 style='color:white;margin:0'>Healthcare Performance Review</h2>
        <p style='color:{BLUE_LIGHT};margin:4px 0 0'>
            Interactive Analytics Dashboard &nbsp;·&nbsp;
            Showing <b style='color:white'>{len(df):,}</b> of {len(df_full):,} records
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

_csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download filtered data (.csv)", _csv,
    "healthcare_filtered.csv", "text/csv",
)

# ----------------------------------------------------------------------
# KPI section — 2 metric cards (with YoY delta) + 3 gauge charts
# ----------------------------------------------------------------------
def _gauge(title, value, lo, hi, sfx=""):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 13}},
        number={"suffix": sfx, "font": {"size": 20, "color": BLUE_DARK}},
        gauge={
            "axis": {"range": [lo, hi], "tickwidth": 1, "tickcolor": GRAY},
            "bar":  {"color": BLUE_MID, "thickness": 0.28},
            "bgcolor": "white",
            "steps": [
                {"range": [lo, lo + (hi - lo) * 0.5],                   "color": "#EBF3FB"},
                {"range": [lo + (hi - lo) * 0.5, lo + (hi - lo) * 0.75], "color": "#C5DCF0"},
                {"range": [lo + (hi - lo) * 0.75, hi],                   "color": "#9DC3E6"},
            ],
        },
    ))
    fig.update_layout(height=200, margin=dict(t=50, b=0, l=20, r=20),
                      paper_bgcolor="white")
    return fig


total_adm   = len(df)
net_rev     = df["Billing Amount"].sum()
avg_billing = df["Billing Amount"].mean()
avg_los     = df["LOS Days"].mean()
refund_pct  = (df["Billing Amount"] < 0).mean() * 100

p_adm    = len(_df22)                                    if _has_yoy else 0
p_rev    = _df22["Billing Amount"].sum()                 if _has_yoy else 0
p_los    = _df22["LOS Days"].mean()                      if _has_yoy else 0
p_refund = (_df22["Billing Amount"] < 0).mean() * 100    if _has_yoy else 0

mc1, mc2, gc1, gc2, gc3 = st.columns([1.3, 1.3, 1, 1, 1])
mc1.metric("Total Admissions", f"{total_adm:,}",         _yoy(total_adm, p_adm))
mc2.metric("Net Revenue",      f"${net_rev/1e6:.2f}M",   _yoy(net_rev,   p_rev))
gc1.plotly_chart(_gauge("Avg LOS",     avg_los,            0, 30, " days"), use_container_width=True)
gc2.plotly_chart(_gauge("Avg Billing", avg_billing / 1000, 0, 50, "K"),     use_container_width=True)
gc3.plotly_chart(_gauge("Refund Rate", refund_pct,          0,  1, "%"),     use_container_width=True)

st.markdown("---")

# ----------------------------------------------------------------------
# Row 1 — Admissions trend  |  Monthly trend
# ----------------------------------------------------------------------
_section("Operations — Volume & Throughput")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Annual Admissions")
    yearly = df.groupby("Year").size().reset_index(name="Admissions")
    yearly["Color"] = yearly["Year"].apply(
        lambda y: BLUE_LIGHT if y in (yearly["Year"].min(), yearly["Year"].max()) else BLUE_MID
    )
    fig = px.bar(
        yearly, x="Year", y="Admissions",
        text="Admissions",
        color="Year",
        color_discrete_sequence=PALETTE_CAT,
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig.update_layout(showlegend=False, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Monthly Admissions Trend")
    monthly = df.groupby("YearMonth").size().reset_index(name="Admissions")
    monthly["Date"] = pd.to_datetime(monthly["YearMonth"])
    monthly = monthly.sort_values("Date")
    avg = monthly["Admissions"].mean()
    fig = px.line(
        monthly, x="Date", y="Admissions",
        color_discrete_sequence=[BLUE_DARK],
    )
    fig.add_hline(y=avg, line_dash="dash", line_color=ACCENT_AMB,
                  annotation_text=f"Mean: {avg:,.0f}", annotation_position="bottom right")
    fig.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# Row 2 — LOS distribution  |  Age groups
# ----------------------------------------------------------------------
_section("Clinical — Length of Stay & Demographics")
col3, col4 = st.columns(2)

with col3:
    st.subheader("Length of Stay Distribution")
    fig = px.histogram(
        df, x="LOS Days", nbins=30,
        color_discrete_sequence=[BLUE_MID],
    )
    fig.add_vline(x=df["LOS Days"].mean(),   line_dash="dash", line_color=ACCENT_RED,
                  annotation_text=f"Mean: {df['LOS Days'].mean():.1f}d")
    fig.add_vline(x=df["LOS Days"].median(), line_dash="dash", line_color=ACCENT_AMB,
                  annotation_text=f"Median: {df['LOS Days'].median():.0f}d")
    fig.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Patient Age Distribution")
    age_counts = (
        df["Age Group"]
        .value_counts()
        .reindex(["18–34", "35–49", "50–64", "65–79", "80+"])
        .reset_index()
    )
    age_counts.columns = ["Age Group", "Patients"]
    fig = px.bar(
        age_counts, x="Age Group", y="Patients",
        text="Patients",
        color="Age Group",
        color_discrete_map=AGE_COLOR_MAP,
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig.update_layout(showlegend=False, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# Row 3 — Insurance revenue  |  Admission type
# ----------------------------------------------------------------------
_section("Financial — Revenue & Payer Mix")
col5, col6 = st.columns(2)

with col5:
    st.subheader("Net Revenue by Insurance Provider")
    ins = (
        df.groupby("Insurance Provider")["Billing Amount"]
        .sum()
        .sort_values()
        .reset_index()
    )
    ins["Revenue ($M)"] = ins["Billing Amount"] / 1e6
    fig = px.bar(
        ins, x="Revenue ($M)", y="Insurance Provider",
        orientation="h", text="Revenue ($M)",
        color="Insurance Provider",
        color_discrete_map=INS_COLOR_MAP,
    )
    fig.update_traces(texttemplate="$%{text:.1f}M", textposition="outside")
    fig.update_layout(showlegend=False, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col6:
    st.subheader("Admission Type Breakdown")
    adm = df["Admission Type"].value_counts().reset_index()
    adm.columns = ["Admission Type", "Count"]
    fig = px.pie(
        adm, names="Admission Type", values="Count",
        hole=0.4,
        color="Admission Type",
        color_discrete_map=ADM_COLOR_MAP,
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(showlegend=False, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# Row 4 — Condition × Age heatmap  (full width)
# ----------------------------------------------------------------------
_section("Clinical Mix — Condition × Age Group Volume")
st.subheader("Patient Volume by Medical Condition × Age Group")
ct = pd.crosstab(df["Medical Condition"], df["Age Group"])
fig = px.imshow(
    ct,
    text_auto=",",
    color_continuous_scale="Blues",
    aspect="auto",
)
fig.update_layout(margin=dict(t=20, b=20), coloraxis_showscale=True)
st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# Row 5 — Test results stacked bar  |  Pareto
# ----------------------------------------------------------------------
_section("Patient Outcomes & Revenue Concentration")
col7, col8 = st.columns(2)

with col7:
    st.subheader("Test Results by Medical Condition")
    tr = pd.crosstab(df["Medical Condition"], df["Test Results"], normalize="index") * 100
    tr = tr.reset_index().melt(id_vars="Medical Condition", var_name="Result", value_name="Pct")
    order = ["Normal", "Inconclusive", "Abnormal"]
    tr["Result"] = pd.Categorical(tr["Result"], categories=order, ordered=True)
    tr = tr.sort_values("Result")
    fig = px.bar(
        tr, x="Pct", y="Medical Condition",
        color="Result", orientation="h",
        barmode="stack",
        color_discrete_map={
            "Normal":       BLUE_LIGHT,
            "Inconclusive": GRAY,
            "Abnormal":     ACCENT_RED,
        },
        text="Pct",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="inside")
    fig.update_layout(margin=dict(t=20, b=20), xaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

with col8:
    st.subheader("Revenue Concentration (Pareto)")
    ins_sorted = (
        df.groupby("Insurance Provider")["Billing Amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    ins_sorted["Revenue ($M)"] = ins_sorted["Billing Amount"] / 1e6
    ins_sorted["Cumulative %"] = ins_sorted["Billing Amount"].cumsum() / ins_sorted["Billing Amount"].sum() * 100

    pareto_bar_colors = [INS_COLOR_MAP.get(p, BLUE_MID)
                         for p in ins_sorted["Insurance Provider"]]

    fig = go.Figure()
    fig.add_bar(
        x=ins_sorted["Insurance Provider"],
        y=ins_sorted["Revenue ($M)"],
        name="Revenue ($M)",
        marker_color=pareto_bar_colors,
        yaxis="y1",
    )
    fig.add_scatter(
        x=ins_sorted["Insurance Provider"],
        y=ins_sorted["Cumulative %"],
        name="Cumulative %",
        mode="lines+markers",
        marker=dict(color=ACCENT_RED, size=8),
        line=dict(color=ACCENT_RED, width=2),
        yaxis="y2",
    )
    fig.update_layout(
        yaxis=dict(title="Revenue ($M)", titlefont_color=BLUE_DARK),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right",
                    range=[0, 110], titlefont_color=ACCENT_RED),
        legend=dict(orientation="h", y=-0.2),
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# Row 6 — Revenue efficiency  |  LOS vs Billing scatter
# ----------------------------------------------------------------------
_section("Advanced Analysis — Efficiency & Correlation")
col9, col10 = st.columns(2)

with col9:
    st.subheader("Revenue Efficiency by Condition ($/LOS Day)")
    _eff = df[(df["Billing Amount"] > 0) & (df["LOS Days"] > 0)].copy()
    _eff["Rev/Day"] = _eff["Billing Amount"] / _eff["LOS Days"]
    eff_cond = (_eff.groupby("Medical Condition")["Rev/Day"]
                .mean().sort_values().reset_index())
    eff_cond.columns = ["Medical Condition", "Avg Rev/Day"]
    fig = px.bar(eff_cond, x="Avg Rev/Day", y="Medical Condition",
                 orientation="h", text="Avg Rev/Day",
                 color="Medical Condition",
                 color_discrete_sequence=PALETTE_CAT)
    fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig.update_layout(showlegend=False, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col10:
    st.subheader("LOS Days vs Billing Amount")
    _pool = df[df["Billing Amount"] > 0]
    _samp = _pool.sample(n=min(2000, len(_pool)), random_state=42)
    fig = px.scatter(
        _samp, x="LOS Days", y="Billing Amount",
        color="Medical Condition",
        color_discrete_sequence=PALETTE_CAT,
        opacity=0.45,
        labels={"Billing Amount": "Billing ($)", "LOS Days": "LOS (days)"},
    )
    _m, _b = np.polyfit(_samp["LOS Days"], _samp["Billing Amount"], 1)
    _x = np.linspace(_samp["LOS Days"].min(), _samp["LOS Days"].max(), 100)
    fig.add_scatter(x=_x, y=_m * _x + _b, mode="lines",
                    line=dict(color=ACCENT_RED, width=2, dash="dash"),
                    name="Trend", showlegend=True)
    fig.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# Row 7 — Medication distribution  |  Top 10 hospitals
# ----------------------------------------------------------------------
_section("Operations — Medications & Hospital Volume")
col11, col12 = st.columns(2)

with col11:
    st.subheader("Medication Distribution")
    med_ct = df["Medication"].value_counts().reset_index()
    med_ct.columns = ["Medication", "Count"]
    fig = px.bar(
        med_ct.sort_values("Count"), x="Count", y="Medication",
        orientation="h", text="Count",
        color="Medication", color_discrete_sequence=PALETTE_CAT,
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig.update_layout(showlegend=False, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col12:
    st.subheader("Top 10 Hospitals by Patient Volume")
    top_h = df["Hospital"].value_counts().head(10).reset_index()
    top_h.columns = ["Hospital", "Patients"]
    fig = px.bar(
        top_h.sort_values("Patients"), x="Patients", y="Hospital",
        orientation="h", text="Patients",
        color_discrete_sequence=[BLUE_MID],
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig.update_layout(showlegend=False, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------
# Raw data explorer (collapsed)
# ----------------------------------------------------------------------
with st.expander("Raw Data Explorer"):
    st.dataframe(df.reset_index(drop=True), use_container_width=True, height=300)
    st.caption(f"{len(df):,} rows · {df.shape[1]} columns")
