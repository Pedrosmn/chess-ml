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
df = pd.read_sql("abt", con)
df


# %%

ply_col = "ply_count"
# %%
df = df[df["elo_diff"] != 0].copy()
df = df.drop(columns=[c for c in df.columns if c.endswith(("_d1", "_d3", "_d5"))])  # lags serão refeitos
df = df.sort_values(["uuid", ply_col]).reset_index(drop=True)


move_is_upset = (df["elo_diff"] < 0).to_numpy()
move_is_upset

# %%
move_is_upset_num  = np.where(move_is_upset, 1, -1)
move_is_upset_num
# %%

df_new = pd.DataFrame({
    "uuid": df["uuid"], ply_col: df[ply_col], "fl_upset": df["fl_upset"],
    "elo_gap": df["elo_diff"].abs(),
    "mover_is_underdog": move_is_upset.astype(int),
})


# 1) diferenças com sinal -> vantagem do azarão
for c in ["time_diff", "diff_pawn", "diff_knight", "diff_bishop", "diff_rook", "diff_queen"]:
    df_new[f"und_adv_{c}"] = df[c] * move_is_upset_num

df_new

# %%

# 2) pares "de quem jogou / do oponente" -> azarão / favorito
pairs = {
    "has_castled": "opp_has_castled",
    "has_king_castled": "opp_has_king_castled",
    "has_queen_castled": "opp_has_queen_castled",
    "has_2_repetition": "opp_has_2_repetition",
    "has_promotion": "opp_has_promotion",
    "qtde_capture": "opp_qtde_capture",
    "qtde_irreversible": "opp_qtde_irreversible",
    "recency_capture": "opp_recency_capture",
    "recency_gives_check": "opp_recency_gives_check",
    "recency_is_irreversible": "opp_recency_is_irreversible",
}
for p in ["pawn", "knight", "bishop", "rook", "queen", "king"]:
    pairs[f"recency_{p}_move"] = f"opp_recency_{p}_piece"

for own, opp in pairs.items():
    df_new[f"und_{own}"] = np.where(move_is_upset, df[own], df[opp])
    df_new[f"fav_{own}"] = np.where(move_is_upset, df[opp], df[own])

# 3) contagem de peças (a do oponente sai de qtde - diff)
for p in ["pawn", "knight", "bishop", "rook", "queen"]:
    own = df[f"qtde_{p}"]
    opp = own - df[f"diff_{p}"]
    df_new[f"und_qtde_{p}"] = np.where(move_is_upset, own, opp)
    df_new[f"fav_qtde_{p}"] = np.where(move_is_upset, opp, own)

# 4) propriedades do lance atual (ficam como estão)
for c in ["move_piece", "is_capture", "is_irreversible", "gives_check", "is_2_repetition", "is_trade"]:
    df_new[c] = df[c]

# 5) deltas no referencial fixo (k par = mesmo lado joga)
state = [c for c in df_new.columns if c.startswith(("und_adv_", "und_qtde_", "fav_qtde_"))]
g = df_new.groupby("uuid")
for k in (2, 4, 6):
    for c in state:
        df_new[f"{c}_d{k}"] = df_new[c] - g[c].shift(k)


# %%

matches = df_new[["uuid", "fl_upset"]].drop_duplicates()

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
df_train = train.merge(df_new)
df_test = test.merge(df_new)

print(f"Dimensões do df completo: {df_new.shape}")
print(f"Dimensões do df train: {df_train.shape}")
print(f"Dimensões do df test: {df_test.shape}")

# %%
columns = df_train.columns.to_list()
columns

# %%

lag_columns = []

for column in columns:
    split = column.split("_")[-1]
    if split in ["d2", "d4", "d6"]:
        lag_columns.append(column)

nan_lag_columns = []

for column in columns:
    if column not in lag_columns:
        nan_lag_columns.append(column)

print((df_train[lag_columns].isna().sum()).to_string())

# %%

all_features = columns[3:]
all_features.append('ply_count')
target = "fl_upset"

X_train, y_train = df_train[all_features], df_train[target]
X_test, y_test = df_test[all_features], df_test[target]


# %%

def features_0_imputation(all_features):
    features_0_imp = all_features
    # print(features_0_imp)
    lags = ["","_d2","_d4","_d6"]
    players = ["und", "fav"]
    for lag in lags:
        for player in players:
            non_0_features = [
                f"{player}_qtde_pawn{lag}",
                f"{player}_qtde_knight{lag}",
                f"{player}_qtde_bishop{lag}",
                f"{player}_qtde_rook{lag}",
                f"{player}_qtde_queen{lag}",
                f"{player}_move_piece{lag}",
            ]
            # print(non_0_features)
            for f in non_0_features:
                # print(f)
                # print(features_0_imp)
                try:
                    features_0_imp.remove(f)
                except:
                    continue

    features_0_imp = [f for f in features_0_imp if f not in ["turn", "time_class"]]
    return features_0_imp

def features_imputation(columns):
    lags = ["","_d1","_d3","_d5"]
    players = ["und", "fav"]
    features = []
    for lag in lags:
        for player in players:
            for column in columns:
                features.append(f"{player}_{column}{lag}")

    return features


# %%

features_0_imp = features_0_imputation(all_features)
features_0_imp.remove('move_piece')
# features_1_imp = features_imputation(["qtde_queen"])
# features_2_imp = features_imputation(["qtde_knight",
#                                       "qtde_bishop",
#                                       "qtde_rook"])
# features_8_imp = features_imputation(["qtde_pawn"])
features_none_imp = features_imputation(["move_piece"])
features_none_imp.extend(["time_class", "turn"])

# %%
features_0_imp

# %%

imp_0 = imputation.ArbitraryNumberImputer(0, variables=features_0_imp)
# imp_1 = imputation.ArbitraryNumberImputer(1, variables=features_1_imp)
# imp_2 = imputation.ArbitraryNumberImputer(2, variables=features_2_imp)
# imp_8 = imputation.ArbitraryNumberImputer(8, variables=features_8_imp)
imp_none = imputation.CategoricalImputer(fill_value="none", variables=features_none_imp)

one_hot = encoding.OneHotEncoder(variables=features_none_imp)

# %%
imp_0
# %%

X_train_transform = imp_0.fit_transform(X=X_train)
X_train_transform.isna().sum().tail(30)
#%%
X_train_transform = X_train_transform.drop(columns=["move_piece"])
# X_train_transform = imp_1.fit_transform(X=X_train_transform)
# X_train_transform = imp_2.fit_transform(X=X_train_transform)
# X_train_transform = imp_8.fit_transform(X=X_train_transform)
# X_train_transform = imp_none.fit_transform(X=X_train_transform)

# X_train_transform = one_hot.fit_transform(X=X_train_transform)
print("Quantidade de Missing: ", (X_train_transform.isna().sum().sum()))

# %%

X_test_transform = imp_0.transform(X=X_test)
X_test_transform = X_test_transform.drop(columns=["move_piece"])
# X_test_transform = imp_1.transform(X=X_test_transform)
# X_test_transform = imp_2.transform(X=X_test_transform)
# X_test_transform = imp_8.transform(X=X_test_transform)
# X_test_transform = imp_none.transform(X=X_test_transform)

# X_test_transform = one_hot.transform(X=X_test_transform)
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
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score

base = ["elo_gap"]
plus = base + [c for c in df_new.columns if c.startswith("und_adv_") and "d" not in c]

for nome, cols in [("baseline", base), ("baseline + estado", plus)]:
    m = LogisticRegression(max_iter=2000).fit(X_train_transform[cols], y_train)
    p = m.predict_proba(X_test_transform_end[cols])[:, 1]
    print(nome, roc_auc_score(y_test_end, p), average_precision_score(y_test_end, p))

# %%

rf = ensemble.RandomForestClassifier(
    n_estimators=500,
    min_samples_leaf=50,
    random_state=42,
    n_jobs=3,
    # max_depth=8,
)

rf.fit(X_train_transform, y_train)
# %%
y_train_early_proba = rf.predict_proba(X_train_transform_early)[:,1]
auc_train_early = metrics.roc_auc_score(y_train_early, y_train_early_proba)

print(f"AUC Train Early: {auc_train_early}")

y_test_early_proba = rf.predict_proba(X_test_transform_early)[:,1]
auc_test_early = metrics.roc_auc_score(y_test_early, y_test_early_proba)

print(f"AUC test Early: {auc_test_early}")


y_train_mid_proba = rf.predict_proba(X_train_transform_mid)[:,1]
auc_train_mid = metrics.roc_auc_score(y_train_mid, y_train_mid_proba)

print(f"AUC Train mid: {auc_train_mid}")

y_test_mid_proba = rf.predict_proba(X_test_transform_mid)[:,1]
auc_test_mid = metrics.roc_auc_score(y_test_mid, y_test_mid_proba)

print(f"AUC test mid: {auc_test_mid}")

y_train_end_proba = rf.predict_proba(X_train_transform_end)[:,1]
auc_train_end = metrics.roc_auc_score(y_train_end, y_train_end_proba)

print(f"AUC Train end: {auc_train_end}")

y_test_end_proba = rf.predict_proba(X_test_transform_end)[:,1]
auc_test_end = metrics.roc_auc_score(y_test_end, y_test_end_proba)

print(f"AUC test end: {auc_test_end}")

# %%

feature_importances_rf = pd.Series(rf.feature_importances_, index=X_train_transform.columns.to_list())
feature_importances_rf = feature_importances_rf.sort_values(ascending=False)
feature_importances_rf.head(30)