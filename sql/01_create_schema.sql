-- World Cup SQLite schema
-- Run once via db_loader.py before any data is loaded

CREATE TABLE IF NOT EXISTS tournaments (
    year             INTEGER PRIMARY KEY,
    host_country     TEXT,
    winner           TEXT,
    runner_up        TEXT,
    third_place      TEXT,
    fourth_place     TEXT,
    goals_scored     INTEGER,
    qualified_teams  INTEGER,
    matches_played   INTEGER,
    attendance       INTEGER
);

CREATE TABLE IF NOT EXISTS matches (
    match_id          INTEGER PRIMARY KEY,
    round_id          INTEGER,
    year              INTEGER,
    match_datetime    TEXT,
    stage             TEXT,
    stage_rank        INTEGER,   -- 0=prelim 1=group 2=R16 3=QF 4=SF 5=3rd 6=Final
    stadium           TEXT,
    city              TEXT,
    home_team         TEXT,
    away_team         TEXT,
    home_goals        INTEGER,
    away_goals        INTEGER,
    ht_home_goals     INTEGER,
    ht_away_goals     INTEGER,
    result            TEXT,      -- 'H' 'D' 'A'  (full-time)
    win_conditions    TEXT,      -- '' 'AET' 'Penalties'
    attendance        INTEGER,
    referee           TEXT,
    home_initials     TEXT,
    away_initials     TEXT,
    FOREIGN KEY (year) REFERENCES tournaments(year)
);

CREATE TABLE IF NOT EXISTS players (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    round_id        INTEGER,
    match_id        INTEGER,
    team            TEXT,
    coach_name      TEXT,
    lineup_type     TEXT,        -- 'S' starter | 'N' non-starter
    shirt_number    INTEGER,
    player_name     TEXT,
    position        TEXT,
    event_raw       TEXT,
    goals           INTEGER DEFAULT 0,
    yellow_cards    INTEGER DEFAULT 0,
    red_cards       INTEGER DEFAULT 0,
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);

CREATE INDEX IF NOT EXISTS idx_matches_year      ON matches(year);
CREATE INDEX IF NOT EXISTS idx_matches_home      ON matches(home_team);
CREATE INDEX IF NOT EXISTS idx_matches_away      ON matches(away_team);
CREATE INDEX IF NOT EXISTS idx_players_match     ON players(match_id);
CREATE INDEX IF NOT EXISTS idx_players_team      ON players(team);
