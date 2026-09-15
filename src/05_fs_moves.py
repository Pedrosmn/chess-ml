# %%

import pandas as pd
import chess.pgn
import sqlalchemy
import io

con = sqlalchemy.create_engine("sqlite:///../data/db/database.db")

pieces = chess.PIECE_TYPES
white = chess.WHITE
black = chess.BLACK
# %%
df_base = pd.read_sql("matches", con)
df_base

# %%

class FSMoves:

    def __init__(self, board, match):
        self.board = board
        self.match = match
        
    def qtde_pieces(self, piece):
        piece_name = chess.piece_name(piece)
        turn = self.board.turn
        print(len(
            self.board.pieces(piece, turn)))

        self.match[self.board.ply()][f"qtde_{piece_name}"] = len(
            self.board.pieces(piece, turn))

    def diff_piece(self, piece):
        piece_name = chess.piece_name(piece)
        turn = self.board.turn
        opponent = not self.board.turn

        qtde_pieces = len(self.board.pieces(piece, turn))
        qtde_pieces_opponent = len(self.board.pieces(piece, opponent))

        self.match[self.board.ply()][f"diff_{piece_name}"] = qtde_pieces - qtde_pieces_opponent

    def has_castled(self, move):
        if self.board.ply() >= 2:
            castled = self.match[self.board.ply() - 2]["has_castled"]
        else:
            castled = False

        self.match[self.board.ply()]["has_castled"] = castled or self.board.is_castling(move)

    def is_capture(self, move):
        self.match[self.board.ply()]["is_capture"] = self.board.is_capture(move)

    def move_piece(self, piece):
        self.match[self.board.ply()]["move_piece"] = chess.piece_name(piece.piece_type)

    def is_irreversible(self, move):
        self.match[self.board.ply()]["is_irreversible"] = self.board.is_irreversible(move)

    def is_in_check(self):
        self.match[self.board.ply()]["is_in_check"] = self.board.is_check()

    def gives_check(self, move):
        self.match[self.board.ply()]["gives_check"] = self.board.gives_check(move)

    def is_2_repetition(self):
        self.match[self.board.ply()]["is_2_repetition"] = self.board.is_repetition(count=2)

    def is_trade(self, move):
        if self.board.is_capture(move) and (self.match[self.board.ply()-1]["is_capture"] == True):
            self.match[self.board.ply()]["is_trade"] = self.board.is_capture(move)
        else:
            self.match[self.board.ply()]["is_trade"] = False


def feature_store(pgn_str):

    pgn = io.StringIO(pgn_str)
    game = chess.pgn.read_game(pgn)
    board = game.board()

    match = []
    fs_moves = FSMoves(board, match)

    for move in game.mainline_moves():
        move_dict = {}
        match.append(move_dict)
        piece = board.piece_at(move.from_square)
        turn = board.turn

        match[board.ply()]["move"] = move

        # features about de player

        if turn == white:
            match[board.ply()]["turn"] = "white"

        else:
            match[board.ply()]["turn"] = "black"

        # features about the move
        fs_moves.is_capture(move)
        fs_moves.is_trade(move)
        fs_moves.move_piece(piece)
        fs_moves.is_irreversible(move)
        fs_moves.is_in_check()
        fs_moves.gives_check(move)
        fs_moves.is_2_repetition()

        # features históricas
        for p in pieces[:-1]:
            fs_moves.qtde_pieces(p)
            fs_moves.diff_piece(p)
        fs_moves.has_castled(move)

        board.push(move)

    return match



pgn_str = df_base.iloc[6]["moves"]

features = feature_store(pgn_str)

teste = pd.DataFrame(features)
teste.head(30)

# %%
df_base.iloc[6]
# match

# %%


# print(board.halfmove_clock)
#     número de half-moves desde a última captura ou movimento de peão

# attacks(square: chess.Square) → SquareSet
# is_attacked_by(color: chess.Color, square: chess.Square, occupied: chess.IntoSquareSet | None = None) → bool
# attackers(color: chess.Color, square: chess.Square, occupied: chess.IntoSquareSet | None = None) → SquareSet
# print(board.is_pinned(True, square))

