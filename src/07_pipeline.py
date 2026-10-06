# %%

import pandas as pd
import numpy as np
import sqlalchemy
from sklearn import model_selection
from sklearn import ensemble, tree
from sklearn import metrics
from feature_engine import imputation, encoding
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

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

### Missing

X_train.isna().sum().sort_values(ascending=False)

# %%

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

features_0_imp = features_0_imputation(all_features)
features_1_imp = features_imputation(["qtde_queen"])
features_2_imp = features_imputation(["qtde_knight",
                                      "qtde_bishop",
                                      "qtde_rook"])
features_8_imp = features_imputation(["qtde_pawn"])
features_none_imp = features_imputation(["move_piece"])
features_none_imp.extend(["time_class", "turn"])

# %%

imp_0 = imputation.ArbitraryNumberImputer(0, variables=features_0_imp)
imp_1 = imputation.ArbitraryNumberImputer(1, variables=features_1_imp)
imp_2 = imputation.ArbitraryNumberImputer(2, variables=features_2_imp)
imp_8 = imputation.ArbitraryNumberImputer(8, variables=features_8_imp)
imp_none = imputation.CategoricalImputer(fill_value="none", variables=features_none_imp)

one_hot = encoding.OneHotEncoder(variables=features_none_imp)


# %%

X_train_transform = imp_0.fit_transform(X=X_train)
X_train_transform = imp_1.fit_transform(X=X_train_transform)
X_train_transform = imp_2.fit_transform(X=X_train_transform)
X_train_transform = imp_8.fit_transform(X=X_train_transform)
X_train_transform = imp_none.fit_transform(X=X_train_transform)

X_train_transform = one_hot.fit_transform(X=X_train_transform)
print("Quantidade de Missing: ", (X_train_transform.isna().sum().sum()))

# %%

### Summary

# game phases X_train

X_train_transform_early = X_train_transform.loc[((X_train_transform["ply_count"] <= 15) &
                                                (X_train_transform["qtde_queen"] == 1))]
X_train_transform_early = X_train_transform_early.drop(columns=["ply_count"])

X_train_transform_mid = X_train_transform.loc[((X_train_transform["ply_count"] > 15) & 
                                              (X_train_transform["ply_count"] <= 60) &
                                              (X_train_transform["qtde_queen"] == 1))]
X_train_transform_mid = X_train_transform_mid.drop(columns=["ply_count"])

X_train_transform_end = X_train_transform.loc[((X_train_transform["ply_count"] > 60) |
                                              (X_train_transform["qtde_queen"] == 0))]
X_train_transform_end = X_train_transform_end.drop(columns=["ply_count"])

X_train_transform = X_train_transform.drop(columns=["ply_count"])

# %%
# game phases y_train
y_train_early = y_train.iloc[X_train_transform_early.index]
y_train_mid = y_train.iloc[X_train_transform_mid.index]
y_train_end = y_train.iloc[X_train_transform_end.index]


# %%

df_explore_early = X_train_transform_early.copy()
df_explore_early[target] = y_train_early

df_explore_mid = X_train_transform_mid.copy()
df_explore_mid[target] = y_train_mid

df_explore_end = X_train_transform_end.copy()
df_explore_end[target] = y_train_end

# %%
summary_early = df_explore_early.groupby("fl_upset").agg(["mean", "median"]).T
summary_early["diff_abs"] = (summary_early[0]) - (summary_early[1])
summary_early["diff_rel"] = (summary_early[0]) / (summary_early[1])
summary_early.sort_values("diff_rel", ascending=False)
# %%
summary_mid = df_explore_mid.groupby("fl_upset").agg(["mean", "median"]).T
summary_mid["diff_abs"] = (summary_mid[0]) - (summary_mid[1])
summary_mid["diff_rel"] = (summary_mid[0]) / (summary_mid[1])
summary_mid.sort_values("diff_rel", ascending=False)
# %%
summary_end = df_explore_end.groupby("fl_upset").agg(["mean", "median"]).T
summary_end["diff_abs"] = (summary_end[0]) - (summary_end[1])
summary_end["diff_rel"] = (summary_end[0]) / (summary_end[1])
summary_end.sort_values("diff_rel", ascending=False)

# %%

dtc = tree.DecisionTreeClassifier(random_state=42)
dtc.fit(X_train_transform, y_train)

# %%
feature_importance = pd.Series(dtc.feature_importances_, index=X_train_transform.columns).sort_values(ascending=False).reset_index()
feature_importance["acum."] = feature_importance[0].cumsum()
feature_importance = feature_importance[feature_importance["acum."] < 0.96]
feature_importance

# %%
