"""
This class is responsible for storing all of the info about the current state of a chess game. It will also be responsible for determining the valid moves at the current state. It will also keep a move log.
"""
import logging as log
from src.move_validation import validate_pawn
from src.constants import Square, Player, PieceType

class Move:
    # maps keys to values;
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.valid = True  # init validitiy as True (maybe switch to false later?)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    def getChessNotation(self):
        # not really a chess notation because there's a lot more logic going into it, which doesn't matter at this point
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(
            self.endRow, self.endCol
        )

class GameState:
    """
    The board is represented by a two dimentional list of lists(8x8). Each list represents a row on a chessboard.
    Each element is an enum value from the Square enum representing the piece and its color.
    """
    def __init__(self):
        self.board = [
            [Square.bR, Square.bN, Square.bB, Square.bQ, 
             Square.bK, Square.bB, Square.bN, Square.bR],
            [Square.bp] * 8,
            [Square.EMPTY] * 8,
            [Square.EMPTY] * 8,
            [Square.EMPTY] * 8,
            [Square.EMPTY] * 8,
            [Square.wp] * 8,
            [Square.wR, Square.wN, Square.wB, Square.wQ, 
             Square.wK, Square.wB, Square.wN, Square.wR],
        ]
        self.whiteToMove = True
        self.moveLog = []

    def checkMoveValidity(self, move: Move):
        """
        Takes Move as parameter and determines if it's valid
        """
        piece_color = Square(move.pieceMoved)[0]  # Get the first character (player color)
        piece_type = Square(move.pieceMoved)[1]   # Get the second character (piece type)
        
        # First check if it's the correct player's turn
        if (self.whiteToMove and piece_color != Player.WHITE) or (not self.whiteToMove and piece_color != Player.BLACK):
            move.valid = False
            return

        if piece_type == PieceType.PAWN:
            validate_pawn(move)
        elif piece_type == PieceType.ROOK:
            print("found a rook!")
        elif piece_type == PieceType.KNIGHT:
            print("found a Knight!")
        elif piece_type == PieceType.BISHOP:
            print("found a Bishop!")
        elif piece_type == PieceType.QUEEN:
            print("found a Queen!")
        elif piece_type == PieceType.KING:
            print("found a King!")

    def swap_players(self):
        """
        Swaps the players
        """
        self.whiteToMove = not self.whiteToMove
        log.debug(f"swapped players: {self.whiteToMove}")

    def makeMove(self, move):
        """
        Takes a Move as a parameter and executes it (this will not work for castling, pawn promotion and en-passant)
        """
        if move.pieceMoved != Square.EMPTY:
            self.board[move.startRow][move.startCol] = Square.EMPTY
            self.board[move.endRow][move.endCol] = move.pieceMoved
            self.moveLog.append(move)  # log the move so we can undo it later
            self.swap_players()
            log.info(f"move: {move.pieceMoved} -> {move.pieceCaptured}")
    
    def undoMove(self):
        """
        Undo the last move made
        """
        if len(self.moveLog) != 0:  # make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.swap_players()


