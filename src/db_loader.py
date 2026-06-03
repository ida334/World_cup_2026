"""
CSV → SQLite ETL.
Handles all data-quality issues before inserting, then runs SQL cleaning scripts.
"""
import re
import sqlite3
import os
import pandas as pd

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW   = os.path.join(BASE_DIR, "data", "raw")
DATA_PROC  = os.path.join(BASE_DIR, "data", "processed")
SQL_DIR    = os.path.join(BASE_DIR, "sql")
DB_PATH    = os.path.join(DATA_PROC, "worldcup.db")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_attendance(value) -> int | None:
    """'1.045.246' → 1045246.  Handles NaN, empty string, and plain integers."""
    if pd.isna(value) or str(value).strip() == "":
        return None
    s = str(value).strip().replace(".", "").replace(",", "")
    try:
        return int(float(s))
    except ValueError:
        return None


def _fix_team_name(name) -> str:
    """Strip HTML-encoding artefacts and extra whitespace."""
    if pd.isna(name):
        return ""
    s = str(name).strip()
    s = re.sub(r'^rn">', '', s)
    return s.strip()


def _safe_int(value) -> int | None:
    if pd.isna(value):
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


# ── Loaders ────────────────────────────────────────────────────────────────────

def load_tournaments(conn: sqlite3.Connection, paths: list[str]):
    cursor = conn.cursor()
    for path in paths:
        df = pd.read_csv(path, encoding="utf-8", dtype=str)
        for _, row in df.iterrows():
            year = _safe_int(row.get("Year"))
            if year is None:
                continue
            cursor.execute(
                """INSERT OR REPLACE INTO tournaments
                   (year, host_country, winner, runner_up, third_place, fourth_place,
                    goals_scored, qualified_teams, matches_played, attendance)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    year,
                    str(row.get("Country", "")).strip(),
                    str(row.get("Winner", "")).strip(),
                    str(row.get("Runners-Up", "")).strip(),
                    str(row.get("Third", "")).strip(),
                    str(row.get("Fourth", "")).strip(),
                    _safe_int(row.get("GoalsScored")),
                    _safe_int(row.get("QualifiedTeams")),
                    _safe_int(row.get("MatchesPlayed")),
                    _parse_attendance(row.get("Attendance")),
                ),
            )
    conn.commit()
    print(f"  Tournaments loaded")


def load_matches(conn: sqlite3.Connection, paths: list[str]):
    cursor = conn.cursor()
    total = 0
    for path in paths:
        df = pd.read_csv(path, encoding="utf-8", dtype=str)
        for _, row in df.iterrows():
            year = _safe_int(row.get("Year"))
            if year is None:
                continue
            home = _fix_team_name(row.get("Home Team Name"))
            away = _fix_team_name(row.get("Away Team Name"))
            if not home or not away:
                continue
            cursor.execute(
                """INSERT OR REPLACE INTO matches
                   (match_id, round_id, year, match_datetime, stage,
                    stadium, city, home_team, away_team,
                    home_goals, away_goals, ht_home_goals, ht_away_goals,
                    win_conditions, attendance, referee,
                    home_initials, away_initials)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    _safe_int(row.get("MatchID")),
                    _safe_int(row.get("RoundID")),
                    year,
                    str(row.get("Datetime", "")).strip(),
                    str(row.get("Stage", "")).strip(),
                    str(row.get("Stadium", "")).strip(),
                    str(row.get("City", "")).strip(),
                    home,
                    away,
                    _safe_int(row.get("Home Team Goals")),
                    _safe_int(row.get("Away Team Goals")),
                    _safe_int(row.get("Half-time Home Goals")),
                    _safe_int(row.get("Half-time Away Goals")),
                    str(row.get("Win conditions", "")).strip(),
                    _parse_attendance(row.get("Attendance")),
                    str(row.get("Referee", "")).strip(),
                    str(row.get("Home Team Initials", "")).strip(),
                    str(row.get("Away Team Initials", "")).strip(),
                ),
            )
            total += 1
    conn.commit()
    print(f"  Matches loaded: {total}")


def load_players(conn: sqlite3.Connection, paths: list[str]):
    cursor = conn.cursor()
    total = 0
    for path in paths:
        df = pd.read_csv(path, encoding="utf-8", dtype=str)
        for _, row in df.iterrows():
            match_id = _safe_int(row.get("MatchID"))
            round_id = _safe_int(row.get("RoundID"))
            if match_id is None:
                continue
            team = _fix_team_name(row.get("Team Initials"))
            shirt = _safe_int(row.get("Shirt Number"))
            cursor.execute(
                """INSERT INTO players
                   (round_id, match_id, team, coach_name, lineup_type,
                    shirt_number, player_name, position, event_raw)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    round_id,
                    match_id,
                    team,
                    str(row.get("Coach Name", "")).strip(),
                    str(row.get("Line-up", "")).strip(),
                    shirt,
                    str(row.get("Player Name", "")).strip(),
                    str(row.get("Position", "")).strip(),
                    str(row.get("Event", "")).strip(),
                ),
            )
            total += 1
    conn.commit()
    print(f"  Players loaded: {total}")


def _run_sql_file(conn: sqlite3.Connection, filename: str):
    path = os.path.join(SQL_DIR, filename)
    with open(path, encoding="utf-8") as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()
    print(f"  Ran {filename}")


# ── Main entry point ───────────────────────────────────────────────────────────

def build_database(force_rebuild: bool = False):
    os.makedirs(DATA_PROC, exist_ok=True)
    if force_rebuild and os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    try:
        print("Creating schema...")
        _run_sql_file(conn, "01_create_schema.sql")

        print("Loading tournaments...")
        load_tournaments(conn, [
            os.path.join(DATA_RAW, "WorldCups.csv"),
            os.path.join(DATA_RAW, "WorldCups_2018_2022.csv"),
        ])

        print("Loading matches...")
        load_matches(conn, [
            os.path.join(DATA_RAW, "WorldCupMatches.csv"),
            os.path.join(DATA_RAW, "WorldCupMatches_2018_2022.csv"),
        ])

        print("Loading players...")
        load_players(conn, [
            os.path.join(DATA_RAW, "WorldCupPlayers.csv"),
        ])

        print("Cleaning data...")
        _run_sql_file(conn, "02_clean_data.sql")

        print("Normalizing team names...")
        _run_sql_file(conn, "03_normalize_teams.sql")

        print("Creating views...")
        _run_sql_file(conn, "04_create_views.sql")

        # Quick sanity check
        cur = conn.cursor()
        n_matches = cur.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
        n_teams   = cur.execute("SELECT COUNT(DISTINCT home_team) FROM matches").fetchone()[0]
        print(f"  DB ready: {n_matches} matches across {n_teams} teams")
    finally:
        conn.close()

    return DB_PATH


def get_connection() -> sqlite3.Connection:
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run run_pipeline.py first.")
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == "__main__":
    build_database(force_rebuild=True)
