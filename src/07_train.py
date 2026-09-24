# %%

import pandas as pd
import sqlalchemy
from sklearn import model_selection

con = sqlalchemy.create_engine("sqlite:///../data/db/database.db")

# %%
df = pd.read_sql("abt", con)

# %%

df.head()

# %%

matches = df[["uuid", "time_class", "fl_upset"]].drop_duplicates()

matches

# %%

train, test = model_selection.train_test_split(
    matches,
    random_state=42,
    train_size=0.8,
    stratify=matches["fl_upset"],
)

# %%
print(f"Taxa da target train: {train["fl_upset"].mean()}")
print(f"Taxa da target test: {test["fl_upset"].mean()}")

print(f"\nDistribuição do modo de jogo no train: ")
print(train["time_class"].value_counts())

print(f"\nDistribuição do modo de jogo no test: ")
print(test["time_class"].value_counts())

# %%
df_train = train.merge(df)
df_test = test.merge(df)

# %%

print(f"Dimensões do df completo: {df.shape}")
print(f"Dimensões do df train: {df_train.shape}")
print(f"Dimensões do df test: {df_test.shape}")

# %%
columns = df_train.columns.to_list()
columns

# %%

lag_columns = []

for column in columns:
    split = column.split("_")[-1]
    if split in ["d1", "d3", "d5"]:
        print(column)
        lag_columns.append(column)

# %%
nan_lag_columns = []

for column in columns:
    if column not in lag_columns:
        nan_lag_columns.append(column)

# %%

df_train[nan_lag_columns].isna().sum().head(60)