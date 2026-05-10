# Contributing to Healthcare Performance Review

Thanks for your interest in this project. Contributions, issues, and feature requests are welcome.

This is a portfolio project, but I treat it as a working repo — the same standards apply as for any production codebase.

---

## Ways to Contribute

- 🐛 **Report a bug** — Open an issue with steps to reproduce
- 💡 **Suggest an enhancement** — Open an issue describing the use case
- 📊 **Add a new chart or DAX measure** — Submit a pull request
- 📝 **Improve documentation** — Typos, clarifications, or new examples are always welcome

---

## Local Setup

```bash
# Clone the repo
git clone https://github.com/SMARTEND/Healthcare-Performance-Review.git
cd Healthcare-Performance-Review

# Create a virtual environment (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify the pipeline runs end-to-end
python python/profile_kaggle.py
python python/generate_charts.py
```

For Power BI work you'll also need [Power BI Desktop](https://powerbi.microsoft.com/desktop/) (Windows only).

---

## Pull Request Workflow

1. **Fork** the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes** — keep them focused. One PR = one purpose.
3. **Test your changes** — re-run the relevant script and confirm output is unchanged or improved.
4. **Commit** with a clear message:
   ```bash
   git commit -m "Add: cumulative-revenue chart for payer mix"
   ```
   Conventional prefixes: `Add:`, `Fix:`, `Update:`, `Refactor:`, `Docs:`.
5. **Push** and open a pull request against `main` with:
   - A short description of what changed and why
   - A screenshot if the change affects a visual output
   - A note if any DAX measure or schema field was added/renamed

---

## Code Style

### Python
- Follow PEP 8 (4-space indent, ~100-char lines)
- Prefer explicit names (`monthly_admissions` over `df1`)
- Add a one-line comment when a calculation isn't self-evident
- All charts must include the source-disclaimer footer (see `generate_charts.py`)

### SQL
- Uppercase keywords (`SELECT`, `FROM`, `WHERE`)
- Two-space indent inside CTEs and subqueries
- Comment any non-obvious filter or derived column
- Use CTEs for multi-step logic rather than nested subqueries

### DAX
- Measures use `PascalCase With Spaces` (`Total Admissions`, not `totalAdmissions`)
- Prefer `DIVIDE(num, denom, 0)` over `/` to avoid division-by-zero errors
- Keep one measure per logical KPI; chain via reference rather than copy-paste

---

## Reporting Issues

Open issues at [https://github.com/SMARTEND/Healthcare-Performance-Review/issues](https://github.com/SMARTEND/Healthcare-Performance-Review/issues).

Please include:
- **What you expected to happen**
- **What actually happened** (error message, screenshot, or unexpected output)
- **Steps to reproduce** (commands run, file paths, OS)
- **Environment** (Python version, OS, Power BI Desktop version if relevant)

---

## Data Disclaimer

This project uses the [Kaggle Healthcare Dataset](https://www.kaggle.com/datasets/prasad22/healthcare-dataset) — a **synthetic** dataset. Contributions that cite findings from this data must preserve the synthetic-data caveat. Do not present figures as real clinical insights.

---

## Contact

Questions outside the issue tracker → **mokha9999@hotmail.com**.

Thank you for helping make this project better.
