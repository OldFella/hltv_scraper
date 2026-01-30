from concurrent.futures import ProcessPoolExecutor

from scraper.match_scraper import match_scraper
import pandas as pd
import os
import time
import gc
import argparse

def multiprocessing(func, workers, args):
    res = []
    with ProcessPoolExecutor(workers) as ex:
        for i in range(workers):
            res.append(ex.submit(func, args))
            time.sleep(0.1)

    return res


def match_scraping(path):
    m_todo = pd.read_csv(f'{path}matches_todo.csv')
    row = m_todo.loc[0]
    m_todo.loc[1:].to_csv(f'{path}matches_todo.csv', index=False)
    ms = match_scraper()
    data = ms.open_match(row)
    ms.get_stats(data,row)
    return ms.player_stats, ms.players, ms.match

def load_matches(f_matches):
    return pd.read_csv(f_matches)

def get_matches_in_db(matches):
    if os.path.exists(matches):
        df = pd.read_csv(matches)
        return df['matchid'].unique()
    return [0]

def remove_forfeit(df):
    df_copy = df.copy()
    df_copy['sum'] = df_copy['score1'] + df_copy['score2']
    return df[df_copy['sum'] != 1]

def main(n_workers, f_matches = 'data/matches/matches.csv', result_path = 'data/database/'):

    matches = load_matches(f_matches)
    m_todo = matches
    ids_in_db = get_matches_in_db(f'{result_path}/matches.csv')
    m_todo = remove_forfeit(m_todo)
    m_todo = m_todo[~m_todo['matchID'].isin(ids_in_db)]

    m_todo.to_csv(f'{result_path}matches_todo.csv',index=False)
    if len(m_todo) == 0:
        return False
    if not os.path.exists(f'{result_path}/matches.csv'):
        db_matches = pd.DataFrame()
    else:
        db_matches = pd.read_csv(f'{result_path}/matches.csv')
    
    if not os.path.exists(f'{result_path}player_stats.csv'):
        db_player_stats = pd.DataFrame()
    else:
        db_player_stats = pd.read_csv(f'{result_path}player_stats.csv')

    
    if not os.path.exists(f'{result_path}players.csv'):
        db_players = pd.DataFrame()
    else:
        db_players = pd.read_csv(f'{result_path}players.csv')

    # MAX_ITER = 20
    it = 0
    while len(m_todo) > 0:
        m_todo = pd.read_csv(f'{result_path}matches_todo.csv')

        print(f'{len(m_todo)} still to go...',end = '\r')
        mp_results = []
        if n_workers == 1:
            mp_results.append(match_scraping(result_path))
        else:
            mp_results = multiprocessing(match_scraping, n_workers, result_path)
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
            db_player_stats.to_csv(f'{result_path}player_stats.csv',index=False)

            if db_players.empty:
                db_players = players
            else:
                db_players = pd.concat([db_players, players])
                db_players = db_players.drop_duplicates()
            db_players.to_csv(f'{result_path}players.csv',index=False)
            
            if db_matches.empty:
                db_matches = matches
            else:
                db_matches = pd.concat([db_matches, matches])
            db_matches.to_csv(f'{result_path}matches.csv',index=False)

            # backup every 100 websites
            if it % 100 == 99:
                
                db_player_stats.to_csv(f'{result_path}backup/player_stats{it}.csv',index=False)
                db_players.to_csv(f'{result_path}backup/players{it}.csv',index=False)
                db_matches.to_csv(f'{result_path}backup/matches{it}.csv',index=False)
        c = gc.collect()


        it += 1
    return True

        
        
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--matches', type = str, default = './data/matches/')
    parser.add_argument('--result', type = str, default = 'data/database/')

    args = parser.parse_args()
    results = main(n_workers=4, f_matches=args.matches, result_path=args.result)

    
