import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dashboard.app import get_db
from dashboard.theme import (inject_css, section_header_html, apply_chart_defaults,
                              C_GOLD, C_GREEN, C_RED, C_BLUE, C_SUBTEXT,
                              C_TEXT, C_SURFACE, C_BORDER, C_SURFACE2)


st.markdown("""
<h1 style="margin-bottom: 4px;">🔍 Data Explorer</h1>
<p style="color: #8b949e; margin-top: 0;">Browse every World Cup match from 1930 to 2022</p>
""", unsafe_allow_html=True)

conn = get_db()

years     = pd.read_sql("SELECT DISTINCT year FROM matches ORDER BY year", conn)["year"].tolist()
all_teams = sorted(pd.read_sql(
    "SELECT DISTINCT home_team AS t FROM matches UNION SELECT away_team FROM matches ORDER BY t",
    conn)["t"].tolist())
stages    = pd.read_sql("SELECT DISTINCT stage FROM matches ORDER BY stage", conn)["stage"].tolist()

# ── Filters ────────────────────────────────────────────────────────────────────
st.markdown(section_header_html("Filters", C_GOLD), unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    year_range = st.slider("Year range", int(min(years)), int(max(years)),
                           (int(min(years)), int(max(years))))
with col2:
    team_filter = st.multiselect("Teams", all_teams, placeholder="All teams")
with col3:
    stage_filter = st.multiselect("Stage", stages, placeholder="All stages")

query  = """SELECT year, match_datetime, stage, home_team, home_goals, away_goals,
                   away_team, win_conditions, attendance, city, stadium
            FROM matches WHERE year BETWEEN ? AND ?"""
params: list = [year_range[0], year_range[1]]

if team_filter:
    ph = ",".join("?" * len(team_filter))
    query  += f" AND (home_team IN ({ph}) OR away_team IN ({ph}))"
    params += team_filter + team_filter
if stage_filter:
    ph = ",".join("?" * len(stage_filter))
    query  += f" AND stage IN ({ph})"
    params += stage_filter
query += " ORDER BY year, match_id"

df = pd.read_sql(query, conn, params=params)

# ── Result count ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:{C_SURFACE}; border:1px solid {C_BORDER}; border-radius:8px;
            padding:12px 20px; margin:12px 0; display:inline-block;">
  <span style="color:{C_GOLD}; font-weight:700; font-size:1.2rem;">{len(df):,}</span>
  <span style="color:{C_SUBTEXT}; font-size:0.9rem;"> matches match your filters</span>
</div>
""", unsafe_allow_html=True)

# ── Table ──────────────────────────────────────────────────────────────────────
df_display = df.copy()
df_display["Score"] = df["home_goals"].astype(str) + " – " + df["away_goals"].astype(str)
df_display = df_display[["year","match_datetime","stage","home_team","Score",
                          "away_team","win_conditions","attendance","city"]].rename(columns={
    "year": "Year", "match_datetime": "Date", "stage": "Stage",
    "home_team": "Home", "away_team": "Away", "win_conditions": "Extra",
    "attendance": "Attendance", "city": "City",
})

st.dataframe(df_display, use_container_width=True, hide_index=True, height=400)

csv_bytes = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇ Download filtered data as CSV",
    csv_bytes, file_name="worldcup_filtered.csv", mime="text/csv",
)

# ── Team comparison radar ──────────────────────────────────────────────────────
st.markdown(section_header_html("Team Comparison Radar", C_BLUE), unsafe_allow_html=True)

team_stats = pd.read_sql("SELECT * FROM v_team_alltime_stats", conn)

col_r1, col_r2 = st.columns(2)
with col_r1:
    radar_a = st.selectbox("Team A", all_teams,
                           index=all_teams.index("Brazil") if "Brazil" in all_teams else 0, key="ra")
with col_r2:
    radar_b = st.selectbox("Team B", all_teams,
                           index=all_teams.index("Germany") if "Germany" in all_teams else 1, key="rb")


def get_stats(team):
    row = team_stats[team_stats["team"] == team]
    if row.empty:
        return None
    r      = row.iloc[0]
    m      = r["total_matches"] or 1
    titles = pd.read_sql("SELECT COUNT(*) AS c FROM tournaments WHERE winner = ?",
                         conn, params=(team,)).iloc[0]["c"]
    return {
        "Win Rate":    round(r["wins"] / m, 2),
        "GF/Match":   round(r["gf_per_match"], 2),
        "GA/Match":   round(r["ga_per_match"], 2),
        "Tournaments":int(r["tournaments_played"]),
        "Best Stage": int(r["best_stage_reached"]),
        "Titles":     int(titles),
    }


stats_a = get_stats(radar_a)
stats_b = get_stats(radar_b)

if stats_a and stats_b:
    cats   = list(stats_a.keys())
    # Normalize each dimension to [0,1] relative to the pair
    def norm(s):
        return [
            s[k] / max(stats_a[k], stats_b[k]) if max(stats_a[k], stats_b[k]) > 0 else 0
            for k in cats
        ]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=norm(stats_a) + [norm(stats_a)[0]], theta=cats + [cats[0]],
        fill="toself", name=radar_a,
        line=dict(color=C_BLUE, width=2),
        fillcolor=f"rgba(79,156,249,0.2)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=norm(stats_b) + [norm(stats_b)[0]], theta=cats + [cats[0]],
        fill="toself", name=radar_b,
        line=dict(color=C_RED, width=2),
        fillcolor=f"rgba(224,82,82,0.2)",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=C_SURFACE2,
            radialaxis=dict(visible=True, range=[0, 1], gridcolor=C_BORDER,
                            tickfont=dict(color=C_SUBTEXT)),
            angularaxis=dict(gridcolor=C_BORDER, tickfont=dict(color=C_TEXT)),
        ),
        legend=dict(orientation="h", y=-0.1),
    )
    apply_chart_defaults(fig, 420)
    st.plotly_chart(fig, use_container_width=True)

    # Side-by-side stat cards — build complete HTML before calling st.markdown
    c1, c2 = st.columns(2)
    for col, team, stats, color in [(c1, radar_a, stats_a, C_BLUE), (c2, radar_b, stats_b, C_RED)]:
        rows_html = ""
        for k, v in stats.items():
            fmt = f"{v:.1%}" if k == "Win Rate" else str(v)
            rows_html += f"""
<div style="display:flex; justify-content:space-between; padding:6px 0;
            border-bottom:1px solid {C_BORDER};">
  <span style="color:{C_SUBTEXT}; font-size:0.85rem;">{k}</span>
  <span style="color:{C_TEXT}; font-weight:600; font-size:0.85rem;">{fmt}</span>
</div>"""
        col.markdown(f"""
<div style="background:{C_SURFACE}; border:1px solid {C_BORDER};
            border-top:3px solid {color}; border-radius:10px; padding:16px;">
  <div style="font-weight:700; color:{color}; margin-bottom:12px; font-size:1rem;">{team}</div>
  {rows_html}
</div>""", unsafe_allow_html=True)
