select  m.matchid,
        m.mapid,
        m.sideid,
        t1.name as team,
        m.score, 
        t2.name as opponent, 
        m2.score score_opponent, 
        mo.date,
        mo.event
from matches m 
join matches m2
    on m.matchid = m2.matchid and m.teamid != m2.teamid
join teams t1
    on m.teamid = t1.teamid
join teams t2
    on m2.teamid = t2.teamid
join match_overview mo
    on m.matchid = mo.matchid
where t1.name = '{{team}}' 
        and m.sideid = m2.sideid
        and m.mapid = m2.mapid 
        and m.sideid = {{sideid}} 
        and m.mapid = {{mapid}}
        and mo.date between CAST('{{start_date}}' as date)  - INTERVAL '{{months}} months'
                   and CAST('{{start_date}}' as date)
order by date
desc
;