"""
Healthcare Analytics Project — Chart Generator
Generates publication-quality PNG charts from the Kaggle Healthcare Dataset.

Output: ./charts/  (8 PNGs at 300 DPI)
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.ticker import FuncFormatter

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
SRC = r"C:\Users\alshe\Downloads\healthcare_dataset.csv"
OUT_DIR = r"C:\Users\alshe\Downloads\charts"
os.makedirs(OUT_DIR, exist_ok=True)

# Dashboard-aligned blue palette
BLUE_DARK = "#1F4E79"
BLUE_MID = "#2E75B6"
BLUE_LIGHT = "#9DC3E6"
ACCENT_RED = "#C00000"
ACCENT_AMBER = "#ED7D31"
GRAY = "#7F7F7F"

PALETTE_BLUE = [BLUE_DARK, BLUE_MID, BLUE_LIGHT, "#5B9BD5", "#BDD7EE", "#DEEBF7"]

# Global plot styling
sns.set_style("whitegrid", {"grid.linestyle": "--", "grid.alpha": 0.4})
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "figure.dpi": 100,
})

DISCLAIMER = ("Source: Kaggle Healthcare Dataset (synthetic) · "
              "55,500 records · May 2019 – May 2024")

def add_footer(fig):
    fig.text(0.5, -0.02, DISCLAIMER, ha="center", va="top",
             fontsize=8, color=GRAY, style="italic")

def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [ok] saved: {name}")

# ----------------------------------------------------------------------
# Load + prep
# ----------------------------------------------------------------------
print("Loading data...")
df = pd.read_csv(SRC)
df["Date of Admission"] = pd.to_datetime(df["Date of Admission"])
df["Discharge Date"] = pd.to_datetime(df["Discharge Date"])
df["LOS Days"] = (df["Discharge Date"] - df["Date of Admission"]).dt.days
df["Year"] = df["Date of Admission"].dt.year
df["Month"] = df["Date of Admission"].dt.to_period("M").astype(str)
df["Age Group"] = pd.cut(df["Age"], bins=[0, 34, 49, 64, 79, 120],
                         labels=["18–34", "35–49", "50–64", "65–79", "80+"])

print(f"Loaded {len(df):,} rows.")
print()

# ----------------------------------------------------------------------
# Chart 1 — Annual Admissions Trend
# ----------------------------------------------------------------------
print("Generating charts...")
yearly = df.groupby("Year").size().reset_index(name="Admissions")

fig, ax = plt.subplots(figsize=(10, 5.5))
bars = ax.bar(yearly["Year"].astype(str), yearly["Admissions"],
              color=BLUE_MID, edgecolor=BLUE_DARK, linewidth=1.2)
# Highlight partial years
bars[0].set_color(BLUE_LIGHT)
bars[-1].set_color(BLUE_LIGHT)

for bar, val in zip(bars, yearly["Admissions"]):
    ax.text(bar.get_x() + bar.get_width()/2, val + 150,
            f"{val:,}", ha="center", fontsize=10, fontweight="bold")

ax.set_title("Annual Admissions — Steady ~11K/year After 2020 Ramp", pad=15)
ax.set_xlabel("Year")
ax.set_ylabel("Admissions")
ax.set_ylim(0, max(yearly["Admissions"]) * 1.15)
ax.text(0.02, 0.95, "Light bars = partial-year data",
        transform=ax.transAxes, fontsize=9, color=GRAY,
        verticalalignment="top",
        bbox=dict(facecolor="white", edgecolor=GRAY, alpha=0.8))
add_footer(fig)
save(fig, "01_annual_admissions.png")

# ----------------------------------------------------------------------
# Chart 2 — Monthly Admissions Trend (Time Series)
# ----------------------------------------------------------------------
monthly = df.groupby("Month").size().reset_index(name="Admissions")
monthly["MonthDate"] = pd.to_datetime(monthly["Month"])

fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(monthly["MonthDate"], monthly["Admissions"],
        color=BLUE_DARK, linewidth=2, marker="o", markersize=4,
        markerfacecolor=BLUE_MID)
ax.fill_between(monthly["MonthDate"], monthly["Admissions"],
                alpha=0.15, color=BLUE_MID)

avg = monthly["Admissions"].mean()
ax.axhline(avg, color=ACCENT_AMBER, linestyle="--", linewidth=1.5,
           label=f"Mean: {avg:,.0f}/month")
ax.set_title("Monthly Admissions Trend — Stable Operations 2020–2023", pad=15)
ax.set_xlabel("Month")
ax.set_ylabel("Admissions")
ax.legend(loc="lower right")
add_footer(fig)
save(fig, "02_monthly_trend.png")

# ----------------------------------------------------------------------
# Chart 3 — Length of Stay Distribution (Histogram)
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.hist(df["LOS Days"].dropna(), bins=range(0, 32),
        color=BLUE_MID, edgecolor=BLUE_DARK, linewidth=0.8)

mean_los = df["LOS Days"].mean()
median_los = df["LOS Days"].median()
ax.axvline(mean_los, color=ACCENT_RED, linestyle="--", linewidth=2,
           label=f"Mean: {mean_los:.1f} days")
ax.axvline(median_los, color=ACCENT_AMBER, linestyle="--", linewidth=2,
           label=f"Median: {median_los:.0f} days")

ax.set_title("Length of Stay Distribution — Hard Cap at 30 Days", pad=15)
ax.set_xlabel("Length of Stay (days)")
ax.set_ylabel("Number of Patients")
ax.legend()
add_footer(fig)
save(fig, "03_los_distribution.png")

# ----------------------------------------------------------------------
# Chart 4 — Age Group Distribution
# ----------------------------------------------------------------------
age_counts = df["Age Group"].value_counts().reindex(
    ["18–34", "35–49", "50–64", "65–79", "80+"])

fig, ax = plt.subplots(figsize=(10, 5.5))
colors = [BLUE_DARK if i == age_counts.idxmax() else BLUE_MID
          for i in age_counts.index]
bars = ax.bar(age_counts.index, age_counts.values,
              color=colors, edgecolor="white", linewidth=1.2)

for bar, val in zip(bars, age_counts.values):
    pct = val / age_counts.sum() * 100
    ax.text(bar.get_x() + bar.get_width()/2, val + 150,
            f"{val:,}\n({pct:.1f}%)", ha="center",
            fontsize=10, fontweight="bold")

ax.set_title("Patient Age Distribution — 18–34 Is the Largest Cohort", pad=15)
ax.set_xlabel("Age Group")
ax.set_ylabel("Patients")
ax.set_ylim(0, max(age_counts.values) * 1.18)
add_footer(fig)
save(fig, "04_age_groups.png")

# ----------------------------------------------------------------------
# Chart 5 — Insurance Provider Revenue (Sorted, Cigna Leading)
# ----------------------------------------------------------------------
ins_revenue = df.groupby("Insurance Provider")["Billing Amount"].sum().sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(10, 5.5))
colors = [BLUE_DARK if i == len(ins_revenue) - 1 else BLUE_MID
          for i in range(len(ins_revenue))]
bars = ax.barh(ins_revenue.index, ins_revenue.values / 1e6,
               color=colors, edgecolor="white", linewidth=1.2)

for bar, val in zip(bars, ins_revenue.values / 1e6):
    ax.text(val + 2, bar.get_y() + bar.get_height()/2,
            f"${val:,.1f}M", va="center", fontsize=10, fontweight="bold")

ax.set_title("Net Revenue by Insurance Provider — Cigna Leads", pad=15)
ax.set_xlabel("Net Revenue ($M)")
ax.set_xlim(0, max(ins_revenue.values) / 1e6 * 1.15)
add_footer(fig)
save(fig, "05_insurance_revenue.png")

# ----------------------------------------------------------------------
# Chart 6 — Medical Condition x Age Group Heatmap
# ----------------------------------------------------------------------
ct = pd.crosstab(df["Medical Condition"], df["Age Group"])

fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(ct, annot=True, fmt=",", cmap="Blues",
            cbar_kws={"label": "Patients"}, linewidths=0.5,
            linecolor="white", ax=ax)
ax.set_title("Patient Volume by Medical Condition × Age Group", pad=15)
ax.set_xlabel("Age Group")
ax.set_ylabel("Medical Condition")
add_footer(fig)
save(fig, "06_condition_age_heatmap.png")

# ----------------------------------------------------------------------
# Chart 7 — Admission Type Breakdown
# ----------------------------------------------------------------------
adm = df["Admission Type"].value_counts()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

# Donut
colors_donut = [BLUE_DARK, BLUE_MID, BLUE_LIGHT]
wedges, texts, autotexts = ax1.pie(adm.values, labels=adm.index,
                                    colors=colors_donut, autopct="%1.1f%%",
                                    startangle=90, pctdistance=0.78,
                                    wedgeprops=dict(width=0.4, edgecolor="white"))
for at in autotexts:
    at.set_color("white")
    at.set_fontweight("bold")
ax1.set_title("Share by Admission Type", pad=15)

# Bar with avg billing
billing_by_type = df.groupby("Admission Type")["Billing Amount"].mean().reindex(adm.index)
bars = ax2.bar(billing_by_type.index, billing_by_type.values,
               color=colors_donut, edgecolor="white", linewidth=1.2)
for bar, val in zip(bars, billing_by_type.values):
    ax2.text(bar.get_x() + bar.get_width()/2, val + 200,
             f"${val:,.0f}", ha="center", fontsize=10, fontweight="bold")
ax2.set_title("Average Billing by Admission Type", pad=15)
ax2.set_ylabel("Avg Billing ($)")
ax2.set_ylim(0, max(billing_by_type.values) * 1.15)

add_footer(fig)
save(fig, "07_admission_type.png")

# ----------------------------------------------------------------------
# Chart 8 — Test Results by Medical Condition (Stacked Bar)
# ----------------------------------------------------------------------
tr = pd.crosstab(df["Medical Condition"], df["Test Results"], normalize="index") * 100
tr = tr[["Normal", "Inconclusive", "Abnormal"]]

fig, ax = plt.subplots(figsize=(11, 5.5))
tr.plot(kind="barh", stacked=True, ax=ax,
        color=[BLUE_LIGHT, GRAY, ACCENT_RED],
        edgecolor="white", linewidth=1)

for c in ax.containers:
    ax.bar_label(c, fmt="%.1f%%", label_type="center",
                 color="white", fontweight="bold", fontsize=9)

ax.set_title("Test Results by Medical Condition (% within condition)", pad=15)
ax.set_xlabel("Percentage")
ax.set_ylabel("")
ax.set_xlim(0, 100)
ax.legend(title="Test Result", loc="lower right",
          bbox_to_anchor=(1.0, -0.18), ncol=3, frameon=False)
add_footer(fig)
save(fig, "08_test_results_by_condition.png")

# ----------------------------------------------------------------------
# Chart 9 — Bonus: Revenue Concentration (Pareto)
# ----------------------------------------------------------------------
ins_sorted = df.groupby("Insurance Provider")["Billing Amount"].sum().sort_values(ascending=False)
cumpct = (ins_sorted.cumsum() / ins_sorted.sum() * 100)

fig, ax1 = plt.subplots(figsize=(10, 5.5))
bars = ax1.bar(ins_sorted.index, ins_sorted.values / 1e6,
               color=BLUE_MID, edgecolor=BLUE_DARK, linewidth=1.2)
ax1.set_ylabel("Revenue ($M)", color=BLUE_DARK)
ax1.tick_params(axis="y", labelcolor=BLUE_DARK)

ax2 = ax1.twinx()
ax2.plot(ins_sorted.index, cumpct.values, color=ACCENT_RED,
         marker="o", linewidth=2, markersize=8)
ax2.set_ylabel("Cumulative %", color=ACCENT_RED)
ax2.tick_params(axis="y", labelcolor=ACCENT_RED)
ax2.set_ylim(0, 110)
ax2.spines["right"].set_visible(True)
ax2.grid(False)

for x, y in zip(range(len(cumpct)), cumpct.values):
    ax2.text(x, y + 3, f"{y:.0f}%", ha="center", fontsize=9,
             color=ACCENT_RED, fontweight="bold")

ax1.set_title("Pareto: Revenue Concentration by Payer — Highly Distributed", pad=15)
add_footer(fig)
save(fig, "09_payer_pareto.png")

# ----------------------------------------------------------------------
# Done
# ----------------------------------------------------------------------
print()
print(f"All charts saved to: {OUT_DIR}")
print(f"Total charts: {len([f for f in os.listdir(OUT_DIR) if f.endswith('.png')])}")
