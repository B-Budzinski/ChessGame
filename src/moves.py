"""
Classes representing chess moves and their properties.
This module provides classes for representing and handling chess moves,
including special moves like castling, en passant, and pawn promotion.
"""
from src.constants import BoardPositions, Square

class RookMove:
    """
    Represents a rook's move during castling.
    
    This is a helper class used to track the rook's movement when executing
    a castling move, storing both the start and end positions.
    
    Attributes:
        startRow: Starting row of the rook
        startCol: Starting column of the rook
        endRow: Ending row of the rook
        endCol: Ending column of the rook
    """
    def __init__(self, startRow: int = None, startCol: int = None, endRow: int = None, endCol: int = None):
        self.startRow = startRow
        self.startCol = startCol
        self.endRow = endRow
        self.endCol = endCol

class Move:
    """
    Represents a chess move with all its properties and validation state.
    
    This class handles all aspects of a chess move, including:
    - Start and end positions
    - Piece being moved and captured
    - Special moves (castling, en passant, pawn promotion)
    - Chess notation conversion
    
    Attributes:
        startRow: Starting row of the piece
        startCol: Starting column of the piece
        endRow: Ending row of the piece
        endCol: Ending column of the piece
        pieceMoved: The piece being moved
        pieceCaptured: The piece being captured (if any)
        valid: Whether the move is valid according to chess rules
        isCastling: Whether this is a castling move
        isEnPassant: Whether this is an en passant capture
        isPawnPromotion: Whether this is a pawn promotion move
        rookMove: Associated rook move for castling
        promotedPiece: The piece type chosen for pawn promotion
    """
    
    # Mapping between chess notation and internal board coordinates
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
        """
        Initialize a new move.
        
        Args:
            startSq: Tuple of (row, col) for the starting square
            endSq: Tuple of (row, col) for the ending square
            gameState: Current game state containing board and move information
        """
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
        """
        Convert internal board coordinates to chess notation.
        
        Args:
            r: Row number (0-7)
            c: Column number (0-7)
            
        Returns:
            str: Square in chess notation (e.g., 'e4')
        """
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    def getChessNotation(self) -> str:
        """
        Get the complete move in chess notation.
        
        Returns:
            str: Move in chess notation (e.g., 'e2e4')
        """
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(
            self.endRow, self.endCol
        )