import sys
sys.path.append('../')
import pandas as pd

from db_handling.db_handler import db_reader

def main(fantasyid):
    dbr = db_reader(filename='../db_handling/database.ini', query_dir = '../db_handling/queries/')
    fantasy = dbr.get_table('fantasies')
    fantasy = fantasy[fantasy['fantasyid'] == fantasyid]
    ratings = dbr.get_average_ratings_fantasy(fantasyid)
    fantasy_teams = fantasy['teamid'].drop_duplicates()
    ratings_vs = fantasy[['playerid']]
    for t in fantasy_teams:
        t_name = dbr.get_name('teams', 'teamid', t)
        rating_vs_team = dbr.get_average_ratings_fantasy_vs(fantasyid, vs = t)
        rating_vs_team = rating_vs_team.rename(columns={'n_games': f'n_games_vs_{t_name}',
                                            'avg_rating':f'avg_rating_vs_{t_name}'})
        ratings_vs = ratings_vs.join(rating_vs_team[['playerid',f'avg_rating_vs_{t_name}']].set_index('playerid'), on = 'playerid')

    players = dbr.get_table('players')
    players = players.rename(columns = {'name':'player'})
    teams = dbr.get_table('teams')
    teams = teams.rename(columns={'name':'team'})
    players['playerid'] = players['playerid'].astype('int')
    teams['teamid'] = teams['teamid'].astype('int')


    fantasy = fantasy.join(players.set_index('playerid'), on='playerid')
    fantasy = fantasy.join(teams.set_index('teamid'), on ='teamid')
    cols = list(fantasy)
    cols[3], cols[-1] = cols[-1], cols[3]
    fantasy = fantasy.reindex(columns = cols)
    spreadsheet = fantasy.join(ratings.set_index('playerid'), on='playerid')
    print(spreadsheet)

    spreadsheet = spreadsheet.join(ratings_vs.set_index('playerid'), on='playerid')
    spreadsheet['rating/cost'] = 200 * spreadsheet['avg_rating']/spreadsheet['cost']
    spreadsheet['rating/cost'] = spreadsheet['rating/cost'].astype('float').round(3)
    # spreadsheet['rating/cost_tournament'] = 200 * spreadsheet['avg_rating_tournament']/spreadsheet['cost']
    # spreadsheet['rating/cost_tournament'] = spreadsheet['rating/cost_tournament'].astype('float').round(3)
    
    spreadsheet.to_csv('spreadsheet.csv', index = False)
    print(spreadsheet)


if __name__ == '__main__':
    main(591)