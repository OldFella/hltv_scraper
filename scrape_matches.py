from concurrent.futures import ProcessPoolExecutor

from tools.scraper import match_scraper
import pandas as pd
import os
import time

def multiprocessing(func, workers):
    res = []
    with ProcessPoolExecutor(workers) as ex:
        for i in range(workers):
            res.append(ex.submit(func))
            time.sleep(0.1)

    return res


def match_scraping():
    m_todo = pd.read_csv('data/matches/matches_todo.csv')
    row = m_todo.loc[1]
    m_todo.loc[1:].to_csv('data/matches/matches_todo.csv', index=False)
    ms = match_scraper()
    data = ms.open_match(row)
    ms.get_stats(data,row)
    return ms.player_stats, ms.players, ms.match

def load_matches():
    return pd.read_csv('data/matches/matches.csv')

def get_matches_in_db():
    if os.path.exists('data/database/matches.csv'):
        df = pd.read_csv('data/database/matches.csv')
        return df['matchID'].unique()
    return [0]

def main(n_workers):
    # check if matches_todo.csv exists
    # if not os.path.exists('data/matches/matches_todo.csv'):
    matches = load_matches()
    m_todo = matches
    ids_in_db = get_matches_in_db()
    m_todo = m_todo[~m_todo['matchID'].isin(ids_in_db)]
    m_todo.to_csv('data/matches/matches_todo.csv',index=False)

    # else:
    #     m_todo = pd.read_csv('data/matches/matches_todo.csv')
    
    if not os.path.exists('data/database/matches.csv'):
        db_matches = pd.DataFrame()
    else:
        db_matches = pd.read_csv('data/database/matches.csv')
    
    if not os.path.exists('data/database/player_stats.csv'):
        db_player_stats = pd.DataFrame()
    else:
        db_player_stats = pd.read_csv('data/database/player_stats.csv')

    
    if not os.path.exists('data/database/players.csv'):
        db_players = pd.DataFrame()
    else:
        db_players = pd.read_csv('data/database/players.csv')

    MAX_ITER = 20
    it = 0
    while len(m_todo) > 0 and it < MAX_ITER:
        it += 1
        m_todo = pd.read_csv('data/matches/matches_todo.csv')

        print(f'{len(m_todo)} still to go...')
        mp_results = multiprocessing(match_scraping, n_workers)
        results = []
        for res in mp_results:
            try:
                results.append(res.result())
            except Exception as e:
                print(e)

        for dfs in results:
            player_stats, players, matches = dfs

            if db_player_stats.empty:
                db_player_stats = player_stats
            else:
                db_player_stats = pd.concat([db_player_stats, player_stats])
                db_player_stats.to_csv('data/database/player_stats.csv',index=False)

            if db_players.empty:
                db_players = players
            else:
                db_players = pd.concat([db_players, players])
                db_players.to_csv('data/database/players.csv',index=False)
            
            if db_matches.empty:
                db_matches = matches
            else:
                db_matches = pd.concat([db_matches, matches])
                db_matches.to_csv('data/database/matches.csv',index=False)
        
        
        
    


if __name__ == '__main__':
    results = main(n_workers=4)

    
