import pandas as pd
import psycopg2
import numpy as np
import io
from configparser import ConfigParser
from jinjasql import JinjaSql
import datetime


class db_handler:
    def __init__(self, filename = 'database.ini', section = 'postgresql'):
        config = self.load_config(filename=filename, section=section)
        self.con = psycopg2.connect(**config)
        self.cur = self.con.cursor()
        self.j = JinjaSql(param_style='pyformat')

    
    def load_config(self,filename='database.ini', section='postgresql'):
        parser = ConfigParser()
        parser.read(filename)

        # get section, default to postgresql
        config = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                config[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))

        return config
    
    def execute(self, query):
        self.cur.execute(query)
        results = self.cur.fetchall()
        columns = [desc[0] for desc in self.cur.description]
        if results == []:
            return pd.DataFrame(columns=columns)
        results = np.array(results)
        results = pd.DataFrame(results, columns = columns)
        return results

    def get_query(self, file, params):
        with open(file, 'r') as f:
            template = f.read()        
        try:
            query, params = self.j.prepare_query(template,params)
            query = query % params
        except:
            raise Exception('Failed to build query')
        return query
    
    def query(self,f,params):
        query = self.get_query(f,params)
        return self.execute(query)
    
class db_reader(db_handler):
    def __init__(self, filename = 'database.ini', section = 'postgresql', query_dir = 'queries/'):
        super().__init__(filename, section)
        self.allowed_tables = ['matches', 'players', 'maps','sides', 'teams', 'player_stats', 'fantasies', 'fantasy_overview']
        self.query_dir = query_dir

    def get_matchids(self):
        query = "SELECT DISTINCT matchid FROM matches;"
        mids = self.execute(query)
        mids = np.array(mids).T.squeeze()
        return mids
    
    def get_ids(self,table, id_name):
        query = f"SELECT DISTINCT {id_name} FROM {table}"
        ids = self.execute(query)
        ids = np.array(ids).T.squeeze()
        return ids
    
    def get_name(self, table, idname, id):
        query = f"SELECT name FROM {table} WHERE {idname} = {id}"
        name = self.execute(query)
        name = np.array(name).T.squeeze()
        return name
    
    def get_table(self, table):
        assert table in self.allowed_tables
        query =f"SELECT * FROM {table};"
        table = self.execute(query)
        table = np.array(table).squeeze()
        colnames = [desc[0] for desc in self.cur.description]
        return pd.DataFrame(table, columns=colnames)

    def get_columns(self,table):
        assert table in self.allowed_tables
        query = f"""SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = '{table}'"""
        cols = self.execute(query)
        cols = np.array(cols).T.squeeze()
        return cols
    
    def get_match_history(self, team, map = 0, side = 0, start_date = 0, months = 3):
        if start_date ==0:
            start_date = datetime.date.today()
        params = {'team':team,
                  'sideid': side,
                  'mapid': map,
                  'start_date': start_date,
                  'months': months}
        _TEMPLATE_ = f'{self.query_dir}get_match_history.sql'
        return self.query(_TEMPLATE_, params)

    def get_average_player_rating(self, player, map = 0, side = 0, start_date = 0, months = 3):
        if start_date ==0:
            start_date = datetime.date.today()
        params = {'playerid':player,
                  'sideid': side,
                  'mapid': map,
                  'start_date': start_date,
                  'months': months}
        _TEMPLATE_ = f'{self.query_dir}get_average_player_rating.sql'
        return self.query(_TEMPLATE_, params)
    
    def get_average_ratings_fantasy_vs(self, fantasyid, start_date = 0, months = 3, vs = None):
        if start_date ==0:
            start_date = datetime.date.today()
        params = {'fantasyid':fantasyid,
                  'start_date': start_date,
                  'months': months,
                  'vs':vs}
        _TEMPLATE_ = f'{self.query_dir}get_average_ratings_fantasy_vs.sql'
        return self.query(_TEMPLATE_, params)
    
    def get_average_ratings_fantasy_event(self, fantasyid, start_date = 0, months = 3):
        if start_date ==0:
            start_date = datetime.date.today()
        params = {'fantasyid':fantasyid,
                  'start_date': start_date,
                  'months': months}
        _TEMPLATE_ = f'{self.query_dir}get_average_ratings_fantasy_event.sql'
        return self.query(_TEMPLATE_, params)


    def get_average_ratings_fantasy(self, fantasyid, start_date = 0, months = 3):
        if start_date ==0:
            start_date = datetime.date.today()
        params = {'fantasyid':fantasyid,
                  'start_date': start_date,
                  'months': months}
        _TEMPLATE_ = f'{self.query_dir}get_average_ratings_fantasy.sql'
        return self.query(_TEMPLATE_, params)

    def get_winrate(self, teamid, mapid, start_date = 0, months = 3):
        if start_date ==0:
            start_date = datetime.date.today()
        params = {'teamid':teamid,
                  'mapid': mapid,
                  'start_date': start_date,
                  'months': months}
        _TEMPLATE_ = f'{self.query_dir}get_winrate.sql'
        return self.query(_TEMPLATE_, params)
    
    def get_winrate_h2h(self,teamid ,opponentid,mapid, start_date = 0, months = 3):
        if start_date ==0:
            start_date = datetime.date.today()
        params = {'teamid':teamid,
                  'opponentid': opponentid,
                  'mapid': mapid,
                  'start_date': start_date,
                  'months': months}
        _TEMPLATE_ = f'{self.query_dir}get_winrate_h2h.sql'
        return self.query(_TEMPLATE_, params)
    
    
class db_writer(db_reader):

    def insert(self,df, table):
        assert table in self.allowed_tables
        table_cols = self.get_columns(table)
        col_names, col_dtypes = table_cols
        df = df[col_names]
        integer_cols = col_names[col_dtypes == 'integer']
        df[integer_cols] = df[integer_cols].astype(int)
        buffer = io.StringIO()
        df.to_csv(buffer, index = False, header = False)
        buffer.seek(0)
        query = f'COPY {table} FROM STDIN WITH CSV'
        print('copy...')
        self.cur.copy_expert(query, buffer)
        print('commit...')
        self.con.commit()
