<p align="center">
  <strong>⚽ World Cup 2026 Predictor</strong>
</p>

<p align="center">
  <strong>10,000 simulations.<br>
  48 teams.<br>
  One champion.</strong>
</p>

<p align="center">
  SQL data cleaning · XGBoost ML model · Monte Carlo simulation · Interactive Streamlit dashboard
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.58-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/XGBoost-ML-FF6600?logo=xgboost&logoColor=white" alt="XGBoost">
  <img src="https://img.shields.io/badge/Plotly-Charts-3F4F75?logo=plotly&logoColor=white" alt="Plotly">
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Data-1930--2022-26c281" alt="Data">
</p>

<p align="center">
  <a href="https://ida334-worldcup2026.streamlit.app/">
    <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Open in Streamlit">
  </a>
</p>

---

## Screenshots

> *Replace the placeholders below by dragging your own screenshots into this file on GitHub*

| About Page | Historical Overview |
|---|---|
| ![About](screenshots/about.png) | ![Historical](screenshots/historical.png) |
| **Head to Head** | **2026 Predictions** |
| ![H2H](screenshots/head_to_head.png) | ![Predictions](screenshots/predictions.png) |

---

## What It Does

- **Cleans 90+ years of World Cup data** — 1930 to 2022 across 4 SQL scripts, fixing encoding issues, normalising team names (e.g. "Germany FR" → "Germany"), and building aggregation views
- **Trains a match predictor** — XGBoost classifier with 16 time-decay features, 5-fold cross-validation, 57% accuracy vs 56% always-home-win baseline
- **Simulates the full 2026 bracket** — 10,000 Monte Carlo runs across 12 groups and 6 knockout rounds to produce win probabilities for all 48 teams
- **Serves it all in a dark dashboard** — 5-page Streamlit app with Plotly charts, interactive filters, and a live match predictor

---

## How It Works

1. **SQL pipeline** loads the raw CSVs into SQLite, strips HTML artifacts, normalises historical country names, and creates views for fast querying
2. **Feature engineering** computes 16 per-match features (win rate, goals, stage history, head-to-head record) with exponential time decay so 2022 data outweighs 1930 data
3. **XGBoost** is trained on all 964 historical World Cup matches, predicting Home / Draw / Away with class-weighted sampling to handle the imbalance
4. **Monte Carlo simulator** plays the full tournament 10,000 times — group stage + knockouts — and saves advancement probabilities per team to JSON
5. **Streamlit** loads the database and simulation at startup (cached) and serves everything live

---

## Dashboard Pages

| Page | What You'll Find |
|---|---|
| 🏠 **About App** | Live stats — total matches, teams, model status, top 2026 contender |
| 📊 **Historical Overview** | Goals per match timeline, attendance chart, world map of titles, sortable all-time country table |
| ⚔️ **Head to Head** | Every World Cup meeting between any two teams, win/draw/loss donut, goals chart, live ML prediction |
| 🏆 **2026 Predictions** | Championship odds for all 48 teams, group stage advancement bars, custom match predictor |
| 🔍 **Data Explorer** | Filter every match since 1930 by year/team/stage, download as CSV, radar chart team comparison |

---

## Project Structure

```
World_cup_2026/
├── data/
│   ├── raw/                        # Original CSVs (1930–2022)
│   └── processed/
│       ├── worldcup.db             # Cleaned SQLite database
│       └── simulation_results.json # Monte Carlo output
├── sql/                            # 4-step cleaning & normalisation pipeline
├── src/
│   ├── db_loader.py                # CSV → SQLite ETL
│   ├── feature_engineering.py      # 16 time-decay features
│   ├── model.py                    # XGBoost train / predict
│   ├── simulator.py                # Monte Carlo simulation
│   └── groups_2026.py              # Official 2026 group draw
├── dashboard/
│   ├── app.py                      # Entry point + navigation
│   ├── theme.py                    # Dark navy design system
│   └── pages/                      # 5 Streamlit pages
├── models/
│   └── xgb_match_predictor.pkl
├── run_pipeline.py                 # One-command: DB → train → simulate
└── requirements.txt
```

---

## Getting Started

**1. Clone**
```bash
git clone https://github.com/ida334/World_cup_2026.git
cd World_cup_2026
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Build database, train model, run simulation**
```bash
python run_pipeline.py
```

**4. Launch dashboard**
```bash
python -m streamlit run dashboard/app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## Model Details

| | |
|---|---|
| Algorithm | XGBoost multi-class (H / D / A) |
| Training samples | 964 World Cup matches (1930–2022) |
| CV accuracy | **57.1% ± 2.1%** |
| Baseline | 55.7% (always predict home win) |
| Top feature | `tournaments_played_diff` (9.1% importance) |
| Time decay | `exp(−0.05 × (2026 − year))` |

---

## Data Sources

- [Kaggle — FIFA World Cup Dataset](https://www.kaggle.com/datasets/abecklas/fifa-world-cup) (1930–2014)
- 2018 & 2022 data added manually from public match records

---

## Author

**Idan Akiva** — [github.com/ida334](https://github.com/ida334)

If this project was useful, consider giving it a ⭐ on GitHub!
