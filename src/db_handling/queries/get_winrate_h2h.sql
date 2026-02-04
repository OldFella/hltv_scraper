select  ma.name as map,
        sum(w.win) as n_wins, 
        count(w.win) as n_games, 
        100 * cast(sum(w.win) as float)/ cast(count(w.win) as float) as win_prct
        From (select m.mapid, case when m.score > m2.score then 1 else 0 end as win
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
                        and t2.teamid = {{opponentid}}
                        and m.sideid = m2.sideid 
                        and m.mapid = m2.mapid 
                        and m.sideid = 0 
                        and m.mapid = {{mapid}} 
                        and mo.date between CAST('{{start_date}}' as date) 
                                            - INTERVAL '{{months}} months'
                        and CAST('{{start_date}}' as date)) as w
        join maps ma 
        on ma.mapid = w.mapid
        group by ma.name
        ;