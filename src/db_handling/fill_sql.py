from sqlalchemy import create_engine,inspect
from sqlalchemy import exc
import pandas as pd

engine = create_engine('postgresql+psycopg2://postgres:password@localhost:5432/hltv')

# files = ['players', 'maps', 'sides', 'teams', 'matches', 'player_stats']
files = ['player_stats']

for file in files:

    df = pd.read_csv(f'../data/database/{file}.csv')
    df = df.rename(str.lower, axis='columns')
    df = df.drop_duplicates()
    # print(df)
    df.to_sql(name=file,if_exists='append',con = engine, index = False,chunksize=10000)
    # for i in range(len(df)):
    #     try:
    #         df.iloc[i:i+1].to_sql(name=file,if_exists='append',con = engine, index = False)
    #     except exc.IntegrityError:
    #         pass #or any other action


inspector = inspect(engine)
schemas = inspector.get_schema_names()

for schema in schemas:
    print("schema: %s" % schema)
    for table_name in inspector.get_table_names(schema=schema):
        for column in inspector.get_columns(table_name, schema=schema):
            print("Column: %s" % column)


