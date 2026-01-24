select m.matchid, t1.name, m.score, t2.name as op, m2.score score_op, m.date
    from matches m 
    join matches m2
    on m.matchid = m2.matchid and m.teamid != m2.teamid
    join teams t1
    on m.teamid = t1.teamid
    join teams t2
    on m2.teamid = t2.teamid
    where t1.name = 'Spirit' and m.sideid = m2.sideid and m.mapid = m2.mapid and m.sideid = 0 and m.mapid = 0
    order by date
    desc
    ;


select p.name, t.name, avg(ps.rating) as avg_rating, count(ps.rating) as n_games
    from player_stats ps 
    join teams t
    on ps.teamid = t.teamid
    join players p
    on ps.playerid = p.playerid
    where p.name = 'zweih' and ps.sideid = 0 and ps.mapid != 0
    group by p.name, t.name
    ;

select p.name, ps.sideid, avg(ps.rating) as avg_rating, count(ps.rating) as n_games
    from player_stats ps 
    join teams t
    on ps.teamid = t.teamid
    join players p
    on ps.playerid = p.playerid
    join (select distinct matchid, date from matches) m
    on ps.matchid = m.matchid
    where p.name = 'zweih' and ps.mapid != 0 and m.date >=  CURRENT_DATE - INTERVAL '3 months'
    group by p.name, ps.sideid
    ;

select p.name, t.name, avg(ps.rating) as avg_rating
    from player_stats ps 
    join teams t
    on ps.teamid = t.teamid
    join players p
    on ps.playerid = p.playerid
    join matches m
    on ps.matchid = m.matchid
    where t.name = 'PARIVISION' and ps.sideid = 0 and ps.mapid = 0 and m.date >=  CURRENT_DATE - INTERVAL '3 months'
    group by p.name, t.name
    ;

select p.name as player, t.name as team, s.name as side, avg(ps.rating) as avg_rating
    from player_stats ps 
    join teams t
    on ps.teamid = t.teamid
    join players p
    on ps.playerid = p.playerid
    join (select distinct matchid, date from matches) m
    on ps.matchid = m.matchid
    join sides s
    on ps.sideid = s.sideid
    where t.name = 'B8' and ps.mapid != 0 and m.date >=  CURRENT_DATE - INTERVAL '3 months'
    group by p.name, t.name, s.name
    order by p.name
    ;


select p.name as player, s.name as side, avg(ps.rating) as avg_rating,count(ps.rating) as n_maps
    from player_stats ps 
    join teams t
    on ps.teamid = t.teamid
    join players p
    on ps.playerid = p.playerid
    join (select distinct matchid, date from matches) m
    on ps.matchid = m.matchid
    join sides s
    on ps.sideid = s.sideid
    where p.name in (select distinct pl.name 
                     from player_stats pn
                     join teams te 
                     on pn.teamid = te.teamid 
                     join players pl 
                     on pn.playerid = pl.playerid
                     where te.name = 'PARIVISION')
        and ps.mapid != 0 and m.date >=  CURRENT_DATE - INTERVAL '3 months'
    group by p.name, s.name
    order by p.name
    ;

