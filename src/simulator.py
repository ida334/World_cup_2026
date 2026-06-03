"""
Monte Carlo tournament simulator for the 2026 World Cup.

Each of N_SIMULATIONS iterations independently samples match outcomes
from the model's predicted probability distribution, simulates the full
group stage and knockout bracket, and accumulates stage-advancement counts.

Group stage format: 4 teams, 6 matches each, top 2 advance.
Tiebreak order: points > GD > GF > random.
Knockout: no draws; if model predicts draw, an extra 50/50 coin is flipped
(rough penalty-shootout model).
"""
import json
import os
import sqlite3
import itertools
from typing import Optional

import numpy as np
from xgboost import XGBClassifier

from src.feature_engineering import build_prediction_row, LABEL_INV
from src.groups_2026 import GROUPS_2026, NEW_TEAMS_2026_FALLBACK

N_SIMULATIONS = 10_000
BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIM_PATH       = os.path.join(BASE_DIR, "data", "processed", "simulation_results.json")

# ── Probability cache ──────────────────────────────────────────────────────────
_prob_cache: dict = {}


def _get_probs(home: str, away: str, stage_rank: int,
               model: XGBClassifier, conn: sqlite3.Connection) -> np.ndarray:
    """Return [p_home_win, p_draw, p_away_win] — cached per matchup."""
    key = (home, away, stage_rank)
    if key not in _prob_cache:
        X = build_prediction_row(home, away, stage_rank, conn)
        _prob_cache[key] = model.predict_proba(X)[0]
    return _prob_cache[key]


# ── Single-match sampler ───────────────────────────────────────────────────────

def _sample_match(home: str, away: str, stage_rank: int,
                  model: XGBClassifier, conn: sqlite3.Connection,
                  rng: np.random.Generator,
                  allow_draw: bool = True) -> str:
    """
    Sample one match outcome ('H', 'D', 'A').
    If allow_draw=False (knockout), a draw triggers a 50/50 penalty coin.
    """
    probs = _get_probs(home, away, stage_rank, model, conn)
    outcome = rng.choice(["H", "D", "A"], p=probs)
    if not allow_draw and outcome == "D":
        outcome = rng.choice(["H", "A"])
    return outcome


# ── Group stage ────────────────────────────────────────────────────────────────

def _simulate_group(teams: list[str], model: XGBClassifier,
                    conn: sqlite3.Connection, rng: np.random.Generator) -> list[str]:
    """
    Simulate one group, return [1st, 2nd, 3rd, 4th] order.
    """
    pts  = {t: 0 for t in teams}
    gd   = {t: 0 for t in teams}
    gf   = {t: 0 for t in teams}

    for home, away in itertools.combinations(teams, 2):
        outcome = _sample_match(home, away, 1, model, conn, rng, allow_draw=True)
        hg, ag = _sample_goals(outcome, rng)
        if outcome == "H":
            pts[home] += 3
        elif outcome == "D":
            pts[home] += 1
            pts[away] += 1
        else:
            pts[away] += 3
        gd[home] += hg - ag
        gd[away] += ag - hg
        gf[home] += hg
        gf[away] += ag

    # Sort: pts DESC, gd DESC, gf DESC, random
    noise = {t: rng.random() for t in teams}
    ranked = sorted(teams, key=lambda t: (pts[t], gd[t], gf[t], noise[t]), reverse=True)
    return ranked


def _sample_goals(outcome: str, rng: np.random.Generator) -> tuple[int, int]:
    """Sample a plausible scoreline given the match outcome."""
    # Average goals per match ~2.5; most common outcomes are 1-0, 2-1, 2-0, 1-1
    if outcome == "H":
        hg = rng.choice([1, 2, 3, 4], p=[0.35, 0.40, 0.18, 0.07])
        ag = rng.choice([0, 1, 2],    p=[0.50, 0.38, 0.12])
        ag = min(ag, hg - 1)
    elif outcome == "A":
        ag = rng.choice([1, 2, 3, 4], p=[0.35, 0.40, 0.18, 0.07])
        hg = rng.choice([0, 1, 2],    p=[0.50, 0.38, 0.12])
        hg = min(hg, ag - 1)
    else:  # Draw
        goals = rng.choice([0, 1, 2, 3], p=[0.20, 0.45, 0.28, 0.07])
        hg = ag = goals
    return int(hg), int(ag)


# ── Full tournament simulation ─────────────────────────────────────────────────

def _run_once(model: XGBClassifier, conn: sqlite3.Connection,
              rng: np.random.Generator) -> dict[str, int]:
    """
    Simulate one full tournament.
    Returns {team: final_stage_reached} where stage codes map to:
      1=group exit, 2=R32 exit, 3=R16 exit, 4=QF exit,
      5=SF exit, 6=3rd-place match, 7=finalist, 8=champion
    """
    results = {}

    # ── Group stage ───────────────────────────────────────────────────────────
    first_place, second_place = [], []
    third_place_teams = []

    group_standings = {}
    for gname, teams in GROUPS_2026.items():
        ranked = _simulate_group(teams, model, conn, rng)
        group_standings[gname] = ranked
        first_place.append(ranked[0])
        second_place.append(ranked[1])
        third_place_teams.append(ranked[2])
        for t in ranked[2:]:
            results[t] = 1   # group stage exit

    # Top 2 from each group (24) + best 8 third-place teams (32 total)
    # Simplified: take all 12 first + 12 second + best 8 thirds by random selection
    # (FIFA has complex criteria for which 3rd-place teams qualify)
    rng.shuffle(third_place_teams)
    qualifiers_r32 = first_place + second_place + third_place_teams[:8]
    for t in third_place_teams[8:]:
        results[t] = 1

    # ── Round of 32 (16 matches) ──────────────────────────────────────────────
    rng.shuffle(qualifiers_r32)
    r16_qualifiers = []
    for i in range(0, len(qualifiers_r32), 2):
        home, away = qualifiers_r32[i], qualifiers_r32[i+1]
        outcome = _sample_match(home, away, 2, model, conn, rng, allow_draw=False)
        winner = home if outcome == "H" else away
        loser  = away if outcome == "H" else home
        r16_qualifiers.append(winner)
        results[loser] = 2

    # ── Round of 16 (8 matches) ───────────────────────────────────────────────
    qf_qualifiers = []
    for i in range(0, len(r16_qualifiers), 2):
        home, away = r16_qualifiers[i], r16_qualifiers[i+1]
        outcome = _sample_match(home, away, 2, model, conn, rng, allow_draw=False)
        winner = home if outcome == "H" else away
        loser  = away if outcome == "H" else home
        qf_qualifiers.append(winner)
        results[loser] = 3

    # ── Quarter-finals ────────────────────────────────────────────────────────
    sf_qualifiers = []
    for i in range(0, len(qf_qualifiers), 2):
        home, away = qf_qualifiers[i], qf_qualifiers[i+1]
        outcome = _sample_match(home, away, 3, model, conn, rng, allow_draw=False)
        winner = home if outcome == "H" else away
        loser  = away if outcome == "H" else home
        sf_qualifiers.append(winner)
        results[loser] = 4

    # ── Semi-finals ───────────────────────────────────────────────────────────
    finalists, sf_losers = [], []
    for i in range(0, len(sf_qualifiers), 2):
        home, away = sf_qualifiers[i], sf_qualifiers[i+1]
        outcome = _sample_match(home, away, 4, model, conn, rng, allow_draw=False)
        winner = home if outcome == "H" else away
        loser  = away if outcome == "H" else home
        finalists.append(winner)
        sf_losers.append(loser)
        results[loser] = 5

    # ── 3rd place match ───────────────────────────────────────────────────────
    if len(sf_losers) == 2:
        outcome = _sample_match(sf_losers[0], sf_losers[1], 5, model, conn, rng, allow_draw=False)
        results[sf_losers[0]] = 6 if outcome == "H" else 5
        results[sf_losers[1]] = 5 if outcome == "H" else 6

    # ── Final ─────────────────────────────────────────────────────────────────
    if len(finalists) == 2:
        outcome = _sample_match(finalists[0], finalists[1], 6, model, conn, rng, allow_draw=False)
        winner = finalists[0] if outcome == "H" else finalists[1]
        loser  = finalists[1] if outcome == "H" else finalists[0]
        results[winner] = 8
        results[loser]  = 7

    return results


def run_full_simulation(
    model: XGBClassifier,
    conn: sqlite3.Connection,
    n: int = N_SIMULATIONS,
    seed: int = 42,
) -> dict:
    """
    Run n Monte Carlo simulations.
    Returns {team: {p_group_advance, p_r32, p_r16, p_qf, p_sf, p_final, p_winner}}.
    """
    _prob_cache.clear()
    rng = np.random.default_rng(seed)

    # Accumulate stage counts
    all_teams = [t for group in GROUPS_2026.values() for t in group]
    counts = {t: {"group_advance": 0, "r32": 0, "r16": 0, "qf": 0,
                  "sf": 0, "final": 0, "winner": 0} for t in all_teams}

    stage_to_keys = {
        2: ["group_advance"],
        3: ["group_advance", "r32"],
        4: ["group_advance", "r32", "r16"],
        5: ["group_advance", "r32", "r16", "qf"],
        6: ["group_advance", "r32", "r16", "qf", "sf"],
        7: ["group_advance", "r32", "r16", "qf", "sf", "final"],
        8: ["group_advance", "r32", "r16", "qf", "sf", "final", "winner"],
    }

    for i in range(n):
        if (i + 1) % 1000 == 0:
            print(f"  Simulation {i+1}/{n}...")
        sim = _run_once(model, conn, rng)
        for team, stage in sim.items():
            for key in stage_to_keys.get(stage, []):
                counts[team][key] += 1

    # Convert counts to probabilities
    probs = {}
    for team, c in counts.items():
        probs[team] = {k: round(v / n, 4) for k, v in c.items()}

    return probs


def save_simulation(results: dict, path: str = SIM_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"  Simulation results saved")


def load_simulation(path: str = SIM_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_top_predictions(results: dict, n: int = 10) -> list[dict]:
    """Return top n teams by P(winner), sorted descending."""
    rows = [
        {"team": t, **probs}
        for t, probs in results.items()
    ]
    rows.sort(key=lambda r: r["winner"], reverse=True)
    return rows[:n]
