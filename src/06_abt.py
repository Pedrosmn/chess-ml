# %%

import pandas as pd
import sqlalchemy

con = sqlalchemy.create_engine("sqlite:///../data/db/database.db")

# %%

df = pd.read_sql("abt", con=con)

# %%

df