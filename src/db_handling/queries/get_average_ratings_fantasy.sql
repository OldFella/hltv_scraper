select * from ( select  p.playerid,
                        ROUND(cast(avg(ps.rating) as numeric),3) as avg_rating,
                        count(ps.rating) as n_games
                from player_stats ps 
                join teams t
                on ps.teamid = t.teamid
                join match_overview mo
                on mo.matchid = m.matchid
                full join players p
                on ps.playerid = p.playerid
                join (select distinct matchid,teamid, date from matches) m
                on ps.matchid = m.matchid and m.teamid != ps.teamid
                where p.name in (select distinct pl.name 
                                from player_stats pn
                                join players pl 
                                on pn.playerid = pl.playerid
                                where pl.playerid in (select playerid from fantasies where fantasyid = {{fantasyid}}))
                    and ps.mapid = 0 
                    and ps.sideid = 0
                    and mo.date  between CAST('{{start_date}}' as date) - INTERVAL '{{months}} months'
                                and CAST('{{start_date}}' as date)
                group by p.playerid) as stat
union all
select  p.playerid,
        Null as avg_rating,
        0 as n_games
    from fantasies f
    join players p
    on p.playerid = f.playerid
    where f.playerid not in (select playerid
                                    from player_stats)
        and f.fantasyid = {{fantasyid}}
;