from db_handling.db_handler import db_writer
import pandas as pd
import numpy as np
import os
import shutil
from datetime import datetime

from scraper.result_scraper import result_scraper
import scripts.scrape_matches as sm
from scraper.team_scraper import team_scraper
import argparse

def get_results(page = 0,top = 100, dir = '', teams_path = ''):
    rs = result_scraper(page = page, top = top, dir = dir, teams_path= teams_path)
    return rs

def get_mids(dbw):
    return dbw.get_matchids()

def get_matches(dbw, dir):
    matches = pd.read_csv(f'{dir}/matches.csv')
    mids = dbw.get_matchids()
    matches = matches[~matches['matchID'].isin(mids)]
    return matches
    

def random_N_digits(n):
    start = 10 **(n-1)
    end = (10**n) -1
    return np.random.randint(start,end)

def rearrange_data(dbw, dir):
    db_sides = dbw.get_table('sides')
    db_sides = db_sides.rename(columns = {'name':'side'})
    db_maps = dbw.get_table('maps')
    db_maps = db_maps.rename(columns = {'name':'map'})

    db_teams = dbw.get_table('teams')
    db_teams = db_teams.rename(columns = {'name':'team'})

    player_stats = pd.read_csv(f'{dir}player_stats.csv')
    player_stats = player_stats.rename(str.lower, axis='columns')

    matches = pd.read_csv(f'{dir}matches.csv')
    matches = matches.rename(str.lower, axis='columns')


    for df_ids in [db_sides, db_maps, db_teams]:
        on = df_ids.columns[-1]
        player_stats = rearrange_col(player_stats, df_ids, on = on)
        matches = rearrange_col(matches, df_ids, on=on)
    
    player_stats.to_csv(f'{dir}player_stats.csv', index = False)

    matches.to_csv(f'{dir}matches.csv', index = False)



def rearrange_col(df,df_ids, on):
    df = df.join(df_ids.set_index(on), on = on)
    df = df.dropna()
    df.drop(columns = [on], inplace = True)
    return df


def remove_duplicates(file, dir, dbw, table):
    df = pd.read_csv(f'{dir}{file}')
    ids = df.columns
    ids = [id for id in ids if 'id' in id.lower()]
    table_id = [id for id in ids if table.replace('s', '') in id][0]
    db_ids = dbw.get_ids(table, table_id.lower())
    df = df[~df[table_id].isin(db_ids)]
    return df


def make_dirs(dir):
    tmp_id = datetime.today().strftime('%Y-%m-%d')

    tmp_folder = 'tmp_' + str(tmp_id)
    tmp_folder = "".join([dir, tmp_folder])
    
    # Create folder structure
    if not os.path.exists(tmp_folder):
        os.mkdir(tmp_folder)

    teams_ranking = f"{tmp_folder}/team_rankings/"
    if not os.path.exists(teams_ranking):
            os.mkdir(teams_ranking)
    
    data_folder = tmp_folder + '/data/'
    if not os.path.exists(data_folder):
        os.mkdir(data_folder)
    
    f_matches = f'{tmp_folder}/matches.csv'
    
    return tmp_folder, teams_ranking, data_folder, f_matches

def scrape_teams(teams_ranking, data_folder):
    ts = team_scraper(dir = teams_ranking) 
    teams = ts.teams
    teams.drop(columns = ['points'] ,inplace= True)
    teams.to_csv(f'{data_folder}teams.csv',index = False)

def scrape_results(dbw, tmp_folder, teams_ranking,f_matches ,max_pages):
    for page in range(max_pages):
        rs = get_results(page = page, dir = tmp_folder + '/', teams_path=teams_ranking)
        matches = get_matches(dbw, tmp_folder)
    
    matches.to_csv(f_matches, index = False)

    return matches

def get_match_overview(matches,data_folder):
    dates = pd.read_csv(f'{data_folder}matches.csv')
    events = matches[['matchID', 'event']]
    match_overview = dates[['matchID', 'date']].join(events.set_index('matchID'), on='matchID')
    dates = dates.drop(columns=['date']).to_csv(f'{data_folder}matches.csv', index=False)
    match_overview = match_overview[['matchID', 'event', 'date']].drop_duplicates()
    match_overview.to_csv(f'{data_folder}match_overview.csv', index=False)



def scrape_matches(matches, f_matches,data_folder, dbw, n_workers, tmp_folder):
    n_workers = min(n_workers, len(matches))
    new_data_flag = sm.main(n_workers = n_workers,f_matches = f_matches, result_path = data_folder)
    if new_data_flag:
        get_match_overview(matches, data_folder)

        rearrange_data(dbw, data_folder)

        tables = ['match_overview','players', 'teams','player_stats', 'matches']

        for table in tables:
            if table not in ['player_stats', 'matches', 'match_overview']:
                df = remove_duplicates(f'{table}.csv', data_folder, dbw,table)
            else:
                df = pd.read_csv(f'{data_folder}{table}.csv')
            
            df = df.rename(str.lower, axis ='columns')

            if not df.empty:
                df = df.drop_duplicates()
                dbw.insert(df, table)

def main(n_workers, dir, config, max_pages = 1):

    print('create folder structure...')
    tmp_folder, teams_ranking, data_folder, f_matches = make_dirs(dir)

    dbw = db_writer(filename=config)

    print('get teams...')
    scrape_teams(teams_ranking, data_folder)

    print('get results...')
    matches = scrape_results(dbw, tmp_folder, teams_ranking, f_matches, max_pages)

    if len(matches) == 0:
        print('No new matches available!')
        return
    
    print('get matches...')
    scrape_matches(matches, f_matches, data_folder, dbw, n_workers, tmp_folder)


    print('remove folder structure...')
    shutil.rmtree(tmp_folder)

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--n_workers','-n', type = int, default = 4)
    parser.add_argument('--dir', '-d', type = str, default = 'data/temp/')
    parser.add_argument('--config', '-c', type=str, default = 'database.ini')
    parser.add_argument('--max_pages','-max', type = int, default = 1)

    args = parser.parse_args()

    print('start...')
    
    main(n_workers = args.n_workers, dir = args.dir, config = args.config, max_pages=args.max_pages)


