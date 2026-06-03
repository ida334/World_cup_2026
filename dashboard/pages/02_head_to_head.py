import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dashboard.app import get_db, get_model_cached
from dashboard.theme import (inject_css, section_header_html, matchup_card_html,
                              prob_bar_html, apply_chart_defaults,
                              C_GOLD, C_GREEN, C_RED, C_BLUE, C_SUBTEXT, C_TEXT,
                              C_SURFACE, C_BORDER, C_SURFACE2)

st.set_page_config(page_title="Head-to-Head", page_icon="⚔️", layout="wide")
inject_css(st)

st.markdown("""
<h1 style="margin-bottom: 4px;">⚔️ Head-to-Head</h1>
<p style="color: #8b949e; margin-top: 0;">Compare any two teams and get a live match probability</p>
""", unsafe_allow_html=True)

conn  = get_db()
model = get_model_cached()

all_teams = sorted(pd.read_sql(
    "SELECT DISTINCT home_team AS t FROM matches UNION SELECT away_team FROM matches ORDER BY t",
    conn)["t"].tolist())

# ── Team selectors ─────────────────────────────────────────────────────────────
col1, col_vs, col2 = st.columns([5, 1, 5])
with col1:
    team_a = st.selectbox("", all_teams, index=all_teams.index("Brazil") if "Brazil" in all_teams else 0,
                          key="h2h_a", label_visibility="collapsed",
                          placeholder="Select Team A")
    st.markdown(f'<div style="text-align:center; font-size:0.9rem; color:{C_SUBTEXT}; margin-top:-8px;">Team A</div>',
                unsafe_allow_html=True)
with col_vs:
    st.markdown(f'<div style="text-align:center; font-size:1.8rem; font-weight:800; color:{C_GOLD}; padding-top:12px;">VS</div>',
                unsafe_allow_html=True)
with col2:
    team_b = st.selectbox("", all_teams, index=all_teams.index("Germany") if "Germany" in all_teams else 1,
                          key="h2h_b", label_visibility="collapsed")
    st.markdown(f'<div style="text-align:center; font-size:0.9rem; color:{C_SUBTEXT}; margin-top:-8px;">Team B</div>',
                unsafe_allow_html=True)

if team_a == team_b:
    st.warning("Please select two different teams.")
    st.stop()

# ── Historical record ──────────────────────────────────────────────────────────
h2h = pd.read_sql(
    """SELECT year, stage, home_team, home_goals, away_goals, away_team,
              win_conditions, attendance
       FROM matches
       WHERE (home_team = ? AND away_team = ?)
          OR (home_team = ? AND away_team = ?)
       ORDER BY year, match_id""",
    conn, params=(team_a, team_b, team_b, team_a),
)

if h2h.empty:
    st.markdown(f"""
<div style="background:{C_SURFACE}; border:1px solid {C_BORDER}; border-radius:12px;
            padding:32px; text-align:center; margin:20px 0;">
  <div style="font-size:2rem; margin-bottom:8px;">📋</div>
  <div style="color:{C_TEXT}; font-size:1.1rem; font-weight:600;">No World Cup meetings on record</div>
  <div style="color:{C_SUBTEXT}; font-size:0.9rem; margin-top:4px;">
    These teams have never met at a FIFA World Cup (1930–2022)</div>
</div>
""", unsafe_allow_html=True)
else:
    def outcome(row):
        if row["home_team"] == team_a:
            if row["home_goals"] > row["away_goals"]: return "Win"
            if row["home_goals"] == row["away_goals"]: return "Draw"
            return "Loss"
        else:
            if row["away_goals"] > row["home_goals"]: return "Win"
            if row["home_goals"] == row["away_goals"]: return "Draw"
            return "Loss"

    h2h["result"] = h2h.apply(outcome, axis=1)
    wins_a  = (h2h["result"] == "Win").sum()
    draws   = (h2h["result"] == "Draw").sum()
    losses  = (h2h["result"] == "Loss").sum()

    # Summary stats row
    st.markdown(section_header_html(f"{team_a} vs {team_b} — World Cup Record"), unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, (label, val, color) in zip([c1, c2, c3, c4], [
        ("Meetings",          str(len(h2h)),    C_GOLD),
        (f"{team_a} Wins",    str(int(wins_a)), C_GREEN),
        ("Draws",             str(int(draws)),  C_BLUE),
        (f"{team_b} Wins",    str(int(losses)), C_RED),
    ]):
        col.markdown(f"""
<div style="background:{C_SURFACE}; border:1px solid {C_BORDER};
            border-top:3px solid {color}; border-radius:10px;
            padding:16px; text-align:center;">
  <div style="color:{C_SUBTEXT}; font-size:0.75rem; text-transform:uppercase;
              letter-spacing:1px; margin-bottom:6px;">{label}</div>
  <div style="color:{C_TEXT}; font-size:2rem; font-weight:800;">{val}</div>
</div>""", unsafe_allow_html=True)

    # Win rate donut
    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
    left_col, right_col = st.columns([3, 2], gap="large", vertical_alignment="top")
    with left_col:
        st.markdown(
            f'<div style="display:flex; align-items:center; gap:10px; margin:0 0 14px 0;">'
            f'<div style="width:4px; height:20px; background:{C_BLUE}; border-radius:2px;"></div>'
            f'<h3 style="margin:0; font-size:1.1rem; font-weight:700; color:{C_TEXT};">Recent Meetings</h3>'
            f'</div>',
            unsafe_allow_html=True,
        )
        for _, row in h2h.tail(5).iloc[::-1].iterrows():
            extra = f"  ·  {row['win_conditions']}" if row.get("win_conditions") else ""
            score = f"{int(row['home_goals'])} – {int(row['away_goals'])}"
            m1, m2, m3 = st.columns([4, 3, 4])
            m1.markdown(
                f"<p style='text-align:right; margin:0; font-weight:700;"
                f" color:{C_TEXT};'>{row['home_team']}</p>",
                unsafe_allow_html=True,
            )
            m2.markdown(
                f"<p style='text-align:center; margin:0; font-weight:800;"
                f" font-size:1.25rem; color:{C_GOLD};'>{score}</p>",
                unsafe_allow_html=True,
            )
            m3.markdown(
                f"<p style='text-align:left; margin:0; font-weight:700;"
                f" color:{C_TEXT};'>{row['away_team']}</p>",
                unsafe_allow_html=True,
            )
            st.caption(f"{int(row['year'])}  ·  {row['stage']}{extra}")
            st.markdown(
                f"<hr style='border:none; border-top:1px solid {C_BORDER};"
                f" margin:4px 0 8px 0;'>",
                unsafe_allow_html=True,
            )

    with right_col:
        donut = go.Figure(go.Pie(
            labels=[f"{team_a}", "Draw", f"{team_b}"],
            values=[wins_a, draws, losses],
            hole=0.65,
            marker=dict(colors=[C_BLUE, C_SUBTEXT, C_RED]),
            textinfo="none",
            hovertemplate="<b>%{label}</b>: %{value} (%{percent})<extra></extra>",
        ))
        donut.add_annotation(
            text=f"<b>{len(h2h)}</b><br>Games",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=C_TEXT),
            xref="paper", yref="paper",
        )
        donut.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.15))
        apply_chart_defaults(donut, 240)
        st.plotly_chart(donut, use_container_width=True)

    # Goals over time
    st.markdown(section_header_html("Goals Scored per Meeting"), unsafe_allow_html=True)
    h2h["a_goals"] = h2h.apply(
        lambda r: r["home_goals"] if r["home_team"] == team_a else r["away_goals"], axis=1)
    h2h["b_goals"] = h2h.apply(
        lambda r: r["away_goals"] if r["home_team"] == team_a else r["home_goals"], axis=1)

    fig_g = go.Figure()
    fig_g.add_trace(go.Scatter(
        x=h2h["year"], y=h2h["a_goals"], name=team_a,
        mode="lines+markers", line=dict(color=C_BLUE, width=2),
        marker=dict(size=7)))
    fig_g.add_trace(go.Scatter(
        x=h2h["year"], y=h2h["b_goals"], name=team_b,
        mode="lines+markers", line=dict(color=C_RED, width=2),
        marker=dict(size=7)))
    fig_g.update_layout(xaxis_title="Year", yaxis_title="Goals")
    apply_chart_defaults(fig_g, 260)
    st.plotly_chart(fig_g, use_container_width=True)

# ── Live prediction ────────────────────────────────────────────────────────────
st.markdown(section_header_html("Match Prediction", C_GOLD), unsafe_allow_html=True)

stage_label = st.selectbox("Stage", ["Group stage", "Round of 32 / Round of 16", "Quarter-final", "Semi-final", "Final"])
stage_map   = {"Group stage": 1, "Round of 32 / Round of 16": 2,
               "Quarter-final": 3, "Semi-final": 4, "Final": 6}
stage_rank  = stage_map[stage_label]

if model is None:
    st.warning("Model not loaded. Run `python run_pipeline.py` first.")
else:
    from src.model import predict_match
    pred = predict_match(team_a, team_b, stage_rank, conn, model)

    # Styled prediction banner
    result_text = {
        "H": f"🟢 Predicted: <b>{team_a}</b> wins",
        "D": "🟡 Predicted: <b>Draw</b>",
        "A": f"🔵 Predicted: <b>{team_b}</b> wins",
    }[pred["predicted_result"]]
    st.markdown(f"""
<div style="background:linear-gradient(90deg,#1a2340,{C_SURFACE});
            border:1px solid {C_GOLD}; border-radius:12px;
            padding:20px 24px; margin:12px 0;">
  <div style="font-size:1.1rem; color:{C_TEXT};">{result_text}</div>
</div>
""", unsafe_allow_html=True)

    # Probability bars — scale to 100% absolute so width reflects true chance
    st.markdown(
        prob_bar_html(f"{team_a} win", pred["home_win_prob"], C_BLUE) +
        prob_bar_html("Draw",          pred["draw_prob"],       C_SUBTEXT) +
        prob_bar_html(f"{team_b} win", pred["away_win_prob"],   C_RED),
        unsafe_allow_html=True,
    )
