CREATE TABLE players (
    playerid INT,
    name varchar(255)
    PRIMARY KEY (playerid)
);

CREATE TABLE teams (
    teamid INT,
    name varchar(255)
    PRIMARY KEY (teamid)
);

CREATE TABLE maps (
    mapid INT,
    name varchar(255)
    PRIMARY KEY (mapid)
);

CREATE TABLE sides (
    sideid INT,
    name varchar(255)
    PRIMARY KEY (sideid)
);

CREATE TABLE matches (
    matchid INT,
    teamid INT REFERENCES teams (teamid),
    mapid INT REFERENCES maps (mapid),
    sideid INT REFERENCES side (sideid),
    score INT,
    date date,
    PRIMARY KEY (matchid, teamid, mapid,sideid)
);

CREATE TABLE player_stats (
    matchid INT,
    playerid INT REFERENCES players (playerid),
    teamid INT REFERENCES teams (teamid),
    mapid INT REFERENCES maps (mapid),
    sideid INT REFERENCES side (sideid),
    k INT,
    d INT,
    ek INT,
    ed INT,
    roundswing FLOAT,
    adr FLOAT,
    eadr FLOAT,
    ekast FLOAT,
    rating FLOAT,
    PRIMARY KEY (matchid,playerid ,teamid, mapid,sideid)
);