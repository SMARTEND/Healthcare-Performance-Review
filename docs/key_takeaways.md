# Key Takeaways — Healthcare Performance Review

Executive summary of findings from the 55,500-record synthetic healthcare dataset (May 2019 – May 2024).

---

## 1. Operations: Volume Is Predictable and Stable

**Finding:** After a 2019 ramp-up year (7,387 admissions, partial year), annual volume plateaued at ~11,000 admissions/year and stayed within a 1% band from 2020 through 2023.

**Implication:** Demand is highly predictable. Capacity planning, staffing, and procurement can be modeled on a steady-state assumption of ~11K admissions/year (~917/month). The 2024 partial-year figure is on track with that baseline.

---

## 2. Clinical: Length of Stay Is Anomalously Long

**Finding:** Mean LOS is 15.5 days (median similar), with 53% of patients staying 15–30 days and a hard cap at 30 days. The U.S. average for acute inpatient stays is ~4–5 days.

**Implication:** This facility profile is closer to long-term care, rehabilitation, or sub-acute rather than acute inpatient. Any LOS-reduction initiative should first segment by condition and admission type to find the highest-variation cohorts — that is where intervention ROI is highest.

**Caveat:** The 30-day hard cap is likely a data-generation artifact. In a real dataset, the LOS distribution would have a longer tail and this cap would not appear.

---

## 3. Demographics: The 18–34 Cohort Dominates Unexpectedly

**Finding:** The 18–34 age group accounts for 24.7% of admissions (13,721 patients) — the largest single cohort. The 80+ group is the smallest at 8.8%.

**Implication:** For a facility with 15+ day average LOS, young-adult dominance is unusual. In a real setting this would warrant investigation: are these patients presenting with chronic conditions, mental health admissions, or substance-related care? The 80+ group, while smallest in volume, typically carries the highest cost-per-case and should be monitored separately.

---

## 4. Financial: Payer Mix Is Well Balanced — Low Concentration Risk

**Finding:** Five payers account for 100% of revenue. Cigna leads at $287.1M (20.2%), Medicare follows at $285.7M (20.1%). The spread across all five is only 2.9 percentage points.

**Implication:** Revenue concentration risk is minimal. No single payer controls enough volume to materially destabilize the financial picture if lost. However, the near-equal split also means there is no dominant commercial-payer relationship to negotiate leverage from.

| Payer | Net Revenue | Share |
|-------|-------------|-------|
| Cigna | $287.1M | ~20.2% |
| Medicare | $285.7M | ~20.1% |
| Blue Cross | ~$284M | ~20.0% |
| UnitedHealthcare | ~$283M | ~19.9% |
| Aetna | ~$282M | ~19.8% |

---

## 5. Clinical Mix: No Dominant Condition-Age Combination

**Finding:** The condition × age heatmap shows a broadly uniform distribution — no single combination (e.g., Diabetes × 65–79) accounts for a disproportionate share of volume.

**Implication:** Clinical resource planning cannot be optimized around one or two service lines. The facility must maintain broad clinical competency across all six conditions and all age bands. In a real dataset, clustering would likely emerge and would drive specialization decisions.

---

## 6. Billing: Average Revenue per Patient Is Consistent Across Payers

**Finding:** Average billing per patient is $25,539 overall. The near-uniform payer split implies per-patient billing is similar regardless of insurer.

**Implication:** There is no evidence of payer-specific pricing differentiation in this dataset. In a real setting, payer contract rates vary significantly and per-patient revenue by payer would be a key financial KPI to track.

---

## 7. Data Quality: 108 Negative-Billing Records

**Finding:** 108 records carry negative billing amounts, flagged as refunds. These are excluded from gross revenue but included in net revenue.

**Implication:** Refund rate is very low (< 0.2% of records). In a real setting, refund patterns by payer, condition, or physician would be worth tracking as a proxy for billing accuracy and denial rates.

---

## Limitations to Keep in Mind

| Limitation | Impact |
|-----------|--------|
| Synthetic uniform distribution | Condition/age splits are ~equal by design — real case mix would cluster differently |
| 30-day LOS hard cap | Distorts any percentile analysis above the 75th percentile |
| No pediatric population | Minimum age is 13; no children's health analysis is possible |
| Partial boundary years | 2019 (May–Dec) and 2024 (Jan–May) are not full calendar years — exclude from YoY comparisons |
| No physician-level data analysis | Doctor column exists but was not used for attribution analysis |

---

*For pipeline and statistical methodology, see [methodology.md](methodology.md).*
