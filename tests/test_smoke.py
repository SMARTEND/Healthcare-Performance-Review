"""
Smoke tests — verify core packages are importable and key data-prep logic is correct.
Does not require the dataset CSV; safe to run in CI without data.
"""

import pandas as pd
import numpy as np


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
