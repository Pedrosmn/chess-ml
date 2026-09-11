# %%

import pandas as pd
import chess.pgn
import sqlalchemy
import io

con = sqlalchemy.create_engine("sqlite:///../data/db/database.db")

# %%



# %%

df_base = pd.read_sql("matches", con)
df_base

# %%
df = pd.DataFrame(columns=["uuid", "white_move", "black_move"])
df["uuid"] = df_base["uuid"]
df

# Fazer uma lista de dicionários, cada dicinoário sendo as features do lance. e no fim adicionar tudo no df

# %%

pgn = df_base.iloc[49]["moves"]
pgn = io.StringIO(pgn)

game = chess.pgn.read_game(pgn)
board = game.board()

for move in game.mainline_moves():
    # print(board.halfmove_clock)
        # número de half-moves desde a última captura ou movimento de peão
    # print(board.promoted)
    # print(board.is_check())
    # print(board.gives_check(move))
    # print(board.can_claim_draw())
        # verica se o lance pode causar um empate por retetição - talvez leakeage
    # print(board.is_repetition(count=2))
        # repetiu duas vezes?
    # print(board.is_capture(move))
    # print(board.is_zeroing(move))
    #     captura ou lance de peão
    # print(board.is_irreversible(move))
    #     pawn moves, captures, moves that destroy castling rights and moves that cede en passant are irreversible
    # print(board.is_castling(move))
    # print(board.is_kingside_castling(move))
    # print(board.is_queenside_castling(move))

    # branco
    # print(board.has_castling_rights(True))
    # print(board.has_kingside_castling_rights(True))
    # print(board.has_queenside_castling_rights(True))

    # preto
    # print(board.has_castling_rights(False))
    # print(board.has_kingside_castling_rights(False))
    # print(board.has_queenside_castling_rights(False))

    # baseboard

    # attacks(square: chess.Square) → SquareSet
    # is_attacked_by(color: chess.Color, square: chess.Square, occupied: chess.IntoSquareSet | None = None) → bool
    # attackers(color: chess.Color, square: chess.Square, occupied: chess.IntoSquareSet | None = None) → SquareSet

    #qtd peças brancas
    # print(len(board.pieces(color=True, piece_type=chess.PAWN)))
    # print(len(board.pieces(color=True, piece_type=chess.KNIGHT)))
    # print(len(board.pieces(color=True, piece_type=chess.BISHOP)))
    # print(len(board.pieces(color=True, piece_type=chess.ROOK)))
    # print(len(board.pieces(color=True, piece_type=chess.QUEEN)))

    #qtd peças pretas
    # print(len(board.pieces(color=False, piece_type=chess.PAWN)))
    # print(len(board.pieces(color=False, piece_type=chess.KNIGHT)))
    # print(len(board.pieces(color=False, piece_type=chess.BISHOP)))
    # print(len(board.pieces(color=False, piece_type=chess.ROOK)))
    # print(len(board.pieces(color=False, piece_type=chess.QUEEN)))


    # for square in chess.SQUARES:
    #     print(board.is_pinned(True, square))
    print(move)
    board.push(move)
    break

# %%
print(game.end().ply())
