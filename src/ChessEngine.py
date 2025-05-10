"""
This class is responsible for storing all of the info about the current state of a chess game. It will also be responsible for determining the valid moves at the current state. It will also keep a move log.
"""
import logging as log


class GameState:
    """
    The board is represented by a two dimentional list of lists(8x8). Each list is going to represent a row on a chessboard.
    Each element of the list has 2 characters.
    First character represents color of the piece, 'b' or 'w'
    Second character represents the piece type, 'K', 'Q', 'N', 'B' or 'p'
    We'll be looking at it from whites perspective.
    If we wanted to be more efficient we could use numpy.
    """

    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]

        self.whiteToMove = True
        self.moveLog = []

    """
    Takes Move as parameter and determines if it's valid
    """

    def checkMoveValidity(self, move):

        # Definitely needs to be rewritten more elegantly
        if move.pieceMoved[0] == "w":
            if move.pieceMoved[1] == "p":
                print("found a pawn!")
                if move.pieceCaptured == "--" and (((move.startRow, move.startCol) == (move.endRow + 1, move.endCol)) or 
                                                   ((move.startRow, move.startCol) == (move.endRow + 2, move.endCol))):
                    move.valid = True

                elif move.pieceCaptured != "--" and (((move.startRow, move.startCol) == (move.endRow + 1, move.endCol - 1)) or 
                                                   ((move.startRow, move.startCol) == (move.endRow + 1, move.endCol + 1))):
                    move.valid = True
                else:
                    move.valid = False

            elif move.pieceMoved[1] == "R":
                print("found a rook!")

            elif move.pieceMoved[1] == "N":
                print("found a Knight!")

            elif move.pieceMoved[1] == "B":
                print("found a Bishop!")

            elif move.pieceMoved[1] == "Q":
                print("found a Queen!")

            elif move.pieceMoved[1] == "K":
                print("found a King!")

        elif move.pieceMoved[0] == "b":
            if move.pieceMoved[1] == "p":
                print("found a pawn!")
                if move.pieceCaptured == "--" and (move.startRow, move.startCol) == (
                    move.endRow - 1,
                    move.endCol,
                ):
                    move.valid = True
                else:
                    move.valid = False

            elif move.pieceMoved[1] == "R":
                print("found a rook!")

            elif move.pieceMoved[1] == "N":
                print("found a Knight!")

            elif move.pieceMoved[1] == "B":
                print("found a Bishop!")

            elif move.pieceMoved[1] == "Q":
                print("found a Queen!")

            elif move.pieceMoved[1] == "K":
                print("found a King!")

    """
    Takes a Move as a parameter and executes it (this will not work for castling, pawn promotion and en-passant)
    """

    def makeMove(self, move):
        if move.pieceMoved != "--":
            self.board[move.startRow][move.startCol] = "--"
            self.board[move.endRow][move.endCol] = move.pieceMoved
            self.moveLog.append(move)  # log the move so we can undo it later
            self.whiteToMove = not self.whiteToMove  # swap players
            log.info(f"move: {move.pieceMoved} -> {move.pieceCaptured}")

    """
    Undo the last move made
    """

    def undoMove(self):
        if len(self.moveLog) != 0:  # make sure there is a move to undo
            move = (
                self.moveLog.pop()
            )  # removes last element from the list, and assigns it to the move variable
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch turns back


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

    def getChessNotation(self):
        # not really a chess notation because there's a lot more logic going into it, which doesn't matter at this point
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(
            self.endRow, self.endCol
        )

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
