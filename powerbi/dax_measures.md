# DAX Measures — Healthcare Performance Review

All measures used in the Power BI dashboard, organized by purpose. Drop-in ready against a fact table named `Patients` with columns from the Kaggle Healthcare Dataset.

## Table of Contents
- [Core Counts](#core-counts)
- [Financial Measures](#financial-measures)
- [Time Intelligence](#time-intelligence)
- [Length of Stay](#length-of-stay)
- [Data Quality](#data-quality)
- [Format Strings](#format-strings)

---

## Core Counts

```dax
Total Admissions = COUNTROWS ( Patients )

Total Discharges =
CALCULATE (
    COUNTROWS ( Patients ),
    NOT ( ISBLANK ( Patients[Discharge Date] ) )
)

Total Unique Patients = DISTINCTCOUNT ( Patients[Name] )
```

---

## Financial Measures

```dax
Gross Revenue =
CALCULATE (
    SUM ( Patients[Billing Amount] ),
    Patients[Billing Amount] > 0
)

Total Refunds (Amount) =
CALCULATE (
    SUM ( Patients[Billing Amount] ),
    Patients[Billing Amount] < 0
)

Total Refunds (Count) =
CALCULATE (
    COUNTROWS ( Patients ),
    Patients[Billing Amount] < 0
)

Net Revenue = SUM ( Patients[Billing Amount] )

Refund Rate % =
DIVIDE (
    ABS ( [Total Refunds (Amount)] ),
    [Gross Revenue],
    0
)

Average Billing per Patient =
DIVIDE (
    [Net Revenue],
    [Total Admissions],
    0
)
```

---

## Time Intelligence

> Requires a Date table marked as Date. Create one with:
> `Date = CALENDAR ( DATE(2019,1,1), DATE(2024,12,31) )`
> Then mark it as Date Table and link to `Patients[Date of Admission]`.

```dax
Admissions YTD =
TOTALYTD ( [Total Admissions], 'Date'[Date] )

Admissions PY =
CALCULATE (
    [Total Admissions],
    SAMEPERIODLASTYEAR ( 'Date'[Date] )
)

Admissions YoY % =
DIVIDE (
    [Total Admissions] - [Admissions PY],
    [Admissions PY],
    BLANK ()
)

Revenue YTD =
TOTALYTD ( [Net Revenue], 'Date'[Date] )

Revenue PY =
CALCULATE (
    [Net Revenue],
    SAMEPERIODLASTYEAR ( 'Date'[Date] )
)

Revenue YoY % =
DIVIDE (
    [Net Revenue] - [Revenue PY],
    [Revenue PY],
    BLANK ()
)
```

---

## Length of Stay

> Add `LOS Days` as a calculated column on the Patients table:
> `LOS Days = DATEDIFF ( Patients[Date of Admission], Patients[Discharge Date], DAY )`

```dax
Average LOS = AVERAGE ( Patients[LOS Days] )

Median LOS = MEDIAN ( Patients[LOS Days] )

LOS 0-7 Days =
CALCULATE (
    COUNTROWS ( Patients ),
    Patients[LOS Days] >= 0,
    Patients[LOS Days] <= 7
)

LOS 8-14 Days =
CALCULATE (
    COUNTROWS ( Patients ),
    Patients[LOS Days] >= 8,
    Patients[LOS Days] <= 14
)

LOS 15-30 Days =
CALCULATE (
    COUNTROWS ( Patients ),
    Patients[LOS Days] >= 15,
    Patients[LOS Days] <= 30
)
```

---

## Data Quality

```dax
Records Loaded = COUNTROWS ( Patients )

Records With Negative Billing =
CALCULATE (
    COUNTROWS ( Patients ),
    Patients[Billing Amount] < 0
)

Latest Admission Date = MAX ( Patients[Date of Admission] )

Earliest Admission Date = MIN ( Patients[Date of Admission] )

Data Range Label =
"Data: "
& FORMAT ( [Earliest Admission Date], "mmm yyyy" )
& " – "
& FORMAT ( [Latest Admission Date], "mmm yyyy" )
& " · "
& FORMAT ( [Records Loaded], "#,##0" )
& " records"
```

---

## Format Strings

| Measure | Format |
|---------|--------|
| Total Admissions, Total Discharges | `#,##0` |
| Net Revenue, Gross Revenue | `$#,##0,,,"bn";($#,##0,,,"bn")` |
| Average Billing per Patient | `$#,##0` |
| Refund Rate %, Admissions YoY % | `0.000%` |
| Average LOS | `0.0" days"` |
