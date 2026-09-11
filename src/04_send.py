import pandas as pd
from pathlib import Path
import sqlalchemy
import argparse

GAME_MODES = ["bullet", "blitz", "rapid"]

class ParquetSender:
    def __init__(self, con, table="matches"):
        self.con = con
        self.table = table

    @staticmethod
    def load_parquet(path):
        df = pd.read_parquet(path)
        return df

    def select_distinct_id(self, df):
        primary_keys = pd.read_sql("SELECT uuid FROM matches", con=self.con)
        df = df[~df["uuid"].isin(primary_keys["uuid"])]
        return df
    
    def send_table(self, df):
        df = self.select_distinct_id(df)
        df.to_sql(self.table, con=self.con, if_exists="append", index=False)

    def send_dir(self, dir_names=None):
        if dir_names is None:
            dir_names = GAME_MODES

        for dir_name in dir_names:
            parquet_dir_path = Path("../data/raw") / dir_name
            directory = Path(parquet_dir_path)

            for file in directory.iterdir():
                df = self.load_parquet(file)
                self.send_table(df)

def main():
    con = sqlalchemy.create_engine("sqlite:///../data/db/database.db")

    parser = argparse.ArgumentParser()

    parser.add_argument("--game_modes", nargs="+", choices=["bullet", "blitz", "rapid"], default=["bullet", "blitz", "rapid"])

    args = parser.parse_args()

    sender = ParquetSender(con)
    sender.send_dir(args.game_modes)

if __name__ == "__main__":
    main()