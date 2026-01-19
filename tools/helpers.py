import pandas as pd
import os

def create_ids(values,name):
    df = pd.DataFrame(columns=[f'{name}ID', 'name'])
    df['name'] = values
    df = df.drop_duplicates()
    ids = [i for i in range(len(df))]

    df[f'{name}ID'] = ids
    return df

def create_map_ids(file):
    matches = pd.read_csv(file)
    return create_ids(matches['map'], 'map')

def create_team_ids(file):
    teams = pd.read_csv(file)
    return create_ids(teams['team'], 'team')


def check_stats(file1,file2):
    matches = pd.read_csv(file1)
    stats = pd.read_csv(file2)

    matchid1 = matches['matchID'].unique()
    matchid2 = stats['matchID'].unique()
    print(matchid1, matchid2)
    print(len(matchid1), len(matchid2))
    diff =list(set(matchid1) ^ set(matchid2)) 
    match_list = pd.read_csv('../data/matches/matches.csv')
    matches = matches[~matches['matchID'].isin(diff)]
    matches.to_csv(file1,index=False)

def check_faulty_entries():
    table = pd.read_csv('../data/database/player_stats.csv')
    df = table.groupby('matchID').count()
    df['check'] = df['k'] % 30
    faulty = df[~df['check'].isin([3,6]) ]

    faulty = faulty[faulty['check'] != 0].reset_index()
    # print(faulty.reset_index())
    # print(faulty.dtype)
    table = table[~table['matchID'].isin(faulty['matchID'])]
    table.to_csv('../data/database/player_stats.csv', index=False)

    # print(df[df['check']!= 0])

# print(check_faulty_entries())
check_stats('../data/database/matches.csv', '../data/database/player_stats.csv')
# print(create_map_ids('../data/database/matches.csv'))
# print(create_team_ids('../data/database/matches.csv'))