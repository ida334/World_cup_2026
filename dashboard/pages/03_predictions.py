import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dashboard.app import get_db, get_model_cached, get_simulation
from dashboard.theme import (inject_css, section_header_html, prob_bar_html,
                              apply_chart_defaults,
                              C_GOLD, C_GREEN, C_RED, C_BLUE, C_SUBTEXT,
                              C_TEXT, C_SURFACE, C_BORDER, C_SURFACE2)
from src.groups_2026 import GROUPS_2026


st.markdown("""
<h1 style="margin-bottom: 4px;">🏆 2026 World Cup Predictions</h1>
<p style="color: #8b949e; margin-top: 0;">Based on 10,000 Monte Carlo simulations · XGBoost model trained on 1930–2022 data</p>
""", unsafe_allow_html=True)

conn  = get_db()
model = get_model_cached()
sim   = get_simulation()

if sim is None:
    st.error("Simulation not found. Run `python run_pipeline.py` to generate predictions.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["🏅 Championship Odds", "📊 Group Stage", "⚡ Match Predictor"])


# ── Tab 1: Championship Odds ──────────────────────────────────────────────────
with tab1:
    st.markdown(section_header_html("Championship Contenders — Top 20", C_GOLD), unsafe_allow_html=True)

    rows = []
    for team, probs in sim.items():
        rows.append({
            "Team":        team,
            "P(Champion)": probs.get("winner", 0),
            "P(Final)":    probs.get("final", 0),
            "P(Semi)":     probs.get("sf", 0),
            "P(QF)":       probs.get("qf", 0),
            "P(Advance)":  probs.get("group_advance", 0),
        })
    df_odds = (pd.DataFrame(rows)
               .sort_values("P(Champion)", ascending=False)
               .reset_index(drop=True))
    top20 = df_odds.head(20)

    # Podium cards for top 3
    p1, p2, p3 = st.columns(3)
    medals = ["🥇", "🥈", "🥉"]
    medal_colors = [C_GOLD, "#9aa5b4", "#cd7f32"]
    for col, medal, color, (_, row) in zip([p1, p2, p3], medals, medal_colors, df_odds.head(3).iterrows()):
        col.markdown(f"""
<div style="background:{C_SURFACE}; border:1px solid {C_BORDER};
            border-top:4px solid {color}; border-radius:12px;
            padding:24px; text-align:center; margin-bottom:16px;">
  <div style="font-size:2rem;">{medal}</div>
  <div style="font-size:1.2rem; font-weight:800; color:{C_TEXT}; margin:8px 0 4px;">{row['Team']}</div>
  <div style="font-size:1.8rem; font-weight:700; color:{color};">{row['P(Champion)']:.1%}</div>
  <div style="color:{C_SUBTEXT}; font-size:0.8rem; margin-top:4px;">to win the tournament</div>
</div>""", unsafe_allow_html=True)

    # Horizontal bar chart — custom left margin so team names aren't clipped
    fig = go.Figure(go.Bar(
        x=top20["P(Champion)"],
        y=top20["Team"],
        orientation="h",
        marker=dict(
            color=top20["P(Champion)"],
            colorscale=[[0, "#1a2a1a"], [0.4, C_GREEN], [1, C_GOLD]],
            showscale=False,
        ),
        text=[f"{v:.1%}" for v in top20["P(Champion)"]],
        textposition="outside",
        textfont=dict(color=C_TEXT, size=11),
        hovertemplate="<b>%{y}</b><br>P(Champion): %{x:.1%}<extra></extra>",
    ))
    fig.update_layout(
        xaxis=dict(tickformat=".0%",
                   range=[0, top20["P(Champion)"].max() * 1.3]),
        yaxis=dict(autorange="reversed"),
    )
    apply_chart_defaults(fig, 520, margin=dict(l=130, r=80, t=16, b=40))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(section_header_html("Full Probability Table — All 48 Teams"), unsafe_allow_html=True)
    # Use column_config instead of background_gradient — no matplotlib dependency
    st.dataframe(
        df_odds,
        column_config={
            "P(Champion)": st.column_config.ProgressColumn(
                "P(Champion)", min_value=0,
                max_value=float(df_odds["P(Champion)"].max()),
                format="%.1f%%",
            ),
            "P(Final)":   st.column_config.NumberColumn("P(Final)",   format="%.1f%%"),
            "P(Semi)":    st.column_config.NumberColumn("P(Semi)",    format="%.1f%%"),
            "P(QF)":      st.column_config.NumberColumn("P(QF)",      format="%.1f%%"),
            "P(Advance)": st.column_config.NumberColumn("P(Advance)", format="%.1f%%"),
        },
        use_container_width=True, hide_index=True, height=400,
    )


# ── Tab 2: Group Stage ────────────────────────────────────────────────────────
with tab2:
    st.markdown(section_header_html("Group Stage Advancement Probabilities", C_GREEN), unsafe_allow_html=True)
    st.caption("P(Advance) = probability of qualifying from the group stage")

    group_names = list(GROUPS_2026.keys())
    cols_per_row = 3

    for row_start in range(0, len(group_names), cols_per_row):
        row_groups = group_names[row_start:row_start + cols_per_row]
        # Pad to always have cols_per_row columns so layout is consistent
        st_cols = st.columns(cols_per_row)

        for col_idx, gname in enumerate(row_groups):
            teams = GROUPS_2026[gname]
            group_rows = [
                (t,
                 sim.get(t, {}).get("group_advance", 0),
                 sim.get(t, {}).get("winner", 0))
                for t in teams
            ]
            group_rows.sort(key=lambda x: -x[1])
            max_adv = max(r[1] for r in group_rows) if group_rows else 1

            # Build the entire card HTML as one string — avoids the split-div Streamlit bug
            team_rows_html = ""
            for team, p_adv, p_win in group_rows:
                bar_pct = int((p_adv / max_adv) * 100) if max_adv > 0 else 0
                adv_color = (C_GREEN  if p_adv >= 0.5
                             else C_GOLD if p_adv >= 0.3
                             else C_RED)
                team_rows_html += f"""
<div style="margin-bottom:10px;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
    <span style="font-size:0.9rem; font-weight:600; color:{C_TEXT};">{team}</span>
    <span style="font-size:0.85rem; font-weight:700; color:{adv_color};">{p_adv:.0%}</span>
  </div>
  <div style="background:{C_SURFACE2}; border-radius:3px; height:6px;">
    <div style="background:{adv_color}; width:{bar_pct}%; height:100%; border-radius:3px;"></div>
  </div>
  <div style="color:{C_SUBTEXT}; font-size:0.7rem; margin-top:2px;">win tournament: {p_win:.1%}</div>
</div>"""

            card_html = f"""
<div style="background:{C_SURFACE}; border:1px solid {C_BORDER};
            border-radius:12px; padding:16px 16px 8px; margin-bottom:12px;">
  <div style="font-size:0.7rem; text-transform:uppercase; letter-spacing:2px;
              color:{C_SUBTEXT}; margin-bottom:14px; font-weight:600;">Group {gname}</div>
  {team_rows_html}
</div>"""

            with st_cols[col_idx]:
                st.markdown(card_html, unsafe_allow_html=True)


# ── Tab 3: Match Predictor ─────────────────────────────────────────────────────
with tab3:
    st.markdown(section_header_html("Predict Any 2026 Match", C_BLUE), unsafe_allow_html=True)

    all_teams = sorted({t for group in GROUPS_2026.values() for t in group})

    col1, col_vs, col2 = st.columns([5, 1, 5])
    with col1:
        home = st.selectbox("Team A", all_teams, index=0, key="pred_home")
    with col_vs:
        st.markdown(
            f'<div style="text-align:center; font-size:1.5rem; font-weight:800;'
            f' color:{C_GOLD}; padding-top:28px;">VS</div>',
            unsafe_allow_html=True,
        )
    with col2:
        away = st.selectbox("Team B", all_teams, index=1, key="pred_away")

    stage_sel = st.selectbox(
        "Stage",
        ["Group stage", "Round of 32", "Round of 16", "Quarter-final", "Semi-final", "Final"],
    )
    stage_map  = {"Group stage": 1, "Round of 32": 2, "Round of 16": 2,
                  "Quarter-final": 3, "Semi-final": 4, "Final": 6}
    stage_rank = stage_map[stage_sel]

    if model is None:
        st.warning("Model not available. Run `python run_pipeline.py` first.")
    elif home == away:
        st.warning("Please select two different teams.")
    else:
        from src.model import predict_match
        pred = predict_match(home, away, stage_rank, conn, model)

        result_label = {"H": f"{home} wins", "D": "Draw", "A": f"{away} wins"}[pred["predicted_result"]]
        result_color = {"H": C_BLUE, "D": C_GOLD, "A": C_RED}[pred["predicted_result"]]

        st.markdown(f"""
<div style="background:linear-gradient(135deg,#1a2340,{C_SURFACE});
            border:1px solid {result_color}; border-radius:14px;
            padding:28px; text-align:center; margin:16px 0;">
  <div style="font-size:0.9rem; color:{C_SUBTEXT}; margin-bottom:10px;">{stage_sel} &nbsp;·&nbsp; {home} vs {away}</div>
  <div style="font-size:2rem; font-weight:800; color:{result_color};">{result_label}</div>
  <div style="color:{C_SUBTEXT}; font-size:0.8rem; margin-top:8px;">most likely outcome</div>
</div>
""", unsafe_allow_html=True)

        # Bars scale to 100% absolute — width shows true probability, not relative share
        st.markdown(
            prob_bar_html(f"{home} win", pred["home_win_prob"], C_BLUE)
            + prob_bar_html("Draw",       pred["draw_prob"],    C_GOLD)
            + prob_bar_html(f"{away} win",pred["away_win_prob"],C_RED),
            unsafe_allow_html=True,
        )

        # Tournament context cards
        st.markdown("<br>", unsafe_allow_html=True)
        sim_a = sim.get(home, {})
        sim_b = sim.get(away, {})

        ctx_cols = st.columns(2)
        for ctx_col, team, s, color in [
            (ctx_cols[0], home, sim_a, C_BLUE),
            (ctx_cols[1], away, sim_b, C_RED),
        ]:
            bars_html = (
                prob_bar_html("P(Champion)",    s.get("winner", 0),        C_GOLD)
                + prob_bar_html("P(Reach Final)", s.get("final", 0),        C_GREEN)
                + prob_bar_html("P(Advance)",     s.get("group_advance", 0), C_BLUE)
            )
            ctx_col.markdown(f"""
<div style="background:{C_SURFACE}; border:1px solid {C_BORDER};
            border-top:3px solid {color}; border-radius:10px; padding:16px;">
  <div style="font-weight:700; color:{color}; margin-bottom:12px;">{team}</div>
  {bars_html}
</div>""", unsafe_allow_html=True)
