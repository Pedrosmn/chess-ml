# %%

import pandas as pd
import sqlalchemy
from sklearn import model_selection
from sklearn import ensemble
from sklearn import metrics
from feature_engine import imputation
pd.set_option('display.max_columns', None)

con = sqlalchemy.create_engine("sqlite:///../data/db/database.db")

# %%
df = pd.read_sql("abt", con)
df.head()

# %%
matches = df[["uuid", "fl_upset"]].drop_duplicates()

train, test = model_selection.train_test_split(
    matches,
    random_state=42,
    train_size=0.8,
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
columns

lag_columns = []

for column in columns:
    split = column.split("_")[-1]
    if split in ["d1", "d3", "d5"]:
        lag_columns.append(column)

nan_lag_columns = []

for column in columns:
    if column not in lag_columns:
        nan_lag_columns.append(column)

# %%

print((df_train[lag_columns].isna().sum()).to_string())


# %%

df_train.head()

# %%

features = columns[4:]
target = "fl_upset"

X_train, y_train = df_train[features], df_train[target]
X_test, y_test = df_test[features], df_test[target]


def features_0_imputation(all_features):
    features_0_imp = all_features
    lags = ["","_d1","_d3","_d5"]
    for lag in lags:
        non_0_features = [
            f"qtde_pawn{lag}",
            f"qtde_knight{lag}",
            f"qtde_bishop{lag}",
            f"qtde_rook{lag}",
            f"qtde_queen{lag}",
            f"move_piece{lag}",
        ]
        for f in non_0_features:
            features_0_imp.remove(f)

    features_0_imp = [f for f in features_0_imp if f not in ["turn", "time_class"]]
    return features_0_imp

def features_imputation(columns):
    lags = ["","_d1","_d3","_d5"]
    features = []
    for lag in lags:
        for column in columns:
            features.append(f"{column}{lag}")

    return features

features_0_imp = features_0_imputation(features)
features_1_imp = features_imputation(["qtde_queen"])
features_2_imp = features_imputation(["qtde_knight",
                                      "qtde_bishop",
                                      "qtde_rook"])
features_8_imp = features_imputation(["qtde_pawn"])
features_none_imp = features_imputation(["move_piece"])

# %%

imp_0 = imputation.ArbitraryNumberImputer(0, variables=features_0_imp)
imp_1 = imputation.ArbitraryNumberImputer(1, variables=features_1_imp)
imp_2 = imputation.ArbitraryNumberImputer(2, variables=features_2_imp)
imp_8 = imputation.ArbitraryNumberImputer(8, variables=features_8_imp)
imp_none = imputation.CategoricalImputer(fill_value="none", variables=features_none_imp)

# %%

X_train_transform = imp_0.fit_transform(X=X_train)
X_train_transform = imp_1.fit_transform(X=X_train_transform)
X_train_transform = imp_2.fit_transform(X=X_train_transform)
X_train_transform = imp_8.fit_transform(X=X_train_transform)
X_train_transform = imp_none.fit_transform(X=X_train_transform)
print("Quantidade de Missing: ", (X_train_transform.isna().sum().sum()))
X_train_transform.head(10)

# %%

