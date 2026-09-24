import sqlalchemy
from pathlib import Path

def main():

    engine = sqlalchemy.create_engine("sqlite:///../data/db/database.db")

    create_matches = Path("queries/create_matches.sql").read_text(encoding="utf-8")

    with engine.begin() as con:
        con.execute(sqlalchemy.text(create_matches))

if __name__ == "__main__":
    main()