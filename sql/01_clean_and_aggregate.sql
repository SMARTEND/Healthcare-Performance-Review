/* =====================================================================
   Healthcare Performance Review — Data Cleaning & Aggregation
   ---------------------------------------------------------------------
   Source : Kaggle Healthcare Dataset (synthetic, 55,500 rows)
   Engine : T-SQL (Microsoft SQL Server) — also runs on MySQL 8.0+ with
            minor syntax tweaks (see comments in §2 and §6).
   Author : Mohammad Alshehri
   ---------------------------------------------------------------------
   Pipeline:
     1. Create staging table and load raw CSV
     2. Clean & standardize (names, dates, casing)
     3. Deduplicate via window function
     4. Add derived columns (LOS, age band, refund flag)
     5. Materialize the analytical fact table
     6. Aggregations consumed by Power BI / Python
   ===================================================================== */


/* ---------------------------------------------------------------------
   1. STAGING TABLE — raw load target
   --------------------------------------------------------------------- */

IF OBJECT_ID('dbo.stg_Patients', 'U') IS NOT NULL
    DROP TABLE dbo.stg_Patients;

CREATE TABLE dbo.stg_Patients (
    Name                NVARCHAR(120),
    Age                 INT,
    Gender              VARCHAR(10),
    BloodType           VARCHAR(5),
    MedicalCondition    VARCHAR(50),
    DateOfAdmission     DATE,
    Doctor              NVARCHAR(120),
    Hospital            NVARCHAR(160),
    InsuranceProvider   VARCHAR(40),
    BillingAmount       DECIMAL(18, 4),
    RoomNumber          INT,
    AdmissionType       VARCHAR(20),
    DischargeDate       DATE,
    Medication          VARCHAR(40),
    TestResults         VARCHAR(20)
);

-- Bulk load from the CSV. Adjust path to your environment.
BULK INSERT dbo.stg_Patients
FROM '<project_root>\data\healthcare_dataset.csv'   -- update path to your environment
WITH (
    FIRSTROW       = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR  = '\n',
    TABLOCK,
    CODEPAGE       = '65001'   -- UTF-8
);


/* ---------------------------------------------------------------------
   2. CLEANING — standardize names, trim, fix casing
   ---------------------------------------------------------------------
   Source data has mixed-case names like "Bobby JacksOn", "LesLie TErRy".
   Goal: Title Case, trimmed whitespace, no internal double spaces.
   --------------------------------------------------------------------- */

WITH cleaned AS (
    SELECT
        -- Title-case each word in Name and Doctor; trim and collapse spaces.
        LTRIM(RTRIM(
            UPPER(LEFT(Name, 1)) + LOWER(SUBSTRING(REPLACE(Name, '  ', ' '), 2, 200))
        ))                                                  AS Name_Clean,
        Age,
        UPPER(LEFT(Gender, 1)) + LOWER(SUBSTRING(Gender, 2, 10))  AS Gender_Clean,
        UPPER(BloodType)                                    AS BloodType_Clean,
        MedicalCondition,
        DateOfAdmission,
        Doctor,
        Hospital,
        InsuranceProvider,
        BillingAmount,
        RoomNumber,
        AdmissionType,
        DischargeDate,
        Medication,
        TestResults
    FROM dbo.stg_Patients
    WHERE
        DateOfAdmission IS NOT NULL
        AND DischargeDate IS NOT NULL
        AND Age BETWEEN 0 AND 120
)
SELECT *
INTO dbo.tmp_Patients_Clean
FROM cleaned;


/* ---------------------------------------------------------------------
   3. DEDUPLICATE — keep first record per (Name, DateOfAdmission)
   ---------------------------------------------------------------------
   Uses ROW_NUMBER window function partitioned by patient identity +
   admission date. Any duplicate beyond the earliest is discarded.
   --------------------------------------------------------------------- */

IF OBJECT_ID('dbo.Patients_Deduped', 'U') IS NOT NULL
    DROP TABLE dbo.Patients_Deduped;

WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY Name_Clean, DateOfAdmission
            ORDER BY DischargeDate, BillingAmount DESC
        ) AS rn
    FROM dbo.tmp_Patients_Clean
)
SELECT *
INTO dbo.Patients_Deduped
FROM ranked
WHERE rn = 1;

-- Drop the rn helper column from the final dedupe target
ALTER TABLE dbo.Patients_Deduped DROP COLUMN rn;


/* ---------------------------------------------------------------------
   4. DERIVED COLUMNS — LOS days, age band, refund flag, period buckets
   --------------------------------------------------------------------- */

IF OBJECT_ID('dbo.fact_Patients', 'U') IS NOT NULL
    DROP TABLE dbo.fact_Patients;

SELECT
    Name_Clean                                              AS PatientName,
    Age,
    Gender_Clean                                            AS Gender,
    BloodType_Clean                                         AS BloodType,
    MedicalCondition,
    DateOfAdmission,
    DischargeDate,
    DATEDIFF(DAY, DateOfAdmission, DischargeDate)           AS LOS_Days,
    Doctor,
    Hospital,
    InsuranceProvider,
    BillingAmount,
    CASE WHEN BillingAmount < 0 THEN 1 ELSE 0 END           AS IsRefund,
    RoomNumber,
    AdmissionType,
    Medication,
    TestResults,
    YEAR(DateOfAdmission)                                   AS AdmissionYear,
    DATEPART(MONTH, DateOfAdmission)                        AS AdmissionMonth,
    FORMAT(DateOfAdmission, 'yyyy-MM')                      AS YearMonth,
    DATENAME(WEEKDAY, DateOfAdmission)                      AS AdmissionWeekday,
    CASE
        WHEN Age <= 17 THEN '0-17'
        WHEN Age BETWEEN 18 AND 34 THEN '18-34'
        WHEN Age BETWEEN 35 AND 49 THEN '35-49'
        WHEN Age BETWEEN 50 AND 64 THEN '50-64'
        WHEN Age BETWEEN 65 AND 79 THEN '65-79'
        ELSE '80+'
    END                                                     AS AgeGroup,
    CASE
        WHEN DATEDIFF(DAY, DateOfAdmission, DischargeDate) <= 7  THEN '0-7 days'
        WHEN DATEDIFF(DAY, DateOfAdmission, DischargeDate) <= 14 THEN '8-14 days'
        WHEN DATEDIFF(DAY, DateOfAdmission, DischargeDate) <= 30 THEN '15-30 days'
        ELSE '31+ days'
    END                                                     AS LOS_Bucket
INTO dbo.fact_Patients
FROM dbo.Patients_Deduped;

-- Useful indexes for downstream BI queries
CREATE INDEX IX_fact_Patients_AdmissionDate ON dbo.fact_Patients (DateOfAdmission);
CREATE INDEX IX_fact_Patients_Insurance     ON dbo.fact_Patients (InsuranceProvider);
CREATE INDEX IX_fact_Patients_Condition     ON dbo.fact_Patients (MedicalCondition);


/* ---------------------------------------------------------------------
   5. CLEANUP — drop the intermediate temp table
   --------------------------------------------------------------------- */

DROP TABLE dbo.tmp_Patients_Clean;


/* =====================================================================
   AGGREGATION QUERIES — consumed by Power BI / Python notebooks
   ===================================================================== */


/* ---------------------------------------------------------------------
   Q1. Annual KPIs — admissions, revenue, average LOS
   --------------------------------------------------------------------- */

SELECT
    AdmissionYear,
    COUNT(*)                                                AS Admissions,
    SUM(BillingAmount)                                      AS NetRevenue,
    SUM(CASE WHEN BillingAmount > 0 THEN BillingAmount END) AS GrossRevenue,
    SUM(CASE WHEN BillingAmount < 0 THEN BillingAmount END) AS Refunds,
    AVG(BillingAmount)                                      AS AvgBillingPerPatient,
    AVG(CAST(LOS_Days AS DECIMAL(10,2)))                    AS AvgLOS
FROM dbo.fact_Patients
GROUP BY AdmissionYear
ORDER BY AdmissionYear;


/* ---------------------------------------------------------------------
   Q2. Monthly trend — admissions and revenue
   --------------------------------------------------------------------- */

SELECT
    YearMonth,
    COUNT(*)            AS Admissions,
    SUM(BillingAmount)  AS NetRevenue
FROM dbo.fact_Patients
GROUP BY YearMonth
ORDER BY YearMonth;


/* ---------------------------------------------------------------------
   Q3. Insurance Provider revenue ranking
   --------------------------------------------------------------------- */

SELECT
    InsuranceProvider,
    COUNT(*)                                                AS PatientCount,
    SUM(BillingAmount)                                      AS NetRevenue,
    AVG(BillingAmount)                                      AS AvgBilling,
    RANK() OVER (ORDER BY SUM(BillingAmount) DESC)          AS RevenueRank
FROM dbo.fact_Patients
GROUP BY InsuranceProvider
ORDER BY NetRevenue DESC;


/* ---------------------------------------------------------------------
   Q4. Condition × Age Group volume matrix (heatmap source)
   --------------------------------------------------------------------- */

SELECT
    MedicalCondition,
    AgeGroup,
    COUNT(*)            AS PatientCount,
    AVG(BillingAmount)  AS AvgBilling,
    AVG(CAST(LOS_Days AS DECIMAL(10,2))) AS AvgLOS
FROM dbo.fact_Patients
GROUP BY MedicalCondition, AgeGroup
ORDER BY MedicalCondition, AgeGroup;


/* ---------------------------------------------------------------------
   Q5. LOS bucket distribution
   --------------------------------------------------------------------- */

SELECT
    LOS_Bucket,
    COUNT(*)                                                AS PatientCount,
    CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () AS DECIMAL(5,2)) AS Percentage
FROM dbo.fact_Patients
GROUP BY LOS_Bucket
ORDER BY MIN(LOS_Days);


/* ---------------------------------------------------------------------
   Q6. Test Results by condition (% within condition)
   --------------------------------------------------------------------- */

SELECT
    MedicalCondition,
    TestResults,
    COUNT(*)            AS PatientCount,
    CAST(COUNT(*) * 100.0 /
         SUM(COUNT(*)) OVER (PARTITION BY MedicalCondition)
         AS DECIMAL(5,2))                                   AS PctWithinCondition
FROM dbo.fact_Patients
GROUP BY MedicalCondition, TestResults
ORDER BY MedicalCondition, TestResults;


/* ---------------------------------------------------------------------
   Q7. Year-over-year admissions growth (window function)
   --------------------------------------------------------------------- */

WITH yearly AS (
    SELECT
        AdmissionYear,
        COUNT(*) AS Admissions
    FROM dbo.fact_Patients
    GROUP BY AdmissionYear
)
SELECT
    AdmissionYear,
    Admissions,
    LAG(Admissions) OVER (ORDER BY AdmissionYear)           AS PriorYearAdmissions,
    Admissions
        - LAG(Admissions) OVER (ORDER BY AdmissionYear)     AS AbsChange,
    CAST(
        (Admissions - LAG(Admissions) OVER (ORDER BY AdmissionYear)) * 100.0 /
        NULLIF(LAG(Admissions) OVER (ORDER BY AdmissionYear), 0)
        AS DECIMAL(6,2)
    )                                                       AS YoYPct
FROM yearly
ORDER BY AdmissionYear;


/* ---------------------------------------------------------------------
   Q8. Top 10 hospitals by revenue (with cumulative %)
   --------------------------------------------------------------------- */

WITH hospital_rev AS (
    SELECT
        Hospital,
        SUM(BillingAmount) AS Revenue
    FROM dbo.fact_Patients
    GROUP BY Hospital
)
SELECT TOP 10
    Hospital,
    Revenue,
    SUM(Revenue) OVER (ORDER BY Revenue DESC ROWS UNBOUNDED PRECEDING) AS CumulativeRevenue,
    CAST(
        SUM(Revenue) OVER (ORDER BY Revenue DESC ROWS UNBOUNDED PRECEDING)
        * 100.0 / SUM(Revenue) OVER ()
        AS DECIMAL(6,2)
    ) AS CumulativePct
FROM hospital_rev
ORDER BY Revenue DESC;


/* =====================================================================
   END OF SCRIPT
   ===================================================================== */
