import sys
sys.path.append('../')
import pandas as pd

from tools.helpers import rating_to_points
from db_handling.db_handler import db_reader


def dfs_tabs(df_list, sheet_list, file_name):
    writer = pd.ExcelWriter(file_name)   
    for dataframe, sheet in zip(df_list, sheet_list):
        dataframe.to_excel(writer, sheet_name=sheet, startrow=0 , startcol=0, index = False)   
    writer.close()

def main(fantasyid):
    dbr = db_reader(filename='../db_handling/database.ini', query_dir = '../db_handling/queries/')
    fantasy = dbr.get_table('fantasies')
    fantasy = fantasy[fantasy['fantasyid'] == fantasyid]
    ratings = dbr.get_average_ratings_fantasy(fantasyid)
    fantasy_teams = fantasy['teamid'].drop_duplicates()
    ratings_vs = fantasy[['playerid']]
    h2h_matrix = pd.DataFrame(columns = fantasy_teams, index=fantasy_teams)
    for t in fantasy_teams:
        for op in fantasy_teams:
            winrate_h2h = dbr.get_winrate_h2h(t,op,0)
            # print(t, op)

            if not winrate_h2h['win_prct'].empty:
                
                winrate = winrate_h2h['win_prct'].item()
                n_games = winrate_h2h['n_games'].item()

                h2h_matrix.loc[t, op] = f"{winrate} ({n_games})"
            # print(winrate_h2h)
        t_name = dbr.get_name('teams', 'teamid', t)
        rating_vs_team = dbr.get_average_ratings_fantasy_vs(fantasyid, vs = t)
        rating_vs_team = rating_vs_team.rename(columns={'n_games': f'n_games_vs_{t_name}',
                                            'avg_rating':f'{t_name}'})
        ratings_vs = ratings_vs.join(rating_vs_team[['playerid',f'{t_name}']].set_index('playerid'), on = 'playerid')

    ratings_event = dbr.get_average_ratings_fantasy_event(fantasyid)
    ratings_event = ratings_event.rename(columns={'n_games': f'n_games_event',
                                            'avg_rating':f'avg_rating_event'})
    # ratings_event['avg_rating_event'] = ratings_vs[cols[1:]].mean(axis = 1)
    # print(ratings_event)
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

    h2h_matrix = h2h_matrix.rename(columns = team_names)
    h2h_matrix = h2h_matrix.rename(index = team_names).reset_index()
    h2h_matrix = h2h_matrix.rename(columns={'teamid' : 'Team \ Opponent'})

    # h2h_matrix.to_csv('teams_h2h.csv')
    print(h2h_matrix)

    cols = list(fantasy)
    cols[3], cols[-1] = cols[-1], cols[3]
    fantasy = fantasy.reindex(columns = cols)
    spreadsheet = fantasy.join(ratings.set_index('playerid'), on='playerid')


    player_h2h = spreadsheet.join(ratings_vs.set_index('playerid'), on='playerid')
    # player_h2h.to_csv('player_h2h.csv', index = False)
    # spreadsheet = spreadsheet.join(ratings_vs.set_index('playerid'), on='playerid')
    spreadsheet = spreadsheet.join(ratings_event.set_index('playerid'), on='playerid')

    spreadsheet['avg_rating'] = spreadsheet['avg_rating'].astype('float')
    spreadsheet['avg_rating_event'] = spreadsheet['avg_rating_event'].astype('float')

    spreadsheet['rating/cost'] = 200 * spreadsheet['avg_rating']/spreadsheet['cost']
    spreadsheet['rating/cost'] = spreadsheet['rating/cost'].round(3)
    spreadsheet['avg_points'] = spreadsheet['avg_rating'].apply(lambda x: rating_to_points(x))

    spreadsheet['avg_points_event'] = spreadsheet['avg_rating_event'].apply(lambda x: rating_to_points(x))
    spreadsheet['avg_points/$'] = spreadsheet['avg_points']/spreadsheet['cost']
    spreadsheet['avg_points/$_event'] = spreadsheet['avg_points_event']/spreadsheet['cost']


    # spreadsheet['rating/cost_event'] = 200 * spreadsheet['avg_rating_event']/spreadsheet['cost']
    # spreadsheet['rating/cost_event'] = spreadsheet['rating/cost_event'].astype('float').round(3)
    sheets = [spreadsheet, h2h_matrix, player_h2h]
    sheet_names = ['main', 'h2h_teams', 'h2h_players']    

    dfs_tabs(sheets, sheet_names, 'out.ods')
    # spreadsheet.to_csv('spreadsheet.csv', index = False)
    print(spreadsheet)


if __name__ == '__main__':
    main(591)