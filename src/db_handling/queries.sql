-- get the match history of team Spirit
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

select m.matchid, t1.name, m.score, t2.name as op, m2.score score_op, m.date, case when m.score > m2.score then 1 else 0 end as win
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


-- get winrate of team Spirit in the last 3 months
select sum(w.win), count(w.win), 100 * cast(sum(w.win) as float)/ cast(count(w.win) as float) as win_prct
    From (select case when m.score > m2.score then 1 else 0 end as win
            from matches m 
            join matches m2
            on m.matchid = m2.matchid and m.teamid != m2.teamid
            join teams t1
            on m.teamid = t1.teamid
            join teams t2
            on m2.teamid = t2.teamid
            where t1.name = 'Spirit' and m.sideid = m2.sideid and m.mapid = m2.mapid and m.sideid = 0 and m.mapid = 0 and m.date >=  CURRENT_DATE - INTERVAL '3 months') as w
    ;

-- get winrate of team Spirit in the last 3 months for each map
select ma.name as map,sum(w.win) as n_wins, count(w.win) as n_games, 100 * cast(sum(w.win) as float)/ cast(count(w.win) as float) as win_prct
    From (select m.mapid, case when m.score > m2.score then 1 else 0 end as win
            from matches m 
            join matches m2
            on m.matchid = m2.matchid and m.teamid != m2.teamid
            join teams t1
            on m.teamid = t1.teamid
            join teams t2
            on m2.teamid = t2.teamid
            where t1.name = 'Spirit' and m.sideid = m2.sideid and m.mapid = m2.mapid and m.sideid = 0 and m.mapid != 0 and m.date >=  CURRENT_DATE - INTERVAL '3 months') as w
    join maps ma 
    on ma.mapid = w.mapid
    group by ma.name
    ;


-- get average rating of player zweih for all teams he played in
select p.name, t.name, avg(ps.rating) as avg_rating, count(ps.rating) as n_games
    from player_stats ps 
    join teams t
    on ps.teamid = t.teamid
    join players p
    on ps.playerid = p.playerid
    where p.name = 'zweih' and ps.sideid = 0 and ps.mapid = 0
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

-- get average rating per map for all players in PARIVISION
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


-- get average rating per side played on all maps for players in the fantasy 591
select * from (select p.name as player, s.name as side, avg(ps.rating) as avg_rating,count(ps.rating) as n_maps
    from player_stats ps 
    join teams t
    on ps.teamid = t.teamid
    full join players p
    on ps.playerid = p.playerid
    join (select distinct matchid, date from matches) m
    on ps.matchid = m.matchid
    join sides s
    on ps.sideid = s.sideid
    where (p.name in (select distinct pl.name 
                     from player_stats pn
                     join players pl 
                     on pn.playerid = pl.playerid
                     where pl.playerid in (select playerid from fantasies where fantasyid = 591))
        and ps.mapid != 0 and m.date >=  CURRENT_DATE - INTERVAL '3 months')
    group by p.name, s.name) as stat
union all
select p.name as player, s.name as side,Null as avg_rating,0 as n_maps
    from fantasies f
    join players p
    on p.playerid = f.playerid
    cross join sides s
    where f.playerid not in (select playerid
                                    from player_stats)
        and f.fantasyid = 591
order by player
    ;

-- get average rating per game for all players in the fantasy 591
select * from (select p.name as player, ROUND(cast(avg(ps.rating) as numeric),3) as avg_rating,count(ps.rating) as n_games
    from player_stats ps 
    join teams t
    on ps.teamid = t.teamid
    full join players p
    on ps.playerid = p.playerid
    join (select distinct matchid, date from matches) m
    on ps.matchid = m.matchid
    where p.name in (select distinct pl.name 
                     from player_stats pn
                     join players pl 
                     on pn.playerid = pl.playerid
                     where pl.playerid in (select playerid from fantasies where fantasyid = 591))
        and ps.mapid = 0 and m.date >=  CURRENT_DATE - INTERVAL '3 months'
        and ps.sideid = 0
    group by p.name) as stat
union all
select p.name as player,Null as avg_rating,0 as n_maps
    from fantasies f
    join players p
    on p.playerid = f.playerid
    where f.playerid not in (select playerid
                                    from player_stats)
        and f.fantasyid = 591
order by player
;