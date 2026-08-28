import argparse
import dotenv
from chess_collector import get_leaderboard_players, get_leaderboard_games

def main():
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--top-n", default=50, type=int, help="number of top-ranked players (max=50)")
    parser.add_argument("--time-class", nargs="+", choices=["rapid", "bullet", "blitz"], default=["rapid", "bullet", "blitz"])
    parser.add_argument("--qtde-matches", default=250, type=int)

    args = parser.parse_args()

    players = get_leaderboard_players(top_n=args.top_n, time_classes=args.time_class)
    get_leaderboard_games(players, qtde_matches=args.qtde_matches, time_classes=args.time_class)

if __name__ == "__main__":
    main()