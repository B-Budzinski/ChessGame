"""
Classes representing chess moves and their properties.
"""
from src.constants import BoardPositions, Square

class RookMove:
    def __init__(self, startRow: int = None, startCol: int = None, endRow: int = None, endCol: int = None):
        self.startRow = startRow
        self.startCol = startCol
        self.endRow = endRow
        self.endCol = endCol

class Move:
    # maps keys to values using BoardPositions enum
    ranksToRows = {
        "1": BoardPositions.FIRST_RANK,
        "2": BoardPositions.SECOND_RANK,
        "3": BoardPositions.THIRD_RANK,
        "4": BoardPositions.FOURTH_RANK,
        "5": BoardPositions.FIFTH_RANK,
        "6": BoardPositions.SIXTH_RANK,
        "7": BoardPositions.SEVENTH_RANK,
        "8": BoardPositions.EIGHTH_RANK
    }
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {
        "a": BoardPositions.FIRST_FILE,
        "b": BoardPositions.SECOND_FILE,
        "c": BoardPositions.THIRD_FILE,
        "d": BoardPositions.FOURTH_FILE,
        "e": BoardPositions.FIFTH_FILE,
        "f": BoardPositions.SIXTH_FILE,
        "g": BoardPositions.SEVENTH_FILE,
        "h": BoardPositions.EIGHTH_FILE
    }
    colsToFiles = {v: k for k, v in filesToCols.items()}
    
    def __init__(self, startSq: tuple[int, int], endSq: tuple[int, int], gameState):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.gameState = gameState
        self.board = gameState.board
        self.pieceMoved = gameState.board[self.startRow][self.startCol]
        self.pieceCaptured = gameState.board[self.endRow][self.endCol]
        self.valid = True
        
        # Special move flags
        self.isCastling = False
        self.isEnPassant = False
        self.isPawnPromotion = False
        
        # For castling - store rook move
        self.rookMove = RookMove()
        
        # For en passant - store captured pawn position
        self.enPassantCaptureRow: int = None
        self.enPassantCaptureCol: int = None
        
        # For pawn promotion - store promoted piece
        self.promotedPiece: Square = None

    def getRankFile(self, r: int, c: int) -> str:
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    def getChessNotation(self) -> str:
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(
            self.endRow, self.endCol
        )