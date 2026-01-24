select m.matchid, t1.name, m.score, t2.name, m2.score, m.date
    from matches m 
    join matches m2
    on m.matchid = m2.matchid and m.teamid != m2.teamid
    join teams t1
    on m.teamid = t1.teamid
    join teams t2
    on m2.teamid = t2.teamid
    where t1.name = 'Spirit' and m.sideid = m2.sideid and m.mapid = m2.mapid and m.sideid = 0 and m.mapid = 0
    ;