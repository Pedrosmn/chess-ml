# %%

import pandas as pd
import json
import re

"""criar colunas a partir do "pgn":
    Event
    Date
    Round
    White
    Black
    Result
    CurrentPosition
    ECO
    ECOUrl
    WhiteElo
    BlackElo
    Termination
    StartTime

A partir do "accuracies:
    WhiteAcc
    BlackAcc
    Remover accuracies

A partir do "white":
"WhiteResult",
"WhiteUsername",
"WhiteUuid",

A partir do "black":
"BlackResult",
"BlackUsername",
"BlackUuid",
    """

# %%
df = pd.read_parquet("../data/processed/rapid/1stSecond_2026-05-26_16-30-35.parquet")
df.head()

# %%

# PGN
# FAZER FUNÇÃO PARA GENERALIZAR PARA AS OUTRAS COLUNAS
df_test = df.copy()
df_test

pd.set_option("display.max_columns", None)


def search_pgn(cat, text):
    match = re.search(rf'\[{cat} "([^"]+)"\]', text)
    return match.group(1) if match else None

def search_moves(text):
    match = re.search(r'\d+\.\s', text)
    return text[match.start():] if match else None

def search_dict(data, key):
    return data.get(key) if data else None

def add_columns(df, column, new_columns, mode="pgn"):
    if mode == "pgn":
        df["moves"] = df[column].apply(search_moves)
        for tag, new_col in new_columns.items():
            df[new_col] = df[column].apply(lambda text: search_pgn(tag, text))
    elif mode == "dict":
        for key, new_col in new_columns.items():
            df[new_col] = df[column].apply(lambda d: search_dict(d, key))

def add_all_columns(df):
    new_columns_pgn = {
        "Event":"event", 
        "Date":"date", 
        "Round":"round", 
        "Result":"result", 
        "CurrentPosition":"current_position", 
        "ECO":"eco", 
        "ECOUrl":"ecu_url", 
        "WhiteElo":"white_elo", 
        "BlackElo":"black_elo", 
        "Termination":"termination", 
        "StartTime":"start_time",
        }
    new_columns_accuracies = {
        "white":"white_acc", 
        "black":"black_acc"
        }
    new_columns_white = {
        "result":"white_result", 
        "username":"white_username", 
        "uuid":"white_uuid",
        }
    new_columns_black = {
        "result":"black_result", 
        "username":"black_username", 
        "uuid":"black_uuid",
        }

    add_columns(df, "pgn", new_columns_pgn, mode="pgn")
    add_columns(df, "accuracies", new_columns_accuracies, mode="dict")
    add_columns(df, "white", new_columns_white, mode="dict")
    add_columns(df, "black", new_columns_black, mode="dict")
    
    return df

def remove_columns(df):
    columns = ["pgn", "accuracies", "white", "black"]
    df = df.drop(columns=columns)
    return df

def json_to_parquet(json_path, parquet_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    if df.empty:
        print(f"Aviso: dados vazios em {json_path}, parquet não gerado.")
        return False

    df.to_parquet(parquet_path, index=False)
    print(f"Dados convertidos com sucesso em: {parquet_path}")
    return True

df_test = add_all_columns(df_test)
df_test = remove_columns(df_test)
df_test.head()

# %%
for c in new_columns_accuracies:
    print(new_columns_accuracies.get(c))


# %%
# df_test["Date"] = search_pgn("Date", text)
df_test.head(10)

# %%

print((df_test.loc[1, "pgn"]))

# %%

"WhiteAcc",
"BlackAcc"

"WhiteResult",
"WhiteUsername",
"WhiteUuid",

"BlackResult",
"BlackUsername",
"BlackUuid",



# %%

def add_columns(df):
