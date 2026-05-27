# %%

import requests
import os
from dotenv import load_dotenv # type: ignore # type: 
import datetime
import json
import time
from pathlib import Path
import pandas as pd

load_dotenv()

headers = {
    "User-Agent": os.getenv("USER_AGENT")
}

# %%

# Salvar partidas em JSON

def save_data(data, filename_prefix="matches"):
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = f"../data/raw/{filename_prefix}_{now}.json"
    
    with open(filepath, 'w') as open_file:
        json.dump(data, open_file, indent=4)
    print(f"Dados salvos com sucesso em: {filepath}")

# %%

'''
Coletar partidas das mais novas para as mais antigas, de acordo com o:
Player
Modalidade ex.: bullet, blitz
Quatidade de partidas
'''

def get_matches(player, qtde_matches, time_class="bullet"):
    archives_url = f"https://api.chess.com/pub/player/{player}/games/archives"
    resp_archives = requests.get(archives_url, headers=headers)
    
    if resp_archives.status_code != 200:
        print(f"ERRO ao acessar archives: {resp_archives.status_code}")
        return None
        
    archives = resp_archives.json().get("archives", [])
    collected_matches = []
    
    for archive_url in reversed(archives):
        print(f"Buscando partidas do mês: {archive_url.split('/')[-2]}/{archive_url.split('/')[-1]}...")
        
        resp_games = requests.get(archive_url, headers=headers)
        
        if resp_games.status_code != 200:
            print(f"ERRO ao acessar o mês: {resp_games.status_code}")
            time.sleep(1) 
            continue 
            
        games = resp_games.json().get("games", [])
        
        for game in games:
            if game.get("time_class") == time_class:
                collected_matches.append(game)
                
                if len(collected_matches) == qtde_matches:
                    print(f"\nMeta de {qtde_matches} partidas '{time_class}' alcançada!")
                    return collected_matches
        
        time.sleep(1)
                    
    print(f"\nBusca finalizada. Encontradas: {len(collected_matches)}.")
    return collected_matches

# %%

def json_to_parquet(json_path, parquet_path, cols_to_drop=None):
    """
    Lê um arquivo JSON genérico, remove colunas indesejadas e salva em Parquet.
    """
    if cols_to_drop is None:
        cols_to_drop = []

    # Carrega o arquivo JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    if df.empty:
        return False

    # Remove as colunas especificadas (ignora se a coluna não existir)
    df = df.drop(columns=cols_to_drop, errors='ignore')

    df.to_parquet(parquet_path, index=False)
    
    return True
# %%
