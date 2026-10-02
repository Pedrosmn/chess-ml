# %%

import pandas as pd
import numpy as np
import sqlalchemy
from sklearn import model_selection
from sklearn import ensemble, tree
from sklearn import metrics
from feature_engine import imputation, encoding
pd.set_option('display.max_columns', None)

con = sqlalchemy.create_engine("sqlite:///../data/db/database.db")

# %%

# SEMMA

## SAMPLE

df = pd.read_sql("abt", con)
df.head()

# %%
matches = df[["uuid", "fl_upset"]].drop_duplicates()

train, test = model_selection.train_test_split(
    matches,
    random_state=42,
    train_size=0.7,
    stratify=matches["fl_upset"],
)

# %%
print(f"Taxa da target train: {train["fl_upset"].mean()}")
print(f"Taxa da target test: {test["fl_upset"].mean()}")


# %%
df_train = train.merge(df)
df_test = test.merge(df)

print(f"\nDistribuição do modo de jogo no train: ")
print(df_train["time_class"].value_counts())

print(f"\nDistribuição do modo de jogo no test: ")
print(df_test["time_class"].value_counts())

print(f"Dimensões do df completo: {df.shape}")
print(f"Dimensões do df train: {df_train.shape}")
print(f"Dimensões do df test: {df_test.shape}")

# %%
columns = df_train.columns.to_list()

all_features = columns[4:]
all_features.append('ply_count')
target = "fl_upset"
# %%

X_train, y_train = df_train[all_features], df_train[target]
X_test, y_test = df_test[all_features], df_test[target]

# %%

## EXPLORE

