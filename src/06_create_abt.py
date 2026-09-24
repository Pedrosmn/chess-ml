import sqlalchemy

con = sqlalchemy.create_engine("sqlite:///../data/db/database.db")

def create_abt():
    print("Criando ABT...")
    with open("queries/create_abt.sql", encoding="utf-8") as query_file:
        query = query_file.read()

    with con.begin() as conn:
        conn.execute(sqlalchemy.text(query))
        print("ABT criada.")

def main():
    create_abt()

if __name__ == "__main__":
    main()