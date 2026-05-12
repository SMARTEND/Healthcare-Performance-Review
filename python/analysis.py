"""
Healthcare Analytics — Statistical Analysis
Run with:  python python/analysis.py
"""
import os
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, f_oneway, pearsonr

ALPHA = 0.05
SRC = os.path.join(os.path.dirname(__file__), "..", "data", "healthcare_dataset.csv")

# -----------------------------------------------------------------------
# Load + prep
# -----------------------------------------------------------------------
df = pd.read_csv(SRC)
df["Date of Admission"] = pd.to_datetime(df["Date of Admission"])
df["Discharge Date"]    = pd.to_datetime(df["Discharge Date"])
df["LOS Days"]   = (df["Discharge Date"] - df["Date of Admission"]).dt.days.clip(lower=0)
df["Age Group"]  = pd.cut(df["Age"], bins=[0, 34, 49, 64, 79, 120],
                           labels=["18-34", "35-49", "50-64", "65-79", "80+"])
df_pos = df[df["Billing Amount"] > 0].copy()
df_pos["Rev per Day"] = df_pos["Billing Amount"] / df_pos["LOS Days"].replace(0, np.nan)


def _hdr(title):
    print(f"\n{'=' * 68}\n  {title}\n{'=' * 68}")


def _sig(p):
    tag = "SIGNIFICANT" if p < ALPHA else "not significant"
    return f"{tag}  (p = {p:.6f})"


# -----------------------------------------------------------------------
# 1. Chi-square: Medical Condition × Age Group
# -----------------------------------------------------------------------
_hdr("1. CHI-SQUARE — Medical Condition × Age Group")
ct = pd.crosstab(df["Medical Condition"], df["Age Group"])
chi2, p, dof, _ = chi2_contingency(ct)
print(f"  chi2 = {chi2:.2f}   df = {dof}   -> {_sig(p)}")
print("  Tests whether age distribution differs across medical conditions.")

# -----------------------------------------------------------------------
# 2. Chi-square: Medical Condition × Admission Type
# -----------------------------------------------------------------------
_hdr("2. CHI-SQUARE — Medical Condition x Admission Type")
ct2 = pd.crosstab(df["Medical Condition"], df["Admission Type"])
chi2, p, dof, _ = chi2_contingency(ct2)
print(f"  chi2 = {chi2:.2f}   df = {dof}   -> {_sig(p)}")
print("  Tests whether admission urgency profile differs by condition.")

# -----------------------------------------------------------------------
# 3. One-way ANOVA: LOS Days across Medical Conditions
# -----------------------------------------------------------------------
_hdr("3. ONE-WAY ANOVA — LOS Days across Medical Conditions")
groups_los = [g["LOS Days"].dropna().values for _, g in df.groupby("Medical Condition")]
F, p = f_oneway(*groups_los)
print(f"  F = {F:.4f}   -> {_sig(p)}")
print()
print(f"  {'Condition':<18} {'Mean LOS':>10} {'Std':>8} {'n':>7}")
print(f"  {'-' * 46}")
for cond, g in df.groupby("Medical Condition"):
    print(f"  {cond:<18} {g['LOS Days'].mean():>10.1f} {g['LOS Days'].std():>8.1f} {len(g):>7,}")

# -----------------------------------------------------------------------
# 4. One-way ANOVA: Billing Amount across Medical Conditions
# -----------------------------------------------------------------------
_hdr("4. ONE-WAY ANOVA — Billing Amount across Medical Conditions")
groups_bill = [g["Billing Amount"].dropna().values for _, g in df_pos.groupby("Medical Condition")]
F, p = f_oneway(*groups_bill)
print(f"  F = {F:.4f}   -> {_sig(p)}")

# -----------------------------------------------------------------------
# 5. Pearson Correlations: Age, LOS Days, Billing Amount
# -----------------------------------------------------------------------
_hdr("5. PEARSON CORRELATIONS — Age, LOS Days, Billing Amount")
corr_df = df_pos[["Age", "LOS Days", "Billing Amount"]].dropna()
for a, b in [("Age", "LOS Days"), ("Age", "Billing Amount"), ("LOS Days", "Billing Amount")]:
    r, p = pearsonr(corr_df[a], corr_df[b])
    print(f"  {a:<22} x {b:<22}  r = {r:+.4f}   -> {_sig(p)}")

# -----------------------------------------------------------------------
# 6. Revenue Efficiency: Billing per LOS Day by Condition
# -----------------------------------------------------------------------
_hdr("6. REVENUE EFFICIENCY — Avg Billing per LOS Day by Condition")
eff = (df_pos[df_pos["LOS Days"] > 0]
       .groupby("Medical Condition")["Rev per Day"]
       .agg(Mean="mean", Median="median", Std="std", n="count")
       .sort_values("Mean", ascending=False))
print(f"  {'Condition':<18} {'Mean $/day':>12} {'Median $/day':>14} {'Std':>10} {'n':>7}")
print(f"  {'-' * 64}")
for cond, row in eff.iterrows():
    print(f"  {cond:<18} {row['Mean']:>12,.0f} {row['Median']:>14,.0f} {row['Std']:>10,.0f} {row['n']:>7,}")

# -----------------------------------------------------------------------
# 7. Revenue Efficiency by Age Group
# -----------------------------------------------------------------------
_hdr("7. REVENUE EFFICIENCY — Avg Billing per LOS Day by Age Group")
age_eff = (df_pos[df_pos["LOS Days"] > 0]
           .groupby("Age Group", observed=False)["Rev per Day"]
           .agg(Mean="mean", Std="std", n="count"))
print(f"  {'Age Group':<12} {'Mean $/day':>12} {'Std':>10} {'n':>7}")
print(f"  {'-' * 44}")
for age_grp, row in age_eff.iterrows():
    print(f"  {str(age_grp):<12} {row['Mean']:>12,.0f} {row['Std']:>10,.0f} {row['n']:>7,}")

print(f"\n{'=' * 68}")
print("  Statistical analysis complete.")
print(f"{'=' * 68}\n")
