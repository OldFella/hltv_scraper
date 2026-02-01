-- =========================
-- USERS
-- =========================
CREATE USER user_write WITH PASSWORD 'writerpass';
CREATE USER user_read_only WITH PASSWORD 'readerpass';

-- =========================
-- TABLES
-- =========================
CREATE TABLE players (
    playerid INT PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE teams (
    teamid INT PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE maps (
    mapid INT PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE sides (
    sideid INT PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE matches (
    matchid INT,
    teamid INT REFERENCES teams (teamid),
    mapid INT REFERENCES maps (mapid),
    sideid INT REFERENCES sides (sideid),
    score INT,
    date DATE,
    PRIMARY KEY (matchid, teamid, mapid, sideid)
);

CREATE TABLE player_stats (
    matchid INT,
    playerid INT REFERENCES players (playerid),
    teamid INT REFERENCES teams (teamid),
    mapid INT REFERENCES maps (mapid),
    sideid INT REFERENCES sides (sideid),
    k INT,
    d INT,
    ek INT,
    ed INT,
    roundswing FLOAT,
    adr FLOAT,
    eadr FLOAT,
    kast FLOAT,
    ekast FLOAT,
    rating FLOAT,
    PRIMARY KEY (matchid, playerid, teamid, mapid, sideid)
);

CREATE TABLE fantasy_overview (
    fantasyid INT PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE fantasies (
    fantasyid INT REFERENCES fantasy_overview (fantasyid),
    teamid INT REFERENCES teams (teamid),
    playerid INT REFERENCES players (playerid),
    cost INT,
    PRIMARY KEY (fantasyid, teamid, playerid)
);

-- =========================
-- INSERTS
-- =========================
INSERT INTO maps (mapid, name) VALUES 
    (0,'All'),
    (1,'anb'),
    (2,'ovp'),
    (3,'anc'),
    (4,'d2'),
    (5,'nuke'),
    (6,'mrg'),
    (7,'inf'),
    (8,'trn'),
    (9,'tcn'),
    (10,'cbl');

INSERT INTO sides (sideid, name) VALUES
    (0,'total'),
    (1,'ct'),
    (2,'t');

-- =========================
-- PRIVILEGES
-- =========================
REVOKE ALL ON SCHEMA public FROM PUBLIC;

-- Writer
GRANT CONNECT ON DATABASE hltv TO user_write;
GRANT USAGE ON SCHEMA public TO user_write;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO user_write;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE ON TABLES TO user_write;

-- Reader
GRANT CONNECT ON DATABASE hltv TO user_read_only;
GRANT USAGE ON SCHEMA public TO user_read_only;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO user_read_only;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO user_read_only;
