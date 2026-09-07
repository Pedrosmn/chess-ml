# %%
import pandas as pd
import sqlite3

con = sqlite3.connect("../data/db/database.db")
pd.set_option('display.max_columns', None)


# %%

df = pd.read_parquet("../data/raw/blitz/Andreikka_2026-09-04_10-46-30.parquet")
df
# %%

df.to_sql(name="matches", con=con, if_exists="append", index=False)

# %%

df.columns.to_list()

# %%

df.head()

# %%
