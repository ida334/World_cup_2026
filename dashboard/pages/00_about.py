import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
from dashboard.app import get_db, get_model_cached, get_simulation
from dashboard.theme import hero_html, stat_card_html, section_header_html, C_GOLD, C_GREEN, C_BLUE, C_RED

st.markdown(hero_html(
    "World Cup 2026 Predictor",
    "Historical data from 1930–2022 · XGBoost ML model · 10,000 Monte Carlo simulations",
    "🏆",
), unsafe_allow_html=True)

db    = get_db()
model = get_model_cached()
sim   = get_simulation()

n_matches = pd.read_sql("SELECT COUNT(*) AS c FROM matches", db).iloc[0]["c"]
n_teams   = pd.read_sql("SELECT COUNT(DISTINCT home_team) AS c FROM matches", db).iloc[0]["c"]
n_years   = pd.read_sql("SELECT COUNT(DISTINCT year) AS c FROM matches", db).iloc[0]["c"]

top_contender = ""
top_prob      = 0.0
if sim:
    best = max(sim.items(), key=lambda x: x[1].get("winner", 0))
    top_contender = best[0]
    top_prob = best[1].get("winner", 0)

cols = st.columns(4)
cards = [
    ("Historical Matches",  f"{n_matches:,}",     f"{n_years} tournaments",    C_GOLD),
    ("Teams Analysed",      f"{int(n_teams)}",     "across all eras",           C_GREEN),
    ("Model Status",        "Ready" if model else "Not trained", "XGBoost classifier", C_BLUE),
    ("Top Contender",       top_contender or "—",  f"{top_prob:.0%} to win" if top_prob else "run pipeline", C_RED),
]
for col, (label, value, sub, color) in zip(cols, cards):
    col.markdown(stat_card_html(label, value, sub, color), unsafe_allow_html=True)

st.markdown(section_header_html("Explore the Dashboard"), unsafe_allow_html=True)

nav_cols = st.columns(4)
nav_items = [
    ("📊", "Historical Overview", "Tournament winners, goals timeline, world map & country stats"),
    ("⚔️", "Head to Head",        "Compare any two teams and get a live match prediction"),
    ("🏆", "2026 Predictions",    "Group stage probabilities, championship odds & bracket"),
    ("🔍", "Data Explorer",       "Browse and download every match since 1930"),
]
for col, (icon, title, desc) in zip(nav_cols, nav_items):
    col.markdown(f"""
<div style="background:#161b22; border:1px solid #30363d; border-radius:12px;
            padding:20px; height:140px; cursor:default;">
  <div style="font-size:1.6rem; margin-bottom:8px;">{icon}</div>
  <div style="font-weight:700; color:#e6edf3; margin-bottom:6px;">{title}</div>
  <div style="color:#8b949e; font-size:0.8rem; line-height:1.4;">{desc}</div>
</div>
""", unsafe_allow_html=True)

if sim is None:
    st.markdown("<br>", unsafe_allow_html=True)
    st.warning("Predictions not yet generated. Run `python run_pipeline.py` to build the model and simulation.")
