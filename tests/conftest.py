"""Shared pytest fixtures for healthcare analytics tests."""
import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_df():
    """Minimal synthetic DataFrame mirroring the healthcare dataset schema.
    200 rows, deterministic via seed 42. No disk access required.
    """
    rng = np.random.default_rng(42)
    n = 200

    conditions  = ["Diabetes", "Cancer", "Arthritis", "Obesity", "Hypertension", "Asthma"]
    insurers    = ["Aetna", "Blue Cross", "Cigna", "Medicare", "UnitedHealthcare"]
    adm_types   = ["Elective", "Urgent", "Emergency"]
    medications = ["Aspirin", "Ibuprofen", "Penicillin", "Paracetamol", "Lipitor"]
    test_res    = ["Normal", "Abnormal", "Inconclusive"]
    blood_types = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]

    ages        = rng.integers(18, 90, n)
    los         = rng.integers(1, 31, n)
    admit_dates = pd.date_range("2020-01-01", periods=n, freq="9h")

    return pd.DataFrame({
        "Name":               [f"Patient {i}" for i in range(n)],
        "Age":                ages,
        "Gender":             rng.choice(["Male", "Female"], n),
        "Blood Type":         rng.choice(blood_types, n),
        "Medical Condition":  rng.choice(conditions, n),
        "Date of Admission":  admit_dates,
        "Discharge Date":     admit_dates + pd.to_timedelta(los, unit="D"),
        "Doctor":             [f"Dr. Smith {i % 20}" for i in range(n)],
        "Hospital":           rng.choice([f"Hospital {c}" for c in "ABCDE"], n),
        "Insurance Provider": rng.choice(insurers, n),
        "Billing Amount":     rng.uniform(5_000, 50_000, n),
        "Room Number":        rng.integers(100, 500, n),
        "Admission Type":     rng.choice(adm_types, n),
        "Medication":         rng.choice(medications, n),
        "Test Results":       rng.choice(test_res, n),
        "LOS Days":           los,
        "Year":               admit_dates.year,
    })
