import requests
import os
import dotenv
import datetime
import json
import time
from pathlib import Path
import argparse

dotenv.load_dotenv()

def def_headers(headers):
    return headers or {"User-Agent": os.getenv("USER_AGENT")}

class ChessComCollector:
    def __init__(self, player, headers=None):
        self.player = player
        self.headers = def_headers(headers)

    def get_archive(self):
        url = f"https://api.chess.com/pub/player/{self.player}/games/archives"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code != 200:
            print(f"ERRO ao acessar archives: {resp.status_code}")
            return None
        return resp.json().get("archives", [])

    def fetch_month_games(self, archive_url):
        resp = requests.get(archive_url, headers=self.headers)
        if resp.status_code != 200:
            print(f"ERRO ao acessar o mês: {resp.status_code}")
            return []
        return resp.json().get("games", [])

    def filter_games_by_time_class(self, games, time_class):
        return [g for g in games if g.get("time_class") == time_class]

    def get_matches(self, archive, qtde_matches, time_class):
        collected_matches = []
        for archive_url in reversed(archive):
            games = self.fetch_month_games(archive_url)
            collected_matches.extend(self.filter_games_by_time_class(games, time_class))
            if len(collected_matches) >= qtde_matches:
                collected_matches = collected_matches[:qtde_matches]
                break
            time.sleep(1)
        print(f"Busca finalizada. Encontradas: {len(collected_matches)}.\n")
        return collected_matches

    @staticmethod
    def save_json(data, filename_prefix, output_dir="../data/json"):
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = Path(output_dir)

        filepath = output_path / f"{filename_prefix}_{now}.json"
        with open(filepath, 'w', encoding="utf-8") as open_file:
            json.dump(data, open_file, indent=4, ensure_ascii=False)
        return filepath 

def get_leaderboard_games(leaderboard_players,
                            qtde_matches=200,
                            headers=None,
                            time_classes=("bullet", "rapid", "blitz")):
    headers = def_headers(headers)
    for time_class in time_classes:
        players = leaderboard_players[time_class]

        for i, player in enumerate(players):
            print(f"{i} - Iniciando coleta de {time_class.upper()} para: {player}")

            collector = ChessComCollector(player=player, headers=headers)

            archive = collector.get_archive()
            if not archive:
                print(f"Sem archive para {player}, pulando.")
                continue

            partidas = collector.get_matches(archive=archive, qtde_matches=qtde_matches, time_class=time_class)

            if partidas:
                collector.save_json(partidas, filename_prefix=f"{time_class}/{player}")

            time.sleep(1)
    
    return True

def get_leaderboard_players(headers=None, 
                            top_n=50, 
                            time_classes=("bullet", "rapid", "blitz")):
    headers = def_headers(headers)
    url = "https://api.chess.com/pub/leaderboards"
    resp = requests.get(url, headers=headers or {})

    if resp.status_code != 200:
        print(f"ERRO ao acessar leaderboards: {resp.status_code}")
        return {}

    data = resp.json()

    leaderboard_keys = {
        "bullet": "live_bullet",
        "rapid": "live_rapid",
        "blitz": "live_blitz",
    }

    players = {}
    for time_class in time_classes:
        api_key = leaderboard_keys.get(time_class)
        if api_key is None:
            print(f"Aviso: time_class '{time_class}' não reconhecido, pulando.")
            continue

        players[time_class] = [p["username"] for p in data[api_key][:top_n]]

    return players

def main():
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--top_n", default=50, type=int, help="number of top-ranked players (max=50) (default=50)")
    parser.add_argument("--time_class", nargs="+", choices=["bullet", "blitz", "rapid"], default=["bullet", "blitz", "rapid"])
    parser.add_argument("--qtde_matches", default=200, type=int)

    args = parser.parse_args()

    players = get_leaderboard_players(top_n=args.top_n, time_classes=args.time_class)
    get_leaderboard_games(players, qtde_matches=args.qtde_matches, time_classes=args.time_class)

if __name__ == "__main__":
    main()
