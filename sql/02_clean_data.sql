-- Post-load cleaning: applied after CSV data is inserted via db_loader.py

-- Strip HTML-encoding artifacts (rn"> prefix from some team names)
UPDATE matches SET home_team = REPLACE(home_team, 'rn">', '') WHERE home_team LIKE 'rn">%';
UPDATE matches SET away_team = REPLACE(away_team, 'rn">', '') WHERE away_team LIKE 'rn">%';
UPDATE players  SET team     = REPLACE(team,      'rn">', '') WHERE team      LIKE 'rn">%';

-- Trim stray whitespace
UPDATE matches SET home_team = TRIM(home_team);
UPDATE matches SET away_team = TRIM(away_team);
UPDATE matches SET city      = TRIM(city);
UPDATE matches SET stadium   = TRIM(stadium);
UPDATE players SET team      = TRIM(team);
UPDATE players SET player_name = TRIM(player_name);

-- Populate result column from goal counts
UPDATE matches SET result =
    CASE
        WHEN home_goals > away_goals THEN 'H'
        WHEN home_goals = away_goals THEN 'D'
        ELSE 'A'
    END
WHERE result IS NULL OR result = '';

-- Normalize win_conditions to '', 'AET', or 'Penalties'
UPDATE matches SET win_conditions = ''
    WHERE win_conditions IS NULL
       OR win_conditions = '';

UPDATE matches SET win_conditions = 'AET'
    WHERE LOWER(win_conditions) LIKE '%extra time%'
       OR LOWER(win_conditions) LIKE '%aet%'
       OR win_conditions = 'AET';

UPDATE matches SET win_conditions = 'Penalties'
    WHERE LOWER(win_conditions) LIKE '%penalt%'
       OR LOWER(win_conditions) LIKE '%shoot%'
       OR win_conditions = 'Penalties';

-- Populate stage_rank
UPDATE matches SET stage_rank =
    CASE
        WHEN stage = 'Preliminary round'                      THEN 0
        WHEN stage IN ('Group 1','Group 2','Group 3','Group 4',
                       'Group A','Group B','Group C','Group D',
                       'Group E','Group F','Group G','Group H',
                       'First round')                         THEN 1
        WHEN stage = 'Round of 16'                            THEN 2
        WHEN stage = 'Quarter-finals'                         THEN 3
        WHEN stage = 'Semi-finals'                            THEN 4
        WHEN stage IN ('Match for third place',
                       'Play-off for third place',
                       'Third place')                         THEN 5
        WHEN stage = 'Final'                                  THEN 6
        ELSE 1
    END;

-- Null out shirt numbers of 0 (historical data gap marker)
UPDATE players SET shirt_number = NULL WHERE shirt_number = 0;

-- Parse player events into structured columns
UPDATE players SET goals = 0, yellow_cards = 0, red_cards = 0;

-- Goals  (G, OG patterns like G19' or G1' OG45')
UPDATE players SET goals = goals + 1
    WHERE event_raw LIKE '%G%''%'
      AND event_raw NOT LIKE '%OG%';

-- Yellow cards
UPDATE players SET yellow_cards = yellow_cards + 1
    WHERE event_raw LIKE '%Y%''%';

-- Red cards (R or second yellow 2Y)
UPDATE players SET red_cards = red_cards + 1
    WHERE event_raw LIKE '%R%''%'
       OR event_raw LIKE '%2Y%''%';
