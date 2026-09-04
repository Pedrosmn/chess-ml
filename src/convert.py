import pandas as pd
import json
import re
from pathlib import Path
import argparse

COLUMNS_PGN = {
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
COLUMNS_ACCURACIES = {
    "white":"white_acc", 
    "black":"black_acc"
    }
COLUMNS_WHITE = {
    "result":"white_result", 
    "username":"white_username", 
    "uuid":"white_uuid",
    }
COLUMNS_BLACK = {
    "result":"black_result", 
    "username":"black_username", 
    "uuid":"black_uuid",
    }
GAME_MODES = ["bullet", "blitz", "rapid"]
REMOVE_COLUMNS = ["pgn", "accuracies", "white", "black"]

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
        df["moves"] = df[column].apply(lambda text: None if pd.isna(text) else search_moves(text))

        for tag, new_col in new_columns.items():
            df[new_col] = df[column].apply(lambda text: None if pd.isna(text) else search_pgn(tag, text))
        return df
    
    elif mode == "dict":
        for key, new_col in new_columns.items():
            df[new_col] = df[column].apply(lambda d: None if pd.isna(d) else search_dict(d, key))
        return df

def add_all_columns(df):
    add_columns(df, "pgn", COLUMNS_PGN, mode="pgn")
    add_columns(df, "accuracies", COLUMNS_ACCURACIES, mode="dict")
    add_columns(df, "white", COLUMNS_WHITE, mode="dict")
    add_columns(df, "black", COLUMNS_BLACK, mode="dict")
    return df

def remove_columns(df):
    columns = REMOVE_COLUMNS
    df = df.drop(columns=columns)
    return df

def load_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    if df.empty:
        return None
    return df

def save_parquet(df, filename_prefix, output_dir="../data/raw"):
    output_path = Path(output_dir)

    filepath = output_path / f"{filename_prefix}.parquet"
    df.to_parquet(filepath, index=False)
    return True

def df_to_parquet(df, parquet_path):
    df.to_parquet(parquet_path, index=False)

def convert_dir(dir_names=None):
    if dir_names is None:
        dir_names = GAME_MODES

    for dir_name in dir_names:
        json_dir_path = "../data/json/" + dir_name
        output_dir_path = "../data/raw/" + dir_name
        directory = Path(json_dir_path)

        for file in directory.iterdir():
            path = file._raw_paths
            df = load_json(path[0])
            df = add_all_columns(df)
            df = remove_columns(df)
            save_parquet(df, filename_prefix=file.stem, output_dir=output_dir_path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game-modes", nargs="+", choices=["bullet", "blitz", "rapid"], default=["bullet", "blitz", "rapid"])

    args = parser.parse_args()

    convert_dir(dir_names=args.game_modes)

if __name__ == "__main__":
    main()