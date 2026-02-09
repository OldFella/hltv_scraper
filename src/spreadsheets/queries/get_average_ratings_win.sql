select p.name, avg(ps.rating) as avg_rating, count(ps.rating) as n_games
    from player_stats ps 
    join teams t
        on ps.teamid = t.teamid
    join players p
        on ps.playerid = p.playerid
    join (select distinct matchid from matches) m
        on m.matchid=ps.matchid
    join match_overview mo
        on ps.matchid = mo.matchid
    join (select m.matchid, m.mapid, case when m.score > m2.score then 1 else 0 end as win
                from matches m 
                join matches m2
                    on m.matchid = m2.matchid and m.teamid != m2.teamid
                join teams t1
                    on m.teamid = t1.teamid
                join match_overview mo
                    on m.matchid = mo.matchid
                join teams t2
                    on m2.teamid = t2.teamid
                where   t1.teamid = {{teamid}} 
                        and m.sideid = m2.sideid 
                        and m.mapid = m2.mapid 
                        and m.sideid = 0 
                        and m.mapid = {{mapid}} 
                        and mo.date between CAST('{{start_date}}' as date) 
                                            - INTERVAL '{{months}} months'
                        and CAST('{{start_date}}' as date)) as w
        on w.matchid = ps.matchid
    where   p.playerid = {{playerid}} 
            and ps.sideid = {{sideid}}
            and w.win = {{win}} 
            and ps.mapid = {{mapid}}
            and mo.date  between CAST('{{start_date}}' as date) - INTERVAL '{{months}} months'
                        and CAST('{{start_date}}' as date)
    group by p.name
    ;
