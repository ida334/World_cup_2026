-- Team name normalization: unifies historical name variants to canonical names
-- Applied after cleaning so the ML model sees one continuous record per federation.

-- Mapping table
CREATE TABLE IF NOT EXISTS team_name_map (
    raw_name       TEXT PRIMARY KEY,
    canonical_name TEXT NOT NULL
);

DELETE FROM team_name_map;

INSERT OR REPLACE INTO team_name_map VALUES
    -- West Germany is counted as Germany (FIFA treats records as continuous)
    ('Germany FR',                 'Germany'),
    -- East Germany (only 1974) mapped to a neutral label
    ('German DR',                  'German DR'),
    -- Soviet successor states
    ('Soviet Union',               'Russia'),
    -- Czech successor state
    ('Czechoslovakia',             'Czech Republic'),
    -- Yugoslav successor state (Serbia and Montenegro dissolved 2006)
    ('Yugoslavia',                 'Serbia'),
    ('Serbia and Montenegro',      'Serbia'),
    -- Iran variants
    ('IR Iran',                    'Iran'),
    -- Korea variants
    ('Korea Republic',             'South Korea'),
    ('Korea DPR',                  'North Korea'),
    -- China
    ('China PR',                   'China'),
    -- Ivory Coast
    ('Côte d''Ivoire',             'Cote d''Ivoire'),
    ('C te d''Ivoire',             'Cote d''Ivoire'),
    -- Dutch variants
    ('Holland',                    'Netherlands'),
    -- USA
    ('United States',              'USA'),
    -- Trinidad (already full name in most records, but just in case)
    ('Trinidad And Tobago',        'Trinidad and Tobago'),
    -- Bosnia (HTML-encoded variant cleaned in step 02, but add canonical)
    ('Bosnia and Herzegovina',     'Bosnia and Herzegovina');

-- Apply normalization to matches
UPDATE matches
SET home_team = (SELECT canonical_name FROM team_name_map WHERE raw_name = home_team)
WHERE home_team IN (SELECT raw_name FROM team_name_map);

UPDATE matches
SET away_team = (SELECT canonical_name FROM team_name_map WHERE raw_name = away_team)
WHERE away_team IN (SELECT raw_name FROM team_name_map);

-- Apply to players
UPDATE players
SET team = (SELECT canonical_name FROM team_name_map WHERE raw_name = team)
WHERE team IN (SELECT raw_name FROM team_name_map);

-- Apply to tournaments
UPDATE tournaments
SET winner      = (SELECT canonical_name FROM team_name_map WHERE raw_name = winner)
WHERE winner IN (SELECT raw_name FROM team_name_map);

UPDATE tournaments
SET runner_up   = (SELECT canonical_name FROM team_name_map WHERE raw_name = runner_up)
WHERE runner_up IN (SELECT raw_name FROM team_name_map);

UPDATE tournaments
SET third_place = (SELECT canonical_name FROM team_name_map WHERE raw_name = third_place)
WHERE third_place IN (SELECT raw_name FROM team_name_map);

UPDATE tournaments
SET fourth_place = (SELECT canonical_name FROM team_name_map WHERE raw_name = fourth_place)
WHERE fourth_place IN (SELECT raw_name FROM team_name_map);
