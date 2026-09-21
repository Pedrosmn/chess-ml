# %%

import pandas as pd
import chess.pgn
import sqlalchemy
import io

con = sqlalchemy.create_engine("sqlite:///../data/db/database.db")

pieces = chess.PIECE_TYPES
white = chess.WHITE
black = chess.BLACK
df_base = pd.read_sql("matches", con)
df_base

# %%

class GameContext:

    def __init__(self, board, ply, move, piece, match, game, match_qtde=None, match_opp=None):
        self.board = board
        self.ply = ply
        self.move = move
        self.piece = piece
        self.match = match
        self.game = game
        self.match_qtde = match_qtde
        self.match_opp = match_opp

class FsMove:

    def __init__(self, game_context):
        self.board = game_context.board
        self.match = game_context.match
        self.game = game_context.game
        self.move = game_context.move
        self.piece = game_context.piece
        self.match_qtde = game_context.match_qtde

    def fullmove_count(self):
        self.match[self.board.ply()]["fullmove_count"] = self.board.fullmove_number

    def move_not(self):
        self.match[self.board.ply()]["move"] = self.move

    def time_control(self):
        self.match[self.board.ply()]["time_control"] = self.game.headers["TimeControl"]

    def turn(self):
        turn_color = self.board.turn
        if turn_color:
            self.match[self.board.ply()]["turn"] = "white"
        else:
            self.match[self.board.ply()]["turn"] = "black"

    def elo_diff(self):
        turn_color = self.board.turn
        if turn_color:
            self.match[self.board.ply()]["elo_diff"] = int(self.game.headers["WhiteElo"]) - int(self.game.headers["BlackElo"])
        else:
            self.match[self.board.ply()]["elo_diff"] = int(self.game.headers["BlackElo"]) - int(self.game.headers["WhiteElo"])

    def is_capture(self):
        self.match[self.board.ply()]["is_capture"] = self.board.is_capture(self.move)

    def move_piece(self):
        self.match[self.board.ply()]["move_piece"] = chess.piece_name(self.piece.piece_type)

    def is_irreversible(self):
        self.match[self.board.ply()]["is_irreversible"] = self.board.is_irreversible(self.move)

    def is_in_check(self):
        self.match[self.board.ply()]["is_in_check"] = self.board.is_check()

    def gives_check(self):
        self.match[self.board.ply()]["gives_check"] = self.board.gives_check(self.move)

    def is_2_repetition(self):
        self.match[self.board.ply()]["is_2_repetition"] = self.board.is_repetition(count=2)

    def has_2_repetition(self):
        if self.board.ply() >= 2:
            repeated = self.match[self.board.ply() - 2]["has_2_repetition"]
        else:
            repeated = False

        self.match[self.board.ply()]["has_2_repetition"] = repeated or self.board.is_repetition(count=2)

    def has_promotion(self):
        if self.board.ply() >= 2:
            promotion = self.match[self.board.ply() - 2]["has_promotion"]
        else:
            promotion = False

        self.match[self.board.ply()]["has_promotion"] = promotion or bool(self.move.promotion)

    def is_trade(self):
        if self.board.is_capture(self.move) and (self.match[self.board.ply()-1]["is_capture"] == True):
            self.match[self.board.ply()]["is_trade"] = self.board.is_capture(self.move)
        else:
            self.match[self.board.ply()]["is_trade"] = False

    def has_castled(self):
        if self.board.ply() >= 2:
            castled = self.match[self.board.ply() - 2]["has_castled"]
        else:
            castled = False

        self.match[self.board.ply()]["has_castled"] = castled or self.board.is_castling(self.move)

    def has_king_castled(self):
        if self.board.ply() >= 2:
            castled = self.match[self.board.ply() - 2]["has_king_castled"]
        else:
            castled = False

        self.match[self.board.ply()]["has_king_castled"] = castled or self.board.is_kingside_castling(self.move)

    def has_queen_castled(self):
        if self.board.ply() >= 2:
            castled = self.match[self.board.ply() - 2]["has_queen_castled"]
        else:
            castled = False

        self.match[self.board.ply()]["has_queen_castled"] = castled or self.board.is_queenside_castling(self.move)


class FsQtde:

    def __init__(self, game_context):
        self.board = game_context.board
        self.match = game_context.match
        self.move = game_context.move
        self.piece = game_context.piece
        self.match_qtde = game_context.match_qtde
        self.match_opp = game_context.match_opp

    def qtde_pieces(self):
        for p in pieces:
            piece_name = chess.piece_name(p)
            turn_color = self.board.turn

            self.match_qtde[self.board.ply()][f"qtde_{piece_name}"] = len(
                self.board.pieces(p, turn_color))

    def diff_piece(self):
        for p in pieces:
            piece_name = chess.piece_name(p)
            turn_color = self.board.turn
            opponent = not self.board.turn

            qtde_pieces = len(self.board.pieces(p, turn_color))
            qtde_pieces_opponent = len(self.board.pieces(p, opponent))

            self.match_qtde[self.board.ply()][f"diff_{piece_name}"] = qtde_pieces - qtde_pieces_opponent

    def qtde_move(self, qtde_column, origin_column):
        if self.board.ply() <= 1:
            self.match_qtde[self.board.ply()][f"{qtde_column}"] = int(self.match[self.board.ply()][f"{origin_column}"])
        else:
            past_move = self.match_qtde[self.board.ply()-2][f"{qtde_column}"]
            move_now = self.match[self.board.ply()][f"{origin_column}"]
            self.match_qtde[self.board.ply()][f"{qtde_column}"] = past_move + move_now

    def recency(self, recency_column, origin_column):
        if self.board.ply() <= 2:
            self.match_qtde[self.board.ply()][f"{recency_column}"] = 0

        if (self.match[self.board.ply()][f"{origin_column}"]) and (self.board.ply() >= 2):
            self.match_qtde[self.board.ply()][f"{recency_column}"] = 0

        elif (not self.match[self.board.ply()][f"{origin_column}"]) and (self.board.ply() >= 2):
            self.match_qtde[self.board.ply()][f"{recency_column}"] = self.match_qtde[self.board.ply() - 2][f"{recency_column}"] + 2

    def recency_piece(self):

        for p in pieces:
            piece_name = chess.piece_name(p)
            if self.board.ply() < 2:
                self.match_qtde[self.board.ply()][f"recency_{piece_name}_move"] = 0

            elif (self.match[self.board.ply()][f"move_piece"] == f"{piece_name}") and (self.board.ply() >= 2):
                self.match_qtde[self.board.ply()][f"recency_{piece_name}_move"] = 0

            elif (self.match[self.board.ply()][f"move_piece"] != f"{piece_name}") and (self.board.ply() >= 2):
                self.match_qtde[self.board.ply()][f"recency_{piece_name}_move"] = self.match_qtde[self.board.ply() - 2][f"recency_{piece_name}_move"] + 2


class FsOpp:

    def __init__(self, game_context):
        self.board = game_context.board
        self.match = game_context.match
        self.move = game_context.move
        self.piece = game_context.piece
        self.match_qtde = game_context.match_qtde
        self.match_opp = game_context.match_opp

    def opp_move(self, opp_column, origin_column):
        if self.board.ply() >= 2:
            toggle = self.match[self.board.ply() - 1][f"{origin_column}"]
        else: 
            toggle = False

        self.match_qtde[self.board.ply()][f"{opp_column}"] = toggle 

    def qtde_opp_move(self, qtde_column, origin_column):
        if self.board.ply() < 1:
            self.match_opp[self.board.ply()][f"{qtde_column}"] = 0
        else:
            past_move = self.match_qtde[self.board.ply()-1][f"{origin_column}"]
            self.match_opp[self.board.ply()][f"{qtde_column}"] = past_move

    def opp_recency(self, recency_column, origin_column):
            if self.board.ply() <= 1:
                self.match_opp[self.board.ply()][recency_column] = 0
            else:
                past_move = self.match_qtde[self.board.ply()-1][origin_column]
                self.match_opp[self.board.ply()][recency_column] = past_move

    def opp_recency_piece(self):
        for p in pieces:
            piece_name = chess.piece_name(p)

            if self.board.ply() < 1:
                self.match_opp[self.board.ply()][f"opp_recency_{piece_name}_piece"] = 0
            else:
                past_move = self.match_qtde[self.board.ply()-1][f"recency_{piece_name}_move"]
                self.match_opp[self.board.ply()][f"opp_recency_{piece_name}_piece"] = past_move

def pipeline_fs(pgn_str):
    pgn = io.StringIO(pgn_str)
    game = chess.pgn.read_game(pgn)
    board = game.board()

    match = []
    match_qtde = []
    match_opp = []

    for move in game.mainline_moves():
        match.append({})
        match_qtde.append({})
        match_opp.append({})
        piece = board.piece_at(move.from_square)

        game_context = GameContext(board=board, ply=board.ply(), move=move, piece=piece, match=match, game=game, match_qtde=match_qtde, match_opp=match_opp)
        fs_moves = FsMove(game_context)
        fs_qtde = FsQtde(game_context)
        fs_opp = FsOpp(game_context)

        # features headers
        fs_moves.fullmove_count()
        fs_moves.move_not()
        fs_moves.time_control()
        fs_moves.turn()
        fs_moves.elo_diff()

        # features about the move turn
        fs_moves.move_piece()
        fs_moves.is_capture()
        fs_moves.is_irreversible()
        fs_moves.is_in_check()
        fs_moves.gives_check()
        fs_moves.is_2_repetition()
        fs_moves.has_2_repetition()
        fs_moves.has_promotion()
        fs_moves.is_trade()
        fs_moves.has_castled()
        fs_moves.has_king_castled()
        fs_moves.has_queen_castled()

        # features about opponent
        fs_opp.opp_move("opp_has_2_repetition", "has_2_repetition")
        fs_opp.opp_move("opp_has_promotion", "has_promotion")
        fs_opp.opp_move("opp_has_castled", "has_castled")
        fs_opp.opp_move("opp_has_queen_castled", "has_queen_castled")
        fs_opp.opp_move("opp_has_king_castled", "has_king_castled")
        fs_opp.qtde_opp_move("opp_qtde_capture", "qtde_capture")
        fs_opp.qtde_opp_move("opp_qtde_irreversible", "qtde_irreversible")

        # features about the move turn Qtde
        fs_qtde.qtde_pieces()
        fs_qtde.diff_piece()
        fs_qtde.qtde_move("qtde_gives_check", "gives_check")
        fs_qtde.qtde_move("qtde_is_in_check", "is_in_check")
        fs_qtde.qtde_move("qtde_capture", "is_capture")
        fs_qtde.qtde_move("qtde_irreversible", "is_irreversible")

        # features about recency
        fs_qtde.recency("recency_capture", "is_capture")
        fs_qtde.recency("recency_in_check", "is_in_check")
        fs_qtde.recency("recency_gives_check", "gives_check")
        fs_qtde.recency("recency_is_irreversible", "is_irreversible")
        fs_qtde.recency_piece()

        # features about recency opponent
        fs_opp.opp_recency_piece()
        fs_opp.opp_recency("opp_recency_capture", "recency_capture")
        fs_opp.opp_recency("opp_recency_in_check", "recency_in_check")
        fs_opp.opp_recency("opp_recency_gives_check", "recency_gives_check")
        fs_opp.opp_recency("opp_recency_is_irreversible", "recency_is_irreversible")

        board.push(move)

    return match, match_qtde, match_opp


pgn_str = df_base.iloc[202]["pgn"]
match, match_qtde, match_opp = pipeline_fs(pgn_str)
match_df = pd.DataFrame(match)
match_qtde_df = pd.DataFrame(match_qtde)
match_opp_df = pd.DataFrame(match_opp)

teste = pd.concat([match_df, match_qtde_df, match_opp_df], axis=1)
teste.tail(30)
# %%
df_base.iloc[7]
# match


# %%
t = pd.read_parquet("/home/pedro/documents/Estudos/chess-ml/data/raw/blitz/Andreikka_2026-09-04_10-46-30.parquet")
t