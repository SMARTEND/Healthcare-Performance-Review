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

# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.markdown(
    f"""
    <div style='background:{BLUE_DARK};padding:20px 28px;border-radius:8px;margin-bottom:16px'>
        <h2 style='color:white;margin:0'>🏥 Healthcare Performance Review</h2>
        <p style='color:{BLUE_LIGHT};margin:4px 0 0'>
            Interactive Analytics Dashboard &nbsp;·&nbsp;
            Showing <b style='color:white'>{len(df):,}</b> of {len(df_full):,} records
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# KPI cards
# ----------------------------------------------------------------------
k1, k2, k3, k4, k5 = st.columns(5)

def kpi(col, label, value, delta=None):
    col.metric(label, value, delta)

total_adm   = len(df)
net_rev     = df["Billing Amount"].sum()
avg_billing = df["Billing Amount"].mean()
avg_los     = df["LOS Days"].mean()
refund_pct  = (df["Billing Amount"] < 0).mean() * 100

kpi(k1, "Total Admissions",    f"{total_adm:,}")
kpi(k2, "Net Revenue",         f"${net_rev/1e6:.2f}M")
kpi(k3, "Avg Billing/Patient", f"${avg_billing:,.0f}")
kpi(k4, "Avg Length of Stay",  f"{avg_los:.1f} days")
kpi(k5, "Refund Rate",         f"{refund_pct:.1f}%")

st.markdown("---")

# ----------------------------------------------------------------------
# Row 1 — Admissions trend  |  Monthly trend
# ----------------------------------------------------------------------
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
# Raw data explorer (collapsed)
# ----------------------------------------------------------------------
with st.expander("Raw Data Explorer"):
    st.dataframe(df.reset_index(drop=True), use_container_width=True, height=300)
    st.caption(f"{len(df):,} rows · {df.shape[1]} columns")
