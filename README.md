# 🏥 U.S. Healthcare Workforce Shortage Dashboard

Interactive Streamlit app analyzing **39,000+ real HRSA government records** to map and explore U.S. healthcare workforce shortages across all 50 states.

**[▶ Live App](https://healthcare-shortage-dashboard.streamlit.app)** · **[Tableau Dashboard](https://public.tableau.com/app/profile/rahma.ras/viz/USHealthcareWorkforceShortageTracker/Dashboard2)**

---

## What it does

- **Choropleth map** — visualizes average HPSA shortage scores by state
- **State comparison tool** — side-by-side metrics for any two states
- **Rural vs. urban breakdown** — surfaces the overlooked reality that non-rural areas account for more underserved people than rural ones
- **Top 15 rankings** — by underserved population and by shortage score
- **Key insights panel** — auto-generated findings from the data (worst state, national gaps, provider shortfall)
- **Embedded SQL queries** — shows the MySQL queries used in the underlying analysis
- **CSV export** — filtered data downloadable directly from the app

## Stack

`Python` · `Streamlit` · `Plotly` · `Pandas` · `MySQL` · `HRSA Open Data`

## Key findings

- **522M+** Americans live in designated shortage areas across 60 states and territories
- The U.S. needs approximately **~X,XXX additional providers** to close all shortage gaps
- Non-rural areas have a *higher* total underserved population than rural — a finding that challenges common assumptions about where shortages occur

## Data source

U.S. Health Resources & Services Administration (HRSA) — Health Professional Shortage Area (HPSA) designations, May 2026.

---

Built by [Rahma Ras](https://rahmaras.github.io) · [LinkedIn](https://linkedin.com/in/rahma-ras) · [GitHub](https://github.com/RahmaRas)
