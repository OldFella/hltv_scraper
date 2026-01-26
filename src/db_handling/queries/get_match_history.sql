select  m.matchid,
        m.mapid,
        m.sideid,
        t1.name as team,
        m.score, 
        t2.name as opponent, 
        m2.score score_opponent, 
        m.date
from matches m 
join matches m2
    on m.matchid = m2.matchid and m.teamid != m2.teamid
join teams t1
    on m.teamid = t1.teamid
join teams t2
    on m2.teamid = t2.teamid
where t1.name = '{{team}}' 
        and m.sideid = m2.sideid
        and m.mapid = m2.mapid 
        and m.sideid = {{sideid}} 
        and m.mapid = {{mapid}}
        and m.date between CAST('{{start_date}}' as date)  - INTERVAL '{{months}} months'
                   and CAST('{{start_date}}' as date)
order by date
desc
;