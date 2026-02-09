select * from ( select  p.playerid,
                        ROUND(cast(avg(ps.rating) as numeric),3) as avg_rating,
                        count(ps.rating) as n_games
                from player_stats ps 
                join teams t
                    on ps.teamid = t.teamid
                full join players p
                    on ps.playerid = p.playerid
                join (select distinct matchid,teamid from matches) as m
                    on  ps.matchid = m.matchid 
                        and m.teamid != ps.teamid
                join match_overview mo
                    on mo.matchid = ps.matchid
                join (select m.matchid, m.teamid, m.mapid, case when m.score > m2.score then 1 else 0 end as win
                            from matches m 
                            join matches m2
                                on m.matchid = m2.matchid and m.teamid != m2.teamid
                            join teams t1
                                on m.teamid = t1.teamid
                            join match_overview mo
                                on m.matchid = mo.matchid
                            join teams t2
                                on m2.teamid = t2.teamid
                            where   t1.teamid != t2.teamid 
                                    and m.sideid = m2.sideid 
                                    and m.mapid = m2.mapid 
                                    and m.sideid = 0 
                                    and m.mapid = {{mapid}} 
                                    and mo.date between CAST('{{start_date}}' as date) 
                                                        - INTERVAL '{{months}} months'
                                    and CAST('{{start_date}}' as date)) as w
                    on w.matchid = ps.matchid and w.teamid = ps.teamid
                where p.name in (select distinct pl.name 
                                from player_stats pn
                                join players pl 
                                on pn.playerid = pl.playerid
                                where pl.playerid in (select playerid from fantasies where fantasyid = {{fantasyid}}))
                    and ps.mapid = 0 
                    and ps.sideid = 0
                    and w.win = {{win}}
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
