# ⚽ World Cup 2026 Predictor

A full-stack data science project that combines SQL data cleaning, machine learning, and an interactive dashboard to predict the 2026 FIFA World Cup — hosted live on Streamlit Cloud.


---

## What This Project Does

- **Cleans and stores** historical World Cup match data (1930–2022) in a SQLite database using SQL scripts
- **Trains an XGBoost model** on 964 matches with time-decay weighted features to predict match outcomes (Home win / Draw / Away win)
- **Runs 10,000 Monte Carlo simulations** of the full 2026 tournament bracket to estimate each team's probability of advancing, reaching the final, and winning
- **Presents everything** in a dark-themed Streamlit dashboard with 5 pages of interactive charts and tables

---

## Live Demo

🔗 [Open the app on Streamlit Cloud](https://ida334-worldcup2026.streamlit.app/)]

---

## Screenshots

> *Add screenshots by dragging images into this section on GitHub*

| About Page | Historical Overview |
|---|---|
| *Hero banner with live stats* | *Goals per match timeline, world map, country table* |

| Head to Head | 2026 Predictions |
|---|---|
| *Recent meetings, donut chart, live match predictor* | *Group stage odds, championship contenders, match predictor* |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data storage | SQLite (via Python `sqlite3`) |
| Data cleaning | SQL scripts + Pandas |
| Machine learning | XGBoost (multi-class classifier) |
| Simulation | Monte Carlo (10,000 iterations, Python) |
| Dashboard | Streamlit 1.58 |
| Charts | Plotly |
| Language | Python 3.11 |
| Deployment | Streamlit Community Cloud |
| Version control | Git / GitHub |

---

## Project Structure

```
World_cup_2026/
├── data/
│   ├── raw/                        # Original CSVs (1930–2022)
│   │   ├── WorldCupMatches.csv
│   │   ├── WorldCupPlayers.csv
│   │   ├── WorldCups.csv
│   │   ├── WorldCupMatches_2018_2022.csv
│   │   └── WorldCups_2018_2022.csv
│   └── processed/
│       ├── worldcup.db             # Cleaned SQLite database
│       └── simulation_results.json # Pre-run Monte Carlo output
├── sql/
│   ├── 01_create_schema.sql        # Tables, indexes, computed columns
│   ├── 02_clean_data.sql           # HTML fixes, result normalization
│   ├── 03_normalize_teams.sql      # Historical name variants (e.g. Germany FR → Germany)
│   └── 04_create_views.sql         # Aggregation views for dashboard queries
├── src/
│   ├── db_loader.py                # CSV → SQLite ETL
│   ├── feature_engineering.py      # 16 time-decay features per match
│   ├── model.py                    # XGBoost train / save / predict
│   ├── simulator.py                # Monte Carlo tournament simulation
│   └── groups_2026.py              # Official 2026 group draw (12 groups × 4 teams)
├── dashboard/
│   ├── app.py                      # Entry point + shared cache + navigation
│   ├── theme.py                    # Dark navy colour palette + reusable HTML components
│   └── pages/
│       ├── 00_about.py             # Hero banner + live stats
│       ├── 01_historical.py        # Historical charts and country performance table
│       ├── 02_head_to_head.py      # H2H comparison + live match prediction
│       ├── 03_predictions.py       # 2026 odds, group stage, match predictor
│       └── 04_data_explorer.py     # Filterable raw data table + team radar chart
├── models/
│   └── xgb_match_predictor.pkl     # Trained model
├── .streamlit/
│   └── config.toml                 # Dark theme configuration
├── run_pipeline.py                 # One-command pipeline (DB → train → simulate)
└── requirements.txt
```

---

## Machine Learning

The model is an **XGBoost multi-class classifier** predicting Home win / Draw / Away win.

**16 features** per match (home − away differences):

| Feature | Description |
|---|---|
| `win_rate_diff` | Time-decay weighted win rate |
| `gf_per_match_diff` | Goals scored per match |
| `ga_per_match_diff` | Goals conceded per match |
| `avg_stage_reached_diff` | Average stage reached in past WCs |
| `best_stage_reached_diff` | Best-ever stage (0–6 scale) |
| `tournament_appearances_diff` | Number of World Cup appearances |
| `title_count_diff` | World Cup titles won |
| `h2h_win_rate` | Head-to-head win rate (0.5 if no prior meetings) |
| `same_confederation` | 1 if both teams from the same region |
| `is_knockout` | 1 if knock-out stage match |

**Time decay:** recent matches weighted more heavily using `exp(-0.05 × (2026 − year))`

**Result:** 57.1% CV accuracy (±2.1%) vs 55.7% always-home-win baseline

---

## How to Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/ida334/World_cup_2026.git
cd World_cup_2026
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Build the database, train the model, and run the simulation**
```bash
python run_pipeline.py
```

**4. Launch the dashboard**
```bash
python -m streamlit run dashboard/app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Dashboard Pages

| Page | Description |
|---|---|
| **About App** | Overview stats: total matches, teams, model status, top 2026 contender |
| **Historical Overview** | Goals per match over time, attendance chart, world map of WC titles, all-time country stats table |
| **Head to Head** | Pick any two teams — see every World Cup meeting, win/draw/loss breakdown, goals chart, and an ML-powered match prediction |
| **2026 Predictions** | Championship odds for all 48 teams, group stage advancement probabilities, custom match predictor |
| **Data Explorer** | Filter every match since 1930 by year, team, or stage — download as CSV, compare teams on a radar chart |

---

## Data Sources

- [Kaggle — FIFA World Cup Dataset](https://www.kaggle.com/datasets/abecklas/fifa-world-cup) (1930–2014)
- 2018 & 2022 data generated from public match records in the same schema

---

## Author

**Idan Akiva** — [github.com/ida334](https://github.com/ida334)
