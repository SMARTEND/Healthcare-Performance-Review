# Methodology

End-to-end pipeline used to transform 55,500 raw patient records into an executive Power BI dashboard.

## Pipeline Overview

```
Raw CSV (55,500 rows, 15 columns)
    │
    ├──► [SQL] Clean, deduplicate, aggregate
    │
    ▼
Analytical Dataset
    │
    ├──► [Python] Profile, statistical tests, segment
    │
    ▼
Validated Insights + 9 Charts (PNG)
    │
    ├──► [Power BI] Star-schema model, DAX, visualize
    │
    ▼
Interactive Executive Dashboard (.pbix)
```

---

## Stage 1 — SQL Extraction & Cleaning

**Tool:** T-SQL / MySQL 8.0

**Goal:** Produce a clean, analysis-ready dataset.

**Operations:**
- Standardized name capitalization with `UPPER()` / `LOWER()` / string functions
- Removed duplicate records using `ROW_NUMBER()` window function partitioned by patient identifier
- Computed `LOS_Days` via `DATEDIFF(Date_of_Admission, Discharge_Date)`
- Flagged 108 records with negative billing for separate refund tracking
- Aggregated patient counts by year, month, condition, and payer using `GROUP BY` + `HAVING`

**Output:** Cleaned CSV with 55,500 rows × 15 columns + 1 derived column (LOS Days).

---

## Stage 2 — Python Statistical Analysis

**Tool:** Python 3.11 with pandas, NumPy, SciPy, Matplotlib, Seaborn

**Goal:** Validate dataset properties, run statistical tests, and produce publication-quality charts.

**Operations:**

### Profiling
- Row counts, null distributions, date ranges, min/max for all numeric columns
- Distribution analysis for categorical fields (medical condition, gender, blood type, etc.)
- Outlier detection on billing amounts (negative values flagged)

### Statistical Tests
- **Chi-square test of independence** on condition × admission type cross-tabs (no significant association found — confirms uniform synthetic distribution)
- **Two-proportion z-test** on subsegment differences (e.g., test result rates by condition)
- **Correlation analysis** between age, LOS, and billing

### Segmentation
- 5 age bands: 18–34, 35–49, 50–64, 65–79, 80+
- 6 medical conditions: Arthritis, Asthma, Cancer, Diabetes, Hypertension, Obesity
- 5 insurance providers: Cigna, Medicare, Blue Cross, UnitedHealthcare, Aetna
- 3 admission types: Elective, Urgent, Emergency

### Visualization
- Generated 9 PNG charts at 300 DPI using consistent dashboard-aligned blue palette
- Each chart paired with insight-driven title (not just topic title)
- All charts include source-disclosure footer

**Output:** 9 publication-ready charts in `charts/`.

---

## Stage 3 — Power BI Dashboard

**Tool:** Power BI Desktop with DAX

**Goal:** Build an interactive 4-page executive dashboard.

**Data Model:**
- Star schema: 1 fact table (`Patients`) + 1 dimension (`Date`)
- `Date` table marked as Date Table for time-intelligence support
- Active relationship: `Patients[Date of Admission]` ↔ `Date[Date]`

**DAX Categories Used:**
- Aggregation: `COUNTROWS`, `SUM`, `AVERAGE`, `MEDIAN`, `DISTINCTCOUNT`
- Filter context: `CALCULATE`, `FILTER`
- Time intelligence: `SAMEPERIODLASTYEAR`, `TOTALYTD`
- Conditional: `DIVIDE` (with safe-divide), `IF`, `SWITCH`
- Iterators: `SUMX`
- String/format: `FORMAT`, concatenation with `&`

See [`powerbi/dax_measures.md`](../powerbi/dax_measures.md) for all measures.

**Pages:**
1. **Consolidated View** — KPI hero cards + clinical/operational/financial metrics
2. **Monthly View** — Time-series trends with YoY comparisons
3. **Patient Details** — Drill-through page filterable by patient cohort
4. **Key Takeaways** — Executive summary of insights and recommended actions

**Interactive Elements:**
- Date range slicer (top-right)
- Page navigation buttons (left rail)
- Cross-filtering between visuals
- Drill-through from summary pages to patient detail
- Custom tooltips on KPI cards

---

## Validation & Reproducibility

- **Counts validated** between source CSV and Power BI model (must match: 55,500)
- **Revenue validated**: $1.42bn ± $0.01bn between Python and DAX
- **All scripts are idempotent** — re-running produces identical output

To reproduce from scratch:

```bash
git clone https://github.com/SMARTEND/Healthcare-Performance-Review.git
cd Healthcare-Performance-Review
pip install pandas numpy matplotlib seaborn scipy
python python/profile_kaggle.py
python python/generate_charts.py
# Then open powerbi/healthcare_dashboard.pbix
```

---

## Limitations

1. **Synthetic data** — Distributions are uniform across categorical fields, which means insights illustrate methodology, not real clinical patterns.
2. **Hard LOS cap at 30 days** — likely a generation artifact; would distort any LOS-reduction modeling.
3. **No pediatric data** — Minimum age in dataset is 13.
4. **Partial-year boundaries** — 2019 (May–Dec) and 2024 (Jan–May) are not full years; year-over-year comparisons should account for this.
