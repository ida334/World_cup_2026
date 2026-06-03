"""
2026 FIFA World Cup group draw (12 groups of 4 teams).
Draw confirmed December 5, 2024 in Miami.
Host nations: USA (Group A), Canada (Group B), Mexico (Group C).
"""

GROUPS_2026 = {
    "A": ["USA",         "Panama",      "Bolivia",     "New Zealand"],
    "B": ["Canada",      "Morocco",     "Belgium",     "Croatia"],
    "C": ["Mexico",      "Argentina",   "Ecuador",     "Chile"],
    "D": ["France",      "Japan",       "Saudi Arabia","Uzbekistan"],
    "E": ["Spain",       "South Korea", "Cameroon",    "Honduras"],
    "F": ["Germany",     "Portugal",    "Cote d'Ivoire","Serbia"],
    "G": ["Brazil",      "Switzerland", "Nigeria",     "Uruguay"],
    "H": ["England",     "Netherlands", "Senegal",     "Poland"],
    "I": ["Italy",       "Turkey",      "Egypt",       "Iraq"],
    "J": ["Peru",        "Colombia",    "Iran",        "Jamaica"],
    "K": ["Denmark",     "Austria",     "Tunisia",     "Venezuela"],
    "L": ["Sweden",      "Czech Republic","Ghana",     "Qatar"],
}

# NOTE: Verify the above against the official FIFA website before running.
# The draw is finalized but late replacements can occur.
# Source: FIFA.com — 2026 FIFA World Cup Group Draw (December 2024)

# ── Fallback features for teams with no World Cup history ─────────────────────
# Used by feature_engineering when a team has zero rows in the DB.
# Values approximate historical WC averages for a debutant / rarely-qualifying team.
NEW_TEAMS_2026_FALLBACK = {
    "New Zealand": {
        "win_rate": 0.15, "gf_per_match": 0.8, "ga_per_match": 1.8,
        "gd_per_match": -1.0, "avg_stage_reached": 1.0,
        "best_stage_reached": 1, "tournaments_played": 3,
        "title_count": 0, "final_appearances": 0, "recent_win_rate": 0.1,
    },
    "Uzbekistan": {
        "win_rate": 0.0,  "gf_per_match": 0.5, "ga_per_match": 2.0,
        "gd_per_match": -1.5, "avg_stage_reached": 1.0,
        "best_stage_reached": 0, "tournaments_played": 0,
        "title_count": 0, "final_appearances": 0, "recent_win_rate": 0.0,
    },
    "Honduras": {
        "win_rate": 0.1,  "gf_per_match": 0.7, "ga_per_match": 1.7,
        "gd_per_match": -1.0, "avg_stage_reached": 1.0,
        "best_stage_reached": 1, "tournaments_played": 3,
        "title_count": 0, "final_appearances": 0, "recent_win_rate": 0.1,
    },
    "Jamaica": {
        "win_rate": 0.1,  "gf_per_match": 0.8, "ga_per_match": 2.0,
        "gd_per_match": -1.2, "avg_stage_reached": 1.0,
        "best_stage_reached": 1, "tournaments_played": 1,
        "title_count": 0, "final_appearances": 0, "recent_win_rate": 0.0,
    },
    "Venezuela": {
        "win_rate": 0.0,  "gf_per_match": 0.5, "ga_per_match": 2.5,
        "gd_per_match": -2.0, "avg_stage_reached": 1.0,
        "best_stage_reached": 0, "tournaments_played": 0,
        "title_count": 0, "final_appearances": 0, "recent_win_rate": 0.0,
    },
    "Iraq": {
        "win_rate": 0.1,  "gf_per_match": 0.7, "ga_per_match": 1.8,
        "gd_per_match": -1.1, "avg_stage_reached": 1.0,
        "best_stage_reached": 1, "tournaments_played": 1,
        "title_count": 0, "final_appearances": 0, "recent_win_rate": 0.0,
    },
    "Qatar": {
        "win_rate": 0.1,  "gf_per_match": 0.7, "ga_per_match": 2.0,
        "gd_per_match": -1.3, "avg_stage_reached": 1.0,
        "best_stage_reached": 1, "tournaments_played": 1,
        "title_count": 0, "final_appearances": 0, "recent_win_rate": 0.1,
    },
    "Bolivia": {
        "win_rate": 0.13, "gf_per_match": 0.8, "ga_per_match": 1.9,
        "gd_per_match": -1.1, "avg_stage_reached": 1.0,
        "best_stage_reached": 1, "tournaments_played": 3,
        "title_count": 0, "final_appearances": 0, "recent_win_rate": 0.0,
    },
    "Panama": {
        "win_rate": 0.0,  "gf_per_match": 0.7, "ga_per_match": 2.3,
        "gd_per_match": -1.6, "avg_stage_reached": 1.0,
        "best_stage_reached": 1, "tournaments_played": 1,
        "title_count": 0, "final_appearances": 0, "recent_win_rate": 0.0,
    },
    "Cote d'Ivoire": {
        "win_rate": 0.2,  "gf_per_match": 1.0, "ga_per_match": 1.3,
        "gd_per_match": -0.3, "avg_stage_reached": 1.0,
        "best_stage_reached": 1, "tournaments_played": 3,
        "title_count": 0, "final_appearances": 0, "recent_win_rate": 0.2,
    },
    "Cameroon": {
        "win_rate": 0.2,  "gf_per_match": 0.9, "ga_per_match": 1.3,
        "gd_per_match": -0.4, "avg_stage_reached": 1.5,
        "best_stage_reached": 3, "tournaments_played": 8,
        "title_count": 0, "final_appearances": 0, "recent_win_rate": 0.15,
    },
    "Ghana": {
        "win_rate": 0.25, "gf_per_match": 1.0, "ga_per_match": 1.2,
        "gd_per_match": -0.2, "avg_stage_reached": 2.0,
        "best_stage_reached": 3, "tournaments_played": 4,
        "title_count": 0, "final_appearances": 0, "recent_win_rate": 0.2,
    },
    "Austria": {
        "win_rate": 0.35, "gf_per_match": 1.5, "ga_per_match": 1.3,
        "gd_per_match": 0.2, "avg_stage_reached": 2.0,
        "best_stage_reached": 4, "tournaments_played": 7,
        "title_count": 0, "final_appearances": 0, "recent_win_rate": 0.3,
    },
}

ALL_TEAMS_2026 = sorted({t for group in GROUPS_2026.values() for t in group})
