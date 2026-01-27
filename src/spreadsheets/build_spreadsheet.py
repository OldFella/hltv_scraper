import sys
sys.path.append('../')
import pandas as pd

from tools.helpers import rating_to_points
from db_handling.db_handler import db_reader
import argparse
import os


def dfs_tabs(df_list, sheet_list, file_name):
    writer = pd.ExcelWriter(file_name)   
    for dataframe, sheet in zip(df_list, sheet_list):
        dataframe.to_excel(writer, sheet_name=sheet, startrow=0 , startcol=0, index = False)   
    writer.close()


def get_h2h(teams, fantasy,fantasyid,dbr):
    player_h2h = fantasy[['playerid']]
    team_h2h = pd.DataFrame(columns = teams, index=teams)
    for t in teams:
        for op in teams:
            winrate_h2h = dbr.get_winrate_h2h(t,op,0)
            if not winrate_h2h['win_prct'].empty:
                winrate = winrate_h2h['win_prct'].item()
                n_games = winrate_h2h['n_games'].item()
                team_h2h.loc[t, op] = f"{winrate} ({n_games})"


        t_name = dbr.get_name('teams', 'teamid', t)
        rating_vs_team = dbr.get_average_ratings_fantasy_vs(fantasyid, vs = t)
        rating_vs_team = rating_vs_team.rename(columns={'n_games': f'n_games_vs_{t_name}',
                                            'avg_rating':f'{t_name}'})
        player_h2h = player_h2h.join(rating_vs_team[['playerid',f'{t_name}']].set_index('playerid'), on = 'playerid')

    return player_h2h, team_h2h
    
def join_on(df, dfs, on):
    for d in dfs:
        df = df.join(d.set_index(on), on = on)
    return df

def add_metrics(spreadsheet):
    spreadsheet['avg_rating'] = spreadsheet['avg_rating'].astype('float')
    spreadsheet['avg_rating_event'] = spreadsheet['avg_rating_event'].astype('float')

    spreadsheet['rating/cost'] = 200 * spreadsheet['avg_rating']/spreadsheet['cost']
    spreadsheet['rating/cost'] = spreadsheet['rating/cost'].round(3)
    spreadsheet['avg_points'] = spreadsheet['avg_rating'].apply(lambda x: rating_to_points(x))

    spreadsheet['avg_points_event'] = spreadsheet['avg_rating_event'].apply(lambda x: rating_to_points(x))
    spreadsheet['avg_points/$'] = spreadsheet['avg_points']/spreadsheet['cost']
    spreadsheet['avg_points/$_event'] = spreadsheet['avg_points_event']/spreadsheet['cost']
    return spreadsheet
    

def main(fantasyid, output):

    dbr = db_reader(filename='../db_handling/database.ini', query_dir = '../db_handling/queries/')
    fantasy = dbr.get_table('fantasies')
    fantasy = fantasy[fantasy['fantasyid'] == fantasyid]
    ratings = dbr.get_average_ratings_fantasy(fantasyid)
    fantasy_teams = fantasy['teamid'].drop_duplicates()

    player_h2h, team_h2h = get_h2h(fantasy_teams, fantasy, fantasyid, dbr)
    
    ratings_event = dbr.get_average_ratings_fantasy_event(fantasyid)
    ratings_event = ratings_event.rename(columns={'n_games': f'n_games_event',
                                            'avg_rating':f'avg_rating_event'})
    
    players = dbr.get_table('players')
    players = players.rename(columns = {'name':'player'})
    teams = dbr.get_table('teams')
    teams = teams.rename(columns={'name':'team'})
    players['playerid'] = players['playerid'].astype('int')
    teams['teamid'] = teams['teamid'].astype('int')


    fantasy = fantasy.join(players.set_index('playerid'), on='playerid')
    fantasy = fantasy.join(teams.set_index('teamid'), on ='teamid')


    team_names = fantasy[['teamid', 'team']]
    team_names = pd.Series(team_names.team.values,index=team_names.teamid).to_dict()
    team_h2h = team_h2h.rename(columns = team_names)
    team_h2h = team_h2h.rename(index = team_names).reset_index()
    team_h2h = team_h2h.rename(columns={'teamid' : 'Team \ Opponent'})

    cols = list(fantasy)
    cols[3], cols[-1] = cols[-1], cols[3]
    fantasy = fantasy.reindex(columns = cols)
    spreadsheet = fantasy.join(ratings.set_index('playerid'), on='playerid')

    spreadsheet = join_on(fantasy, [ratings, ratings_event], on='playerid')
    player_h2h = spreadsheet.join(player_h2h.set_index('playerid'), on='playerid')

    
    spreadsheet = add_metrics(spreadsheet)

    sheets = [spreadsheet, team_h2h, player_h2h]
    sheet_names = ['main', 'h2h_teams', 'h2h_players']    

    fantasy_name = dbr.get_name('fantasy_overview', 'fantasyid', fantasyid)
    dir = f'{fantasy_name}/'

    os.mkdir(dir)
    dfs_tabs(sheets, sheet_names, f'{dir}{output}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--fantasyid','-f', type = int, default = 591)
    parser.add_argument('--output', '-o', type =str, default = 'out.ods')
    args = parser.parse_args()
    main(args.fantasyid, args.output)