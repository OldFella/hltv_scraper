select p.name, avg(ps.rating) as avg_rating, count(ps.rating) as n_games
    from player_stats ps 
    join teams t
        on ps.teamid = t.teamid
    join players p
        on ps.playerid = p.playerid
    join (select distinct matchid, date from matches) m
        on m.matchid=ps.matchid
    join match_overview mo
        on m.matchid = mo.matchid
    where   p.playerid = {{playerid}} 
            and ps.sideid = {{sideid}} 
            and ps.mapid = {{mapid}}
            and mo.date  between CAST('{{start_date}}' as date) - INTERVAL '{{months}} months'
                        and CAST('{{start_date}}' as date)
    group by p.name
    ;