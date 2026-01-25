from db_handler import db_writer
import pandas as pd
import numpy as np
import os
import shutil
import argparse


def open_fantasy(file):
    return pd.read_csv(file)

def rearrange_fantasy(df, dbw):
    cols = ['teams']

    for col in cols:
        df = rearrange_col(df,dbw,col)
    
    return df

def rearrange_col(df,dbw, col):
    table = dbw.get_table(col)
    index_col = col[:-1]
    table = table.rename(columns={'name':index_col})
    df = df.join(table.set_index(index_col), on=index_col)
    df = df.dropna()
    df.drop(columns = [index_col], axis =1, inplace =True)
    return df

def split_fantasy(df):
    df_overview = df[['fantasyID', 'title']]
    df_overview = df_overview.rename(columns={'title':'name'})
    df_overview = df_overview.rename(str.lower, axis = 'columns')
    df_overview = df_overview.drop_duplicates()
    df_fantasy = df[['fantasyID', 'teamid', 'playerid', 'cost']]
    df_fantasy = df_fantasy.rename(str.lower, axis = 'columns')

    return df_overview, df_fantasy

def insert_table(df_overview, df_fantasy, dbw):
    dbw.insert(df_overview, 'fantasy_overview')
    dbw.insert(df_fantasy, 'fantasies')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--input','-i', type = str, default = "")
    args = parser.parse_args()

    dbw = db_writer()

    df = open_fantasy(args.input)

    df = rearrange_fantasy(df, dbw)

    df_overview, df_fantasy = split_fantasy(df)

    insert_table(df_overview, df_fantasy, dbw)
