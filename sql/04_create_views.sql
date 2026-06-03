-- Aggregation views used by feature engineering and the dashboard

-- Expand home/away into one row per team per match
CREATE VIEW IF NOT EXISTS v_team_match_results AS
SELECT
    year, match_id, round_id, stage, stage_rank,
    home_team         AS team,
    away_team         AS opponent,
    home_goals        AS goals_for,
    away_goals        AS goals_against,
    ht_home_goals     AS ht_goals_for,
    ht_away_goals     AS ht_goals_against,
    CASE result WHEN 'H' THEN 'W' WHEN 'D' THEN 'D' ELSE 'L' END AS result_for_team,
    win_conditions
FROM matches
UNION ALL
SELECT
    year, match_id, round_id, stage, stage_rank,
    away_team         AS team,
    home_team         AS opponent,
    away_goals        AS goals_for,
    home_goals        AS goals_against,
    ht_away_goals     AS ht_goals_for,
    ht_home_goals     AS ht_goals_against,
    CASE result WHEN 'A' THEN 'W' WHEN 'D' THEN 'D' ELSE 'L' END AS result_for_team,
    win_conditions
FROM matches;

-- All-time team aggregates
CREATE VIEW IF NOT EXISTS v_team_alltime_stats AS
SELECT
    team,
    COUNT(*)                                                        AS total_matches,
    SUM(CASE WHEN result_for_team = 'W' THEN 1 ELSE 0 END)        AS wins,
    SUM(CASE WHEN result_for_team = 'D' THEN 1 ELSE 0 END)        AS draws,
    SUM(CASE WHEN result_for_team = 'L' THEN 1 ELSE 0 END)        AS losses,
    SUM(goals_for)                                                  AS total_gf,
    SUM(goals_against)                                              AS total_ga,
    SUM(goals_for) - SUM(goals_against)                            AS total_gd,
    ROUND(CAST(SUM(goals_for) AS REAL) / COUNT(*), 2)              AS gf_per_match,
    ROUND(CAST(SUM(goals_against) AS REAL) / COUNT(*), 2)          AS ga_per_match,
    COUNT(DISTINCT year)                                            AS tournaments_played,
    ROUND(AVG(CAST(stage_rank AS REAL)), 2)                        AS avg_stage_reached,
    MAX(stage_rank)                                                 AS best_stage_reached
FROM v_team_match_results
GROUP BY team;

-- Head-to-head records (canonical pair: alphabetically sorted)
CREATE VIEW IF NOT EXISTS v_head_to_head AS
SELECT
    CASE WHEN home_team < away_team THEN home_team ELSE away_team END  AS team_a,
    CASE WHEN home_team < away_team THEN away_team ELSE home_team END  AS team_b,
    year,
    match_id,
    stage,
    home_team,
    away_team,
    home_goals,
    away_goals,
    result,
    win_conditions
FROM matches
ORDER BY year, match_id;

-- Aggregated H2H win counts
CREATE VIEW IF NOT EXISTS v_h2h_summary AS
SELECT
    team_a,
    team_b,
    COUNT(*) AS total_matches,
    SUM(CASE
        WHEN (team_a = home_team AND result = 'H') OR
             (team_a = away_team AND result = 'A') THEN 1 ELSE 0
    END) AS team_a_wins,
    SUM(CASE WHEN result = 'D' THEN 1 ELSE 0 END) AS draws,
    SUM(CASE
        WHEN (team_b = home_team AND result = 'H') OR
             (team_b = away_team AND result = 'A') THEN 1 ELSE 0
    END) AS team_b_wins,
    MAX(year) AS last_meeting_year
FROM v_head_to_head
GROUP BY team_a, team_b;

-- Tournament placement records
CREATE VIEW IF NOT EXISTS v_tournament_placements AS
SELECT year, winner      AS team, 'winner'    AS placement, 1 AS place_rank FROM tournaments
UNION ALL
SELECT year, runner_up,           'runner_up',              2               FROM tournaments
UNION ALL
SELECT year, third_place,         'third',                  3               FROM tournaments
UNION ALL
SELECT year, fourth_place,        'fourth',                 4               FROM tournaments;

-- Per-year team stats (used for recent-form features)
CREATE VIEW IF NOT EXISTS v_team_year_stats AS
SELECT
    team,
    year,
    COUNT(*)                                                        AS matches,
    SUM(CASE WHEN result_for_team = 'W' THEN 1 ELSE 0 END)        AS wins,
    SUM(CASE WHEN result_for_team = 'D' THEN 1 ELSE 0 END)        AS draws,
    SUM(CASE WHEN result_for_team = 'L' THEN 1 ELSE 0 END)        AS losses,
    SUM(goals_for)                                                  AS gf,
    SUM(goals_against)                                              AS ga,
    MAX(stage_rank)                                                 AS max_stage
FROM v_team_match_results
GROUP BY team, year;
