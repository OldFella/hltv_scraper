import pandas as pd
import psycopg2
import numpy as np
import io
from configparser import ConfigParser


class db_handler:
    def __init__(self, filename = 'database.ini', section = 'postgresql'):
        config = self.load_config(filename=filename, section=section)
        self.con = psycopg2.connect(**config)
        self.cur = self.con.cursor()

    
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


class db_reader(db_handler):
    def __init__(self, filename = 'database.ini', section = 'postgresql'):
        super().__init__(filename, section)
        self.allowed_tables = ['matches', 'players', 'maps', 'teams', 'player_stats', 'fantasies', 'fantasy_overview']
        
    def get_matchids(self):
        query = "SELECT DISTINCT matchid FROM matches;"
        self.cur.execute(query)
        mids = self.cur.fetchall()
        mids = np.array(mids).T.squeeze()
        return mids
    
    def get_ids(self,table, id_name):
        query = f"SELECT DISTINCT {id_name} FROM {table}"
        self.cur.execute(query)
        ids = self.cur.fetchall()
        ids = np.array(ids).T.squeeze()
        return ids
    
    def get_table(self, table):
        assert table in self.allowed_tables
        query =f"SELECT * FROM {table};"
        self.cur.execute(query)
        table = self.cur.fetchall()
        table = np.array(table).squeeze()
        colnames = [desc[0] for desc in self.cur.description]
        return pd.DataFrame(table, columns=colnames)

    def get_columns(self,table):
        assert table in self.allowed_tables
        query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'"
        self.cur.execute(query)
        cols = self.cur.fetchall()
        cols = np.array(cols).T.squeeze()
        return cols
    
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
        self.cur.copy_expert(query, buffer)
        self.con.commit()



# config = load_config(section='user_read_only')
# dbh = db_reader(config)

# print(dbh.get_table('matches'))

# mids = dbh.get_matchids()
# # dbh.engine
# print(mids)