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

class FsMoves:

    def __init__(self, board, match, match_qtde=None):
        self.board = board
        self.match = match
        self.match_qtde = match_qtde

    def has_castled(self, move):
        if self.board.ply() >= 2:
            castled = self.match[self.board.ply() - 2]["has_castled"]
        else:
            castled = False

        self.match[self.board.ply()]["has_castled"] = castled or self.board.is_castling(move)

    def has_king_castled(self, move):
        if self.board.ply() >= 2:
            castled = self.match[self.board.ply() - 2]["has_king_castled"]
        else:
            castled = False

        self.match[self.board.ply()]["has_king_castled"] = castled or self.board.is_kingside_castling(move)

    def has_queen_castled(self, move):
        if self.board.ply() >= 2:
            castled = self.match[self.board.ply() - 1]["has_queen_castled"]
        else:
            castled = False

        self.match[self.board.ply()]["has_queen_castled"] = castled or self.board.is_queenside_castling(move)

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

    def has_2_repetition(self):
        if self.board.ply() >= 2:
            repeated = self.match[self.board.ply() - 2]["has_2_repetition"]
        else:
            repeated = False

        self.match[self.board.ply()]["has_2_repetition"] = repeated or self.board.is_repetition(count=2)

    def is_trade(self, move):
        if self.board.is_capture(move) and (self.match[self.board.ply()-1]["is_capture"] == True):
            self.match[self.board.ply()]["is_trade"] = self.board.is_capture(move)
        else:
            self.match[self.board.ply()]["is_trade"] = False

class FsQtde:

    def __init__(self, board, match, match_qtde=None):
        self.board = board
        self.match = match
        self.match_qtde = match_qtde

    def qtde_pieces(self, piece):
        piece_name = chess.piece_name(piece)
        turn = self.board.turn
        print(len(
            self.board.pieces(piece, turn)))

        self.match_qtde[self.board.ply()][f"qtde_{piece_name}"] = len(
            self.board.pieces(piece, turn))

    def diff_piece(self, piece):
        piece_name = chess.piece_name(piece)
        turn = self.board.turn
        opponent = not self.board.turn

        qtde_pieces = len(self.board.pieces(piece, turn))
        qtde_pieces_opponent = len(self.board.pieces(piece, opponent))

        self.match_qtde[self.board.ply()][f"diff_{piece_name}"] = qtde_pieces - qtde_pieces_opponent

    def qtde_move(self, qtde_column, origin_column):
        if self.board.ply() <= 1:
            self.match_qtde[self.board.ply()][f"{qtde_column}"] = int(self.match[self.board.ply()][f"{origin_column}"])
        else:
            past_move = self.match_qtde[self.board.ply()-2][f"{qtde_column}"]
            move_now = self.match[self.board.ply()][f"{origin_column}"]
            self.match_qtde[self.board.ply()][f"{qtde_column}"] = past_move + move_now

class FsOpp:

    def __init__(self, board, match, match_qtde=None, match_opp=None):
        self.board = board
        self.match = match
        self.match_qtde = match_qtde
        self.match_opp = match_opp

    def opp_move(self, opp_column, origin_column):
        if self.board.ply() >= 2:
            toggle = self.match[self.board.ply() - 1][f"{origin_column}"]
        else: 
            toggle = False

        if self.match_qtde:
            self.match_qtde[self.board.ply()][f"{opp_column}"] = toggle 
        else:
            self.match[self.board.ply()][f"{opp_column}"] = toggle 

    def qtde_opp_move(self, qtde_column, origin_column):
        if self.board.ply() < 1:
            self.match_opp[self.board.ply()][f"{qtde_column}"] = 0
        else:
            past_move = self.match_qtde[self.board.ply()-1][f"{origin_column}"]
            self.match_opp[self.board.ply()][f"{qtde_column}"] = past_move


def feature_store(pgn_str):

    pgn = io.StringIO(pgn_str)
    game = chess.pgn.read_game(pgn)
    board = game.board()

    match = []
    fs_moves = FsMoves(board, match)

    for move in game.mainline_moves():
        move_dict = {}
        match.append(move_dict)
        max_moves = game.end().ply()
        piece = board.piece_at(move.from_square)
        turn = board.turn


        match[board.ply()]["fullmove"] = board.fullmove_number
        match[board.ply()]["move"] = move

        # features about de player

        if turn == white:
            match[board.ply()]["turn"] = "white"

        else:
            match[board.ply()]["turn"] = "black"

        # # features about the move turn
        fs_moves.is_capture(move)
        # fs_moves.is_trade(move)
        # fs_moves.move_piece(piece)
        fs_moves.is_irreversible(move)
        # fs_moves.gives_check(move)
        # fs_moves.is_in_check()
        # fs_moves.is_2_repetition()
        # fs_moves.has_2_repetition()

        # # features históricas
        # for p in pieces[:-1]:
        #     fs_moves.qtde_pieces(p)
        #     fs_moves.diff_piece(p)
        # fs_moves.has_castled(move)
        # fs_moves.has_king_castled(move)
        # fs_moves.has_queen_castled(move)

        # features about the opponent
        # fs_moves.opp_has_2_repetition()
        # fs_moves.opp_has_castled(move)
        # fs_moves.opp_has_king_castled(move)
        # fs_moves.opp_has_queen_castled(move)

        board.push(move)

    return match

pgn_str = df_base.iloc[2]["moves"]

features = feature_store(pgn_str)
teste = pd.DataFrame(features)

def feature_store_qtde(pgn_str, match):

    pgn = io.StringIO(pgn_str)
    game = chess.pgn.read_game(pgn)
    board = game.board()

    match_qtde = []
    fs_qtde = FsQtde(board, match, match_qtde)

    for move in game.mainline_moves():
        move_dict = {}
        match_qtde.append(move_dict)
        max_moves = game.end().ply()
        piece = board.piece_at(move.from_square)
        turn = board.turn

        # for p in pieces[:-1]:
        #     fs_qtde.qtde_pieces(p)
        #     fs_qtde.diff_piece(p)

        # fs_qtde.qtde_move("qtde_gives_check", "gives_check")
        # fs_qtde.qtde_move("qtde_is_in_check", "is_in_check")
        fs_qtde.qtde_move("qtde_capture", "is_capture")
        # fs_qtde.qtde_move("qtde_irreversible", "is_irreversible")



        board.push(move)

    return match_qtde

def feature_store_opp(pgn_str, match, match_qtde):

    pgn = io.StringIO(pgn_str)
    game = chess.pgn.read_game(pgn)
    board = game.board()

    match_opp = []
    fs_opp = FsOpp(board, match, match_qtde=match_qtde, match_opp=match_opp)
    fs_opp_qtde = FsOpp(board, match, match_qtde=match_qtde, match_opp=match_opp)

    for move in game.mainline_moves():
        move_dict = {}
        match_opp.append(move_dict)
        max_moves = game.end().ply()
        piece = board.piece_at(move.from_square)
        turn = board.turn

        # fs_opp.opp_move("opp_has_2_repetition", "has_2_repetition")
        # fs_opp.opp_move("opp_has_castled", "has_castled")
        # fs_opp.opp_move("opp_has_queen_castled", "has_queen_castled")
        # fs_opp.opp_move("opp_has_king_castled", "has_king_castled")

        fs_opp_qtde.qtde_opp_move("opp_qtde_capture", "qtde_capture")
        # fs_opp_qtde.qtde_opp_move("opp_qtde_irreversible", "qtde_irreversible")

        board.push(move)

    return match_opp

features_qtde = feature_store_qtde(pgn_str, features)
features_opp = feature_store_opp(pgn_str, features, features_qtde)
teste_qtde = pd.DataFrame(features_qtde)
teste_opp = pd.DataFrame(features_opp)
teste_qtde = pd.concat([teste, teste_qtde, teste_opp], axis=1)
teste_qtde.head(50)

# %%
df_base.iloc[2]
# match

# %%


# print(board.halfmove_clock)
#     número de half-moves desde a última captura ou movimento de peão

# attacks(square: chess.Square) → SquareSet
# is_attacked_by(color: chess.Color, square: chess.Square, occupied: chess.IntoSquareSet | None = None) → bool
# attackers(color: chess.Color, square: chess.Square, occupied: chess.IntoSquareSet | None = None) → SquareSet
# print(board.is_pinned(True, square))

