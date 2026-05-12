"""
Smoke tests — verify core packages are importable and key data-prep logic is correct.
Does not require the dataset CSV; safe to run in CI without data.
"""

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, f_oneway


def test_packages_importable():
    import matplotlib  # noqa: F401
    import seaborn  # noqa: F401
    import scipy  # noqa: F401
    import streamlit  # noqa: F401
    import plotly  # noqa: F401


def test_age_binning():
    ages = [25, 40, 55, 70, 85]
    result = pd.cut(
        ages,
        bins=[0, 34, 49, 64, 79, 120],
        labels=["18-34", "35-49", "50-64", "65-79", "80+"],
    )
    assert list(result.astype(str)) == ["18-34", "35-49", "50-64", "65-79", "80+"]


def test_los_calculation():
    admissions = pd.to_datetime(["2023-01-01", "2023-03-15"])
    discharges = pd.to_datetime(["2023-01-16", "2023-04-04"])
    los = (discharges - admissions).days
    assert list(los) == [15, 20]
    assert los.min() >= 0


def test_negative_billing_flagging():
    billing = pd.Series([25000.0, -500.0, 18000.0, -200.0])
    refunds = billing[billing < 0]
    gross = billing[billing > 0].sum()
    net = billing.sum()
    assert len(refunds) == 2
    assert gross == 43000.0
    assert net == 42300.0


def test_revenue_efficiency(sample_df):
    pos = sample_df[sample_df["Billing Amount"] > 0].copy()
    pos["Rev/Day"] = pos["Billing Amount"] / pos["LOS Days"]
    assert (pos["Rev/Day"] > 0).all()


def test_yoy_delta_math():
    cur, prior = 11_000, 10_000
    delta = (cur - prior) / abs(prior) * 100
    assert abs(delta - 10.0) < 1e-9


def test_chi_square_runs(sample_df):
    ct = pd.crosstab(sample_df["Medical Condition"], sample_df["Admission Type"])
    chi2, p, dof, _ = chi2_contingency(ct)
    assert chi2 >= 0
    assert 0.0 <= p <= 1.0


def test_anova_runs(sample_df):
    groups = [g["LOS Days"].values for _, g in sample_df.groupby("Medical Condition")]
    F, p = f_oneway(*groups)
    assert F >= 0
    assert 0.0 <= p <= 1.0


def test_no_negative_los(sample_df):
    assert (sample_df["LOS Days"] >= 0).all()


def test_age_bounds(sample_df):
    assert sample_df["Age"].between(0, 120).all()
