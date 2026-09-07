# %%
import pandas as pd
import sqlite3
from pathlib import Path
import sqlalchemy
import argparse

# con = sqlite3.connect("../data/db/database.db")
con = sqlalchemy.create_engine("sqlite:///../data/db/database.db")
pd.set_option('display.max_columns', None)

GAME_MODES = ["bullet", "blitz", "rapid"]

# %%

def load_parquet(path):
    df = pd.read_parquet(path)
    return df

def send_table(df, con, table="matches"):
    df.to_sql(table, con=con, if_exists="append", index=False)

def send_dir(con, dir_names=None, table="matches"):
    if dir_names is None:
        dir_names = GAME_MODES

    for dir_name in dir_names:
        parquet_dir_path = "../data/raw/" + dir_name
        directory = Path(parquet_dir_path)

        for file in directory.iterdir():
            path = file._raw_paths
            df = load_parquet(path[0])
            send_table(df, con=con, table=table)

# %%

df_test = load_parquet("../data/raw/blitz/Andreikka_2026-09-04_10-46-30.parquet")
df_test

# %%
send_table(df_test, con)

# %%

# Estou com problemas no PK uuid, pois a mesma partida pode acabar aparecendo duas vezes, no histórico dos dois players
# IntegrityError: UNIQUE constraint failed: matches.uuid

# Pensei em fazer um try except. mas acho que não é o ideal, pois iria deixar passar um parquet por completo, sendo que só não gostaria de passar uma única ocorrência

send_dir(con, dir_names=["blitz"])