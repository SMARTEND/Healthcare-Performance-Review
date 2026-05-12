"""
Healthcare Analytics Project — Dashboard PDF Exporter
Combines all chart PNGs from ./charts/ into a single PDF report.

Output: ./reports/healthcare_dashboard_report.pdf
"""

import os
import glob
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages

# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------
ROOT     = os.path.join(os.path.dirname(__file__), "..")
CHARTS   = os.path.join(ROOT, "charts")
REPORTS  = os.path.join(ROOT, "reports")
OUT_PDF  = os.path.join(REPORTS, "healthcare_dashboard_report.pdf")

os.makedirs(REPORTS, exist_ok=True)

# Styling constants (match generate_charts.py palette)
BLUE_DARK  = "#1F4E79"
BLUE_MID   = "#2E75B6"
BLUE_LIGHT = "#9DC3E6"
GRAY       = "#7F7F7F"

CHART_TITLES = {
    "01_annual_admissions.png":        "Annual Admissions Trend",
    "02_monthly_trend.png":            "Monthly Admissions Trend",
    "03_los_distribution.png":         "Length of Stay Distribution",
    "04_age_groups.png":               "Patient Age Distribution",
    "05_insurance_revenue.png":        "Revenue by Insurance Provider",
    "06_condition_age_heatmap.png":    "Medical Condition × Age Group",
    "07_admission_type.png":           "Admission Type Breakdown",
    "08_test_results_by_condition.png":"Test Results by Condition",
    "09_payer_pareto.png":             "Revenue Concentration (Pareto)",
}

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def cover_page(pdf):
    fig = plt.figure(figsize=(11, 8.5))
    fig.patch.set_facecolor(BLUE_DARK)

    fig.text(0.5, 0.62, "Healthcare Performance Review",
             ha="center", va="center", fontsize=28, fontweight="bold",
             color="white", family="DejaVu Sans")

    fig.text(0.5, 0.52, "Analytics Dashboard Report",
             ha="center", va="center", fontsize=18, color=BLUE_LIGHT,
             family="DejaVu Sans")

    fig.text(0.5, 0.42,
             "Source: Kaggle Healthcare Dataset (synthetic)\n"
             "55,500 records  ·  May 2019 – May 2024",
             ha="center", va="center", fontsize=12, color="white",
             family="DejaVu Sans", linespacing=1.8)

    fig.text(0.5, 0.12, f"Generated: {date.today().strftime('%B %d, %Y')}",
             ha="center", va="center", fontsize=10, color=BLUE_LIGHT,
             family="DejaVu Sans", style="italic")

    pdf.savefig(fig, facecolor=BLUE_DARK)
    plt.close(fig)


def chart_page(pdf, img_path, section_num, title):
    fig = plt.figure(figsize=(11, 8.5))
    fig.patch.set_facecolor("white")

    # Header bar
    ax_header = fig.add_axes([0, 0.92, 1, 0.08])
    ax_header.set_facecolor(BLUE_DARK)
    ax_header.set_axis_off()
    ax_header.text(0.02, 0.5, f"{section_num:02d}  |  {title}",
                   transform=ax_header.transAxes,
                   va="center", fontsize=13, fontweight="bold",
                   color="white", family="DejaVu Sans")

    # Chart image
    ax_img = fig.add_axes([0.02, 0.06, 0.96, 0.84])
    ax_img.set_axis_off()
    img = mpimg.imread(img_path)
    ax_img.imshow(img, aspect="equal")

    # Footer
    fig.text(0.5, 0.01,
             "Healthcare Performance Review  ·  Kaggle Healthcare Dataset (synthetic)",
             ha="center", fontsize=8, color=GRAY, style="italic")

    pdf.savefig(fig, facecolor="white")
    plt.close(fig)


# ----------------------------------------------------------------------
# Build PDF
# ----------------------------------------------------------------------

chart_files = sorted(glob.glob(os.path.join(CHARTS, "*.png")))

if not chart_files:
    raise FileNotFoundError(
        f"No PNG charts found in {CHARTS}. Run generate_charts.py first."
    )

print(f"Found {len(chart_files)} chart(s). Building PDF...")

with PdfPages(OUT_PDF) as pdf:
    # Metadata
    d = pdf.infodict()
    d["Title"]   = "Healthcare Performance Review — Dashboard Report"
    d["Author"]  = "Mohammad Alshehri"
    d["Subject"] = "Healthcare Analytics"

    cover_page(pdf)

    for i, path in enumerate(chart_files, start=1):
        fname = os.path.basename(path)
        title = CHART_TITLES.get(fname, fname.replace("_", " ").replace(".png", "").title())
        chart_page(pdf, path, i, title)
        print(f"  [ok] {fname}")

print(f"\nReport saved to: {OUT_PDF}")
print(f"Total pages: {len(chart_files) + 1} (cover + {len(chart_files)} charts)")
