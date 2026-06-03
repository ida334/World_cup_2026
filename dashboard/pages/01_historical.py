import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dashboard.app import get_db
from dashboard.theme import (inject_css, section_header_html, apply_chart_defaults,
                              C_GOLD, C_GREEN, C_BLUE, C_SURFACE, C_BORDER,
                              C_SUBTEXT, C_TEXT, TEAM_COLORS)

st.set_page_config(page_title="Historical Overview", page_icon="📊", layout="wide")
inject_css(st)

st.markdown("""
<h1 style="margin-bottom: 4px;">📊 Historical Overview</h1>
<p style="color: #8b949e; margin-top: 0;">World Cup data from 1930 to 2022 — 22 tournaments</p>
""", unsafe_allow_html=True)

conn = get_db()

tournaments = pd.read_sql("SELECT * FROM tournaments ORDER BY year", conn)
team_stats  = pd.read_sql("SELECT * FROM v_team_alltime_stats ORDER BY wins DESC", conn)
year_data   = pd.read_sql(
    """SELECT year,
              SUM(home_goals + away_goals) AS total_goals,
              COUNT(*) AS matches,
              ROUND(CAST(SUM(home_goals + away_goals) AS REAL) / COUNT(*), 2) AS goals_per_match,
              SUM(attendance) AS total_attendance
       FROM matches GROUP BY year ORDER BY year""", conn)

# ── Row 1: two charts side-by-side ────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.markdown(section_header_html("Goals per Match Over Time", C_GOLD), unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=year_data["year"], y=year_data["goals_per_match"],
        mode="lines+markers",
        name="Goals/Match",
        fill="tozeroy",
        fillcolor="rgba(230,168,23,0.12)",
        line=dict(color=C_GOLD, width=2.5),
        marker=dict(size=6, color=C_GOLD),
        hovertemplate="<b>%{x}</b><br>Goals/Match: %{y:.2f}<extra></extra>",
    ))
    fig.update_layout(
        xaxis_title="Year", yaxis_title="Goals / Match",
        hovermode="x unified", showlegend=False,
    )
    apply_chart_defaults(fig, 300)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown(section_header_html("Tournament Attendance", C_GREEN), unsafe_allow_html=True)

    fig2 = go.Figure(go.Bar(
        x=tournaments["year"], y=tournaments["attendance"],
        marker=dict(
            color=tournaments["attendance"],
            colorscale=[[0, "#1a3a1a"], [1, C_GREEN]],
            showscale=False,
        ),
        hovertemplate="<b>%{x}</b><br>Attendance: %{y:,.0f}<extra></extra>",
    ))
    fig2.update_layout(xaxis_title="Year", yaxis_title="Total Attendance")
    apply_chart_defaults(fig2, 300)
    st.plotly_chart(fig2, use_container_width=True)

# ── World map ──────────────────────────────────────────────────────────────────
st.markdown(section_header_html("World Cup Titles by Country", C_GOLD), unsafe_allow_html=True)
win_map = pd.read_sql(
    "SELECT winner AS country, COUNT(*) AS titles FROM tournaments GROUP BY winner", conn)
fig_map = px.choropleth(
    win_map, locations="country", locationmode="country names",
    color="titles",
    color_continuous_scale=[[0, "#1a2a1a"], [0.3, "#26c281"], [1, "#e6a817"]],
    labels={"titles": "Titles"},
)
fig_map.update_layout(
    paper_bgcolor=C_SURFACE, plot_bgcolor=C_SURFACE,
    geo=dict(
        bgcolor=C_SURFACE,
        showframe=False, showcoastlines=True,
        coastlinecolor=C_BORDER,
        landcolor="#1c2333", oceancolor="#0d1117",
        showocean=True, showlakes=False,
    ),
    coloraxis_colorbar=dict(tickfont=dict(color="#8b949e"), title=dict(font=dict(color="#8b949e"))),
    margin=dict(l=0, r=0, t=0, b=0),
    height=420,
)
st.plotly_chart(fig_map, use_container_width=True)

# ── Champions timeline ─────────────────────────────────────────────────────────
st.markdown(section_header_html("Tournament Champions", C_BLUE), unsafe_allow_html=True)
champ_counts = tournaments.groupby("winner").size().reset_index(name="titles").sort_values("titles", ascending=True)
fig_champ = go.Figure(go.Bar(
    x=champ_counts["titles"], y=champ_counts["winner"],
    orientation="h",
    marker=dict(
        color=champ_counts["titles"],
        colorscale=[[0, "#1a2a3a"], [1, C_GOLD]],
        showscale=False,
    ),
    text=champ_counts["titles"],
    textposition="outside",
    textfont=dict(color=C_GOLD),
    hovertemplate="<b>%{y}</b>: %{x} title(s)<extra></extra>",
))
fig_champ.update_layout(xaxis_title="Titles", yaxis_title="")
apply_chart_defaults(fig_champ, 320)
st.plotly_chart(fig_champ, use_container_width=True)

# ── Country stats table ────────────────────────────────────────────────────────
st.markdown(section_header_html("All-Time Country Performance"), unsafe_allow_html=True)

from src.feature_engineering import CONFEDERATION_MAP
confederation_filter = st.selectbox(
    "Filter by confederation",
    ["All", "UEFA", "CONMEBOL", "CONCACAF", "AFC", "CAF", "OFC"],
)
if confederation_filter != "All":
    filtered_teams = [t for t, c in CONFEDERATION_MAP.items() if c == confederation_filter]
    display = team_stats[team_stats["team"].isin(filtered_teams)].copy()
else:
    display = team_stats.copy()

display["win_rate"] = (display["wins"] / display["total_matches"].replace(0, 1)).round(3)
display = display[[
    "team", "tournaments_played", "total_matches", "wins", "draws", "losses",
    "total_gf", "total_ga", "total_gd", "win_rate", "best_stage_reached"
]].rename(columns={
    "team": "Team", "tournaments_played": "Tournaments", "total_matches": "Matches",
    "wins": "W", "draws": "D", "losses": "L",
    "total_gf": "GF", "total_ga": "GA", "total_gd": "GD",
    "win_rate": "Win Rate", "best_stage_reached": "Best Stage",
})

st.dataframe(
    display,
    column_config={
        "Win Rate": st.column_config.NumberColumn("Win Rate", format="%.1f%%"),
        "W":  st.column_config.ProgressColumn("W", min_value=0,
                  max_value=int(display["W"].max()), format="%d"),
        "GD": st.column_config.NumberColumn("GD"),
    },
    use_container_width=True,
    hide_index=True,
    height=420,
)
