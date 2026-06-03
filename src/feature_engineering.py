"""
Feature engineering for the match outcome classifier.

Key design decisions:
- Time decay: recent tournaments get exponentially higher weight (lambda=0.05).
  Data from 1970 has ~6% the weight of 2022 data.
- Difference features: model receives (team1_metric - team2_metric) so it
  learns relative strength rather than absolute values.
- Leakage prevention: when building training rows for a match in year Y,
  only data from years < Y is used.
"""
import sqlite3
import math
import numpy as np
import pandas as pd
from typing import Optional

DECAY_LAMBDA = 0.05   # exp(-lambda * years_ago)
REF_YEAR     = 2026   # decay reference point


CONFEDERATION_MAP = {
    "Argentina": "CONMEBOL", "Brazil": "CONMEBOL", "Uruguay": "CONMEBOL",
    "Colombia": "CONMEBOL", "Chile": "CONMEBOL", "Paraguay": "CONMEBOL",
    "Peru": "CONMEBOL", "Ecuador": "CONMEBOL", "Bolivia": "CONMEBOL",
    "Venezuela": "CONMEBOL",
    "Germany": "UEFA", "France": "UEFA", "Spain": "UEFA", "Italy": "UEFA",
    "England": "UEFA", "Netherlands": "UEFA", "Portugal": "UEFA",
    "Belgium": "UEFA", "Croatia": "UEFA", "Serbia": "UEFA",
    "Denmark": "UEFA", "Sweden": "UEFA", "Switzerland": "UEFA",
    "Poland": "UEFA", "Czech Republic": "UEFA", "Hungary": "UEFA",
    "Romania": "UEFA", "Austria": "UEFA", "Scotland": "UEFA",
    "Slovakia": "UEFA", "Slovenia": "UEFA", "Ukraine": "UEFA",
    "Norway": "UEFA", "Albania": "UEFA", "Turkey": "UEFA",
    "Russia": "UEFA", "Yugoslavia": "UEFA", "Czechoslovakia": "UEFA",
    "Wales": "UEFA", "Ireland": "UEFA", "Republic of Ireland": "UEFA",
    "Bosnia and Herzegovina": "UEFA", "North Macedonia": "UEFA",
    "USA": "CONCACAF", "Mexico": "CONCACAF", "Canada": "CONCACAF",
    "Costa Rica": "CONCACAF", "Honduras": "CONCACAF", "Jamaica": "CONCACAF",
    "Panama": "CONCACAF", "El Salvador": "CONCACAF", "Cuba": "CONCACAF",
    "Haiti": "CONCACAF", "Trinidad and Tobago": "CONCACAF",
    "Japan": "AFC", "South Korea": "AFC", "Iran": "AFC",
    "Saudi Arabia": "AFC", "Australia": "AFC", "China": "AFC",
    "Iraq": "AFC", "North Korea": "AFC", "Kuwait": "AFC",
    "Indonesia": "AFC", "United Arab Emirates": "AFC", "Uzbekistan": "AFC",
    "Morocco": "CAF", "Senegal": "CAF", "Nigeria": "CAF",
    "Cameroon": "CAF", "Ghana": "CAF", "Cote d'Ivoire": "CAF",
    "Algeria": "CAF", "Tunisia": "CAF", "Egypt": "CAF",
    "South Africa": "CAF", "DR Congo": "CAF", "Zambia": "CAF",
    "Togo": "CAF", "Angola": "CAF",
    "New Zealand": "OFC",
}


def _decay_weight(year: int) -> float:
    return math.exp(-DECAY_LAMBDA * (REF_YEAR - year))


def compute_team_features(
    team: str,
    as_of_year: int,
    conn: sqlite3.Connection,
    decay: bool = True,
) -> dict:
    """Return a dict of scalar features for `team` using data from years < as_of_year."""
    rows = pd.read_sql(
        """SELECT year, result_for_team, goals_for, goals_against, stage_rank
           FROM v_team_match_results
           WHERE team = ? AND year < ?
           ORDER BY year""",
        conn, params=(team, as_of_year),
    )

    if rows.empty:
        return _zero_team_features()

    if decay:
        rows["w"] = rows["year"].apply(_decay_weight)
    else:
        rows["w"] = 1.0

    W = rows["w"].sum()

    wins   = (rows["w"] * (rows["result_for_team"] == "W")).sum()
    draws  = (rows["w"] * (rows["result_for_team"] == "D")).sum()
    losses = (rows["w"] * (rows["result_for_team"] == "L")).sum()

    gf     = (rows["w"] * rows["goals_for"]).sum()
    ga     = (rows["w"] * rows["goals_against"]).sum()

    win_rate   = wins / W
    gf_per_m   = gf / W
    ga_per_m   = ga / W
    gd_per_m   = (gf - ga) / W
    avg_stage  = (rows["w"] * rows["stage_rank"]).sum() / W

    # Unweighted recent form: last 3 tournaments
    recent_years = sorted(rows["year"].unique())[-3:]
    recent = rows[rows["year"].isin(recent_years)]
    recent_win_rate = (
        (recent["result_for_team"] == "W").mean()
        if len(recent) > 0 else win_rate
    )

    title_rows = pd.read_sql(
        "SELECT COUNT(*) AS c FROM tournaments WHERE winner = ? AND year < ?",
        conn, params=(team, as_of_year),
    )
    titles = int(title_rows["c"].iloc[0])

    final_rows = pd.read_sql(
        """SELECT COUNT(*) AS c FROM v_tournament_placements
           WHERE team = ? AND year < ? AND place_rank <= 2""",
        conn, params=(team, as_of_year),
    )
    finals = int(final_rows["c"].iloc[0])

    tournaments_played = int(rows["year"].nunique())
    best_stage         = int(rows["stage_rank"].max())

    return {
        "win_rate":              round(win_rate, 4),
        "gf_per_match":          round(gf_per_m, 4),
        "ga_per_match":          round(ga_per_m, 4),
        "gd_per_match":          round(gd_per_m, 4),
        "avg_stage_reached":     round(avg_stage, 4),
        "best_stage_reached":    best_stage,
        "tournaments_played":    tournaments_played,
        "title_count":           titles,
        "final_appearances":     finals,
        "recent_win_rate":       round(recent_win_rate, 4),
    }


def _zero_team_features() -> dict:
    return {
        "win_rate": 0.33,           # default to 1-in-3 (rough base rate)
        "gf_per_match": 1.0,
        "ga_per_match": 1.0,
        "gd_per_match": 0.0,
        "avg_stage_reached": 1.0,
        "best_stage_reached": 0,
        "tournaments_played": 0,
        "title_count": 0,
        "final_appearances": 0,
        "recent_win_rate": 0.33,
    }


def compute_h2h_features(
    team_a: str,
    team_b: str,
    as_of_year: int,
    conn: sqlite3.Connection,
) -> dict:
    ta = min(team_a, team_b)
    tb = max(team_a, team_b)

    rows = pd.read_sql(
        """SELECT home_team, away_team, result, year
           FROM v_head_to_head
           WHERE team_a = ? AND team_b = ? AND year < ?
           ORDER BY year DESC""",
        conn, params=(ta, tb, as_of_year),
    )

    if rows.empty:
        return {"h2h_win_rate": 0.5, "h2h_meetings": 0, "h2h_available": 0}

    def team_a_won(row):
        if (row["home_team"] == ta and row["result"] == "H") or \
           (row["away_team"] == ta and row["result"] == "A"):
            return 1
        if row["result"] == "D":
            return 0.5
        return 0

    wins_a = rows.apply(team_a_won, axis=1)
    rate_a = wins_a.mean()
    h2h_rate = rate_a if team_a == ta else 1 - rate_a

    return {
        "h2h_win_rate":   round(h2h_rate, 4),
        "h2h_meetings":   len(rows),
        "h2h_available":  1,
    }


def build_match_feature_row(
    home_team: str,
    away_team: str,
    year: int,
    stage_rank: int,
    conn: sqlite3.Connection,
) -> dict:
    """
    Builds one flat feature row for a (home_team, away_team, year, stage) matchup.
    All team features are differenced: home_val - away_val.
    """
    hf = compute_team_features(home_team, year, conn)
    af = compute_team_features(away_team, year, conn)
    h2h = compute_h2h_features(home_team, away_team, year, conn)

    hconf = CONFEDERATION_MAP.get(home_team, "UNK")
    aconf = CONFEDERATION_MAP.get(away_team, "UNK")

    feature_keys = [
        "win_rate", "gf_per_match", "ga_per_match", "gd_per_match",
        "avg_stage_reached", "best_stage_reached",
        "tournaments_played", "title_count", "final_appearances", "recent_win_rate",
    ]

    row = {}
    for k in feature_keys:
        row[f"{k}_diff"] = round(hf[k] - af[k], 4)

    row["h2h_win_rate"]   = h2h["h2h_win_rate"]
    row["h2h_meetings"]   = h2h["h2h_meetings"]
    row["h2h_available"]  = h2h["h2h_available"]
    row["is_knockout"]    = int(stage_rank >= 2)
    row["stage_rank"]     = stage_rank
    row["same_confederation"] = int(hconf == aconf and hconf != "UNK")

    return row


FEATURE_COLUMNS = [
    "win_rate_diff", "gf_per_match_diff", "ga_per_match_diff", "gd_per_match_diff",
    "avg_stage_reached_diff", "best_stage_reached_diff",
    "tournaments_played_diff", "title_count_diff", "final_appearances_diff",
    "recent_win_rate_diff",
    "h2h_win_rate", "h2h_meetings", "h2h_available",
    "is_knockout", "stage_rank", "same_confederation",
]

LABEL_MAP = {"H": 0, "D": 1, "A": 2}
LABEL_INV = {0: "H", 1: "D", 2: "A"}


def build_training_matrix(conn: sqlite3.Connection):
    """
    Iterates all matches, builds feature rows with leakage prevention.
    Returns (X: np.ndarray, y: np.ndarray, meta: pd.DataFrame).
    meta has columns [year, match_id, home_team, away_team, result].
    """
    matches = pd.read_sql(
        """SELECT match_id, year, home_team, away_team, stage_rank, result
           FROM matches
           WHERE home_goals IS NOT NULL AND away_goals IS NOT NULL
           ORDER BY year, match_id""",
        conn,
    )

    rows, labels, meta_rows = [], [], []
    for _, m in matches.iterrows():
        if m["result"] not in LABEL_MAP:
            continue
        feat = build_match_feature_row(
            m["home_team"], m["away_team"],
            int(m["year"]), int(m["stage_rank"] or 1),
            conn,
        )
        rows.append([feat[c] for c in FEATURE_COLUMNS])
        labels.append(LABEL_MAP[m["result"]])
        meta_rows.append({
            "year": m["year"],
            "match_id": m["match_id"],
            "home_team": m["home_team"],
            "away_team": m["away_team"],
            "result": m["result"],
        })

    X = np.array(rows, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)
    meta = pd.DataFrame(meta_rows)
    return X, y, meta


def build_prediction_row(
    home_team: str,
    away_team: str,
    stage_rank: int,
    conn: sqlite3.Connection,
) -> np.ndarray:
    """Build a single feature row for a 2026 prediction (uses all history)."""
    feat = build_match_feature_row(home_team, away_team, REF_YEAR, stage_rank, conn)
    return np.array([[feat[c] for c in FEATURE_COLUMNS]], dtype=np.float32)
