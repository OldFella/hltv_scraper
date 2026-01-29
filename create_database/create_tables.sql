CREATE TABLE players (
    playerid INT PRIMARY KEY,
    name varchar(255)
);

CREATE TABLE teams (
    teamid INT PRIMARY KEY,
    name varchar(255)
);

CREATE TABLE maps (
    mapid INT PRIMARY KEY,
    name varchar(255)
);

CREATE TABLE sides (
    sideid INT PRIMARY KEY,
    name varchar(255)
);

CREATE TABLE matches (
    matchid INT,
    teamid INT REFERENCES teams (teamid),
    mapid INT REFERENCES maps (mapid),
    sideid INT REFERENCES sides (sideid),
    score INT,
    date date,
    PRIMARY KEY (matchid, teamid, mapid,sideid)
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
    PRIMARY KEY (matchid,playerid ,teamid, mapid,sideid)
);


CREATE TABLE fantasy_overview(
    fantasyid INT PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE fantasies (
    fantasyid INT REFERENCES fantasy_overview (fantasyid),
    teamid INT REFERENCES teams(teamid),
    playerid INT REFERENCES players (playerid),
    cost INT,
    PRIMARY KEY (fantasyid, teamid, playerid)
);

