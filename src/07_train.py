# %%

import pandas as pd
import sqlalchemy
from sklearn import model_selection
from sklearn import ensemble
from sklearn import metrics
from feature_engine import imputation, encoding
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

print((df_train[lag_columns].isna().sum()).to_string())


# %%

all_features = columns[4:]
all_features.append('ply_count')
target = "fl_upset"

X_train, y_train = df_train[all_features], df_train[target]
X_test, y_test = df_test[all_features], df_test[target]


# %%
# df_train_early = df_train.loc[df_train["ply_count"] <= 20]
# df_train_mid = df_train.loc[(df_train["ply_count"] > 20) & (df_train["ply_count"] <= 60)]
# df_train_end = df_train.loc[df_train["ply_count"] > 60]

# X_train_early, y_train_early = df_train_early[all_features], df_train_early[target]
# X_train_mid, y_train_mid = df_train_mid[all_features], df_train_mid[target]
# X_train_end, y_train_end = df_train_end[all_features], df_train_end[target]

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

X_test_transform = imp_0.transform(X=X_test)
X_test_transform = imp_1.transform(X=X_test_transform)
X_test_transform = imp_2.transform(X=X_test_transform)
X_test_transform = imp_8.transform(X=X_test_transform)
X_test_transform = imp_none.transform(X=X_test_transform)

X_test_transform = one_hot.transform(X=X_test_transform)
print("Quantidade de Missing: ", (X_test_transform.isna().sum().sum()))

# %%
X_train_transform_early = X_train_transform.loc[X_train_transform["ply_count"] <= 20]
X_train_transform_early = X_train_transform_early.drop(columns=["ply_count"])

X_train_transform_mid = X_train_transform.loc[(X_train_transform["ply_count"] > 20) & (X_train_transform["ply_count"] <= 60)]
X_train_transform_mid = X_train_transform_mid.drop(columns=["ply_count"])

X_train_transform_end = X_train_transform.loc[X_train_transform["ply_count"] > 60]
X_train_transform_end = X_train_transform_end.drop(columns=["ply_count"])

X_train_transform = X_train_transform.drop(columns=["ply_count"])


X_test_transform_early = X_test_transform.loc[X_test_transform["ply_count"] <= 20]
X_test_transform_early = X_test_transform_early.drop(columns=["ply_count"])

X_test_transform_mid = X_test_transform.loc[(X_test_transform["ply_count"] > 20) & (X_test_transform["ply_count"] <= 60)]
X_test_transform_mid = X_test_transform_mid.drop(columns=["ply_count"])

X_test_transform_end = X_test_transform.loc[X_test_transform["ply_count"] > 60]
X_test_transform_end = X_test_transform_end.drop(columns=["ply_count"])

X_test_transform = X_test_transform.drop(columns=["ply_count"])


# %%
y_train_early = y_train.iloc[X_train_transform_early.index]
y_train_mid = y_train.iloc[X_train_transform_mid.index]
y_train_end = y_train.iloc[X_train_transform_end.index]

y_test_early = y_test.iloc[X_test_transform_early.index]
y_test_mid = y_test.iloc[X_test_transform_mid.index]
y_test_end = y_test.iloc[X_test_transform_end.index]



# %%

# X_train_trans_early = imp_0.fit_transform(X=X_train_early)
# X_train_trans_early = imp_1.fit_transform(X=X_train_trans_early)
# X_train_trans_early = imp_2.fit_transform(X=X_train_trans_early)
# X_train_trans_early = imp_8.fit_transform(X=X_train_trans_early)
# X_train_trans_early = imp_none.fit_transform(X=X_train_trans_early)

# X_train_trans_early = one_hot.fit_transform(X=X_train_trans_early)
# # %%

# X_train_trans_mid = imp_0.fit_transform(X=X_train_mid)
# X_train_trans_mid = imp_1.fit_transform(X=X_train_trans_mid)
# X_train_trans_mid = imp_2.fit_transform(X=X_train_trans_mid)
# X_train_trans_mid = imp_8.fit_transform(X=X_train_trans_mid)
# X_train_trans_mid = imp_none.fit_transform(X=X_train_trans_mid)

# X_train_trans_mid = one_hot.fit_transform(X=X_train_trans_mid)
# # %%

# X_train_trans_end = imp_0.fit_transform(X=X_train_end)
# X_train_trans_end = imp_1.fit_transform(X=X_train_trans_end)
# X_train_trans_end = imp_2.fit_transform(X=X_train_trans_end)
# X_train_trans_end = imp_8.fit_transform(X=X_train_trans_end)
# X_train_trans_end = imp_none.fit_transform(X=X_train_trans_end)

# X_train_trans_end = one_hot.fit_transform(X=X_train_trans_end)
# %%

rf = ensemble.RandomForestClassifier(
    n_estimators=500,
    min_samples_leaf=50,
    random_state=42,
    n_jobs=3,
)

rf.fit(X_train_transform, y_train)

# %%

y_train_early_proba = rf.predict_proba(X_train_transform_early)[:,1]
auc_train_early = metrics.roc_auc_score(y_train_early, y_train_early_proba)

print(f"AUC Train Early: {auc_train_early}")

y_test_early_proba = rf.predict_proba(X_test_transform_early)[:,1]
auc_test_early = metrics.roc_auc_score(y_test_early, y_test_early_proba)

print(f"AUC test Early: {auc_test_early}")

# %%

y_train_mid_proba = rf.predict_proba(X_train_transform_mid)[:,1]
auc_train_mid = metrics.roc_auc_score(y_train_mid, y_train_mid_proba)

print(f"AUC Train mid: {auc_train_mid}")

y_test_mid_proba = rf.predict_proba(X_test_transform_mid)[:,1]
auc_test_mid = metrics.roc_auc_score(y_test_mid, y_test_mid_proba)

print(f"AUC test mid: {auc_test_mid}")
# %%

y_train_end_proba = rf.predict_proba(X_train_transform_end)[:,1]
auc_train_end = metrics.roc_auc_score(y_train_end, y_train_end_proba)

print(f"AUC Train end: {auc_train_end}")

y_test_end_proba = rf.predict_proba(X_test_transform_end)[:,1]
auc_test_end = metrics.roc_auc_score(y_test_end, y_test_end_proba)

print(f"AUC test end: {auc_test_end}")

# %%

feature_importances = pd.Series(rf.feature_importances_, index=X_train_transform.columns.to_list())
feature_importances = feature_importances.sort_values(ascending=False)
feature_importances.head(40)
