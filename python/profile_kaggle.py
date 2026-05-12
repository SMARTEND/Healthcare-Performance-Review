import csv
import os
from collections import Counter, defaultdict
from datetime import datetime
from statistics import mean, median, stdev

PATH = os.path.join(os.path.dirname(__file__), "..", "data", "healthcare_dataset.csv")

rows = []
with open(PATH, "r", encoding="utf-8", errors="ignore") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

n = len(rows)
print(f"TOTAL ROWS: {n:,}")
print(f"COLUMNS: {list(rows[0].keys())}")
print()

def safe_float(v):
    try: return float(v)
    except: return None

def safe_date(v):
    try: return datetime.strptime(v, "%Y-%m-%d")
    except: return None

# Date range
dates = [safe_date(r["Date of Admission"]) for r in rows]
dates = [d for d in dates if d]
print(f"DATE RANGE: {min(dates).date()} to {max(dates).date()}")
print(f"YEARS COVERED: {(max(dates)-min(dates)).days/365.25:.2f}")
print()

# Validate dashboard numbers
billing = [safe_float(r["Billing Amount"]) for r in rows]
billing = [b for b in billing if b is not None]
print(f"=== FINANCIAL ===")
print(f"Total billing (gross): ${sum(billing):,.2f}")
print(f"Total billing (positive only, treating negatives as refunds): ${sum(b for b in billing if b>0):,.2f}")
print(f"Refunds (negative billing): ${sum(b for b in billing if b<0):,.2f}")
print(f"Net billing: ${sum(billing):,.2f}")
print(f"Average billing per patient: ${mean(billing):,.2f}")
print(f"Median billing: ${median(billing):,.2f}")
print(f"Negative billing count (refunds): {sum(1 for b in billing if b<0):,}")
print()

# Length of stay
print("=== LENGTH OF STAY ===")
los_days = []
for r in rows:
    d_in = safe_date(r["Date of Admission"])
    d_out = safe_date(r["Discharge Date"])
    if d_in and d_out:
        los = (d_out - d_in).days
        if los >= 0:
            los_days.append(los)
print(f"Mean LOS: {mean(los_days):.2f} days")
print(f"Median LOS: {median(los_days):.2f} days")
print(f"Min/Max: {min(los_days)} / {max(los_days)}")
# LOS buckets
buckets = {"0-7": 0, "8-14": 0, "15-30": 0, "31+": 0}
for l in los_days:
    if l <= 7: buckets["0-7"] += 1
    elif l <= 14: buckets["8-14"] += 1
    elif l <= 30: buckets["15-30"] += 1
    else: buckets["31+"] += 1
for b, c in buckets.items():
    print(f"  {b} days: {c:,} ({c/len(los_days)*100:.2f}%)")
print()

# Demographics
print("=== DEMOGRAPHICS ===")
print(f"Gender: {Counter(r['Gender'] for r in rows)}")
ages = [int(r["Age"]) for r in rows if r["Age"].isdigit()]
print(f"Age: mean={mean(ages):.1f}, median={median(ages)}, min={min(ages)}, max={max(ages)}")
# Age buckets matching dashboard
age_buckets = {"18-34": 0, "35-49": 0, "50-64": 0, "65-79": 0, "80+": 0}
for a in ages:
    if a <= 34: age_buckets["18-34"] += 1
    elif a <= 49: age_buckets["35-49"] += 1
    elif a <= 64: age_buckets["50-64"] += 1
    elif a <= 79: age_buckets["65-79"] += 1
    else: age_buckets["80+"] += 1
print(f"Age buckets:")
for b, c in age_buckets.items():
    print(f"  {b}: {c:,} ({c/len(ages)*100:.1f}%)")
print()

# Conditions
print("=== MEDICAL CONDITIONS ===")
conditions = Counter(r["Medical Condition"] for r in rows)
for c, count in conditions.most_common():
    print(f"  {c}: {count:,} ({count/n*100:.1f}%)")
print()

# Admission type
print("=== ADMISSION TYPE ===")
adm = Counter(r["Admission Type"] for r in rows)
for a, c in adm.most_common():
    print(f"  {a}: {c:,} ({c/n*100:.1f}%)")
print()

# Test results
print("=== TEST RESULTS ===")
tr = Counter(r["Test Results"] for r in rows)
for t, c in tr.most_common():
    print(f"  {t}: {c:,} ({c/n*100:.1f}%)")
print()

# Insurance providers
print("=== INSURANCE PROVIDER (Net Revenue) ===")
ip_revenue = defaultdict(float)
for r in rows:
    b = safe_float(r["Billing Amount"])
    if b is not None:
        ip_revenue[r["Insurance Provider"]] += b
for ip, rev in sorted(ip_revenue.items(), key=lambda x: -x[1]):
    print(f"  {ip}: ${rev:,.0f}")
print()

# Cross-cut: condition x admission type (real-world clinical patterns?)
print("=== CONDITION x ADMISSION TYPE (% Emergency) ===")
cond_adm = defaultdict(lambda: Counter())
for r in rows:
    cond_adm[r["Medical Condition"]][r["Admission Type"]] += 1
print(f"{'Condition':<15} {'n':>7} {'Elective%':>10} {'Urgent%':>10} {'Emergency%':>11}")
for cond in sorted(cond_adm.keys()):
    c = cond_adm[cond]
    total = sum(c.values())
    print(f"{cond:<15} {total:>7} {c.get('Elective',0)/total*100:>9.1f}% {c.get('Urgent',0)/total*100:>9.1f}% {c.get('Emergency',0)/total*100:>10.1f}%")
print()

# Test results by condition
print("=== TEST RESULTS BY CONDITION (% Abnormal) ===")
cond_tr = defaultdict(lambda: Counter())
for r in rows:
    cond_tr[r["Medical Condition"]][r["Test Results"]] += 1
print(f"{'Condition':<15} {'Abnormal%':>10} {'Normal%':>10} {'Inconclusive%':>14}")
for cond in sorted(cond_tr.keys()):
    c = cond_tr[cond]
    total = sum(c.values())
    print(f"{cond:<15} {c.get('Abnormal',0)/total*100:>9.1f}% {c.get('Normal',0)/total*100:>9.1f}% {c.get('Inconclusive',0)/total*100:>13.1f}%")
print()

# Top hospitals by volume
print("=== TOP 10 HOSPITALS BY VOLUME ===")
hosp = Counter(r["Hospital"] for r in rows)
for h, c in hosp.most_common(10):
    print(f"  {h}: {c:,}")
print(f"Total unique hospitals: {len(hosp):,}")
print()

# Medication
print("=== MEDICATION ===")
med = Counter(r["Medication"] for r in rows)
for m, c in med.most_common():
    print(f"  {m}: {c:,} ({c/n*100:.1f}%)")
print()

# Blood type
print("=== BLOOD TYPE ===")
bt = Counter(r["Blood Type"] for r in rows)
for b, c in bt.most_common():
    print(f"  {b}: {c:,} ({c/n*100:.1f}%)")
print()

# Yearly volume
print("=== ADMISSIONS BY YEAR ===")
year_count = Counter(d.year for d in dates)
for y in sorted(year_count.keys()):
    print(f"  {y}: {year_count[y]:,}")
