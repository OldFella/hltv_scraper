import pandas as pd

def get_team_id(file):
    df = pd.read_csv(file)
    df = df[['team_id', 'team_name']]
    df = df.rename(columns = {'team_id':'teamID', 'team_name':'name'})
    df.to_csv('../data/database/teams.csv',index = False)
    print(df)

def create_side_id(file):
    df = pd.DataFrame({'sideID': [0,1,2], 'name':['total', 'ct', 't']})
    df.to_csv(file, index = False)
    print(df)

def create_map_ids(file):
    df = pd.read_csv(file)
    maps = df['map'].unique()
    ids = list(range(len(maps)))
    df_map = pd.DataFrame({'mapID':ids, 'name':maps})
    df_map.to_csv('../data/database/maps.csv', index = False)

    print(df_map)


def sub_names_matches():
    matches = pd.read_csv('../data/database/matches.csv')
    sides = pd.read_csv('../data/database/sides.csv')
    sides = sides.rename(columns={'name':'side'}) 
    maps = pd.read_csv('../data/database/maps.csv')
    maps = maps.rename(columns={'name':'map'})
    teams = pd.read_csv('../data/database/teams.csv')
    teams = teams.rename(columns={'name':'team'})
    matches = matches.join(maps.set_index('map'), on=['map'])
    matches = matches.join(sides.set_index('side'), on=['side'])
    matches = matches.join(teams.set_index('team'), on=['team'])
    matches = matches.dropna()
    matches = matches[['matchID','teamID','score', 'mapID','sideID', 'date']]
    matches['teamID'] = matches['teamID'].astype(int)
    matches['score'] = matches['score'].astype(int)
    matches.to_csv('../data/database/matches.csv', index = False)
    # print(results[results['teamID'].isna()]['team'].unique())

def sub_names_player_stats():
    player_stats = pd.read_csv('../data/database/player_stats.csv')
    sides = pd.read_csv('../data/database/sides.csv')
    sides = sides.rename(columns={'name':'side'}) 
    maps = pd.read_csv('../data/database/maps.csv')
    maps = maps.rename(columns={'name':'map'})
    teams = pd.read_csv('../data/database/teams.csv')
    teams = teams.rename(columns={'name':'team'})
    player_stats = player_stats.join(maps.set_index('map'), on=['map'])
    player_stats = player_stats.join(sides.set_index('side'), on=['side'])
    player_stats = player_stats.join(teams.set_index('team'), on=['team'])
    player_stats = player_stats.dropna()
    player_stats['teamID'] = player_stats['teamID'].astype(int)
    cols = ['matchID', 'playerID','teamID', 'mapID', 'sideID', 'k', 'd', 'ek','ed', 'roundSwing', 'adr',  'eadr',  'kast',  'ekast',  'rating']
    print(player_stats)
    player_stats = player_stats[cols]
    player_stats[['k', 'd', 'ek','ed']] = player_stats[['k', 'd', 'ek','ed']].astype(int)
    print(player_stats)
    
    player_stats.to_csv('../data/database/player_stats.csv', index = False)


# get_team_id('../data/team_rankings/2026-01-18.csv')
# create_side_id('../data/database/sides.csv')
# create_map_ids('../data/database/player_stats.csv')
# sub_names_matches()
sub_names_player_stats()