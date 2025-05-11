"""
This class is responsible for storing all of the info about the current state of a chess game. It will also be responsible for determining the valid moves at the current state. It will also keep a move log.
"""
import logging as log
from src.constants import Square, Player, PieceType, BoardPositions
from src.move_validation import MoveValidatorFactory

class RookMove:
    def __init__(self, startRow=None, startCol=None, endRow=None, endCol=None):
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
    
    def __init__(self, startSq, endSq, gameState):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.gameState = gameState  # Store reference to full game state
        self.board = gameState.board  # Keep board reference for compatibility
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
        self.enPassantCaptureRow = None
        self.enPassantCaptureCol = None
        
        # For pawn promotion - store promoted piece
        self.promotedPiece = None

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    def getChessNotation(self):
        # not really a chess notation because there's a lot more logic going into it, which doesn't matter at this point
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(
            self.endRow, self.endCol
        )

class CastlingRights:
    def __init__(self, white_can_castle=True, black_can_castle=True):
        self.white_can_castle = white_can_castle  # Whether white king can still castle
        self.black_can_castle = black_can_castle  # Whether black king can still castle

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
        self.enPassantPossible = ()  # Keeps track of possible en passant square
        self.castlingRights = CastlingRights()
        log.info("New game state initialized")

    def checkMoveValidity(self, move: Move):
        """
        Takes Move as parameter and determines if it's valid
        """
        log.debug(f"Validating move - Piece moved: {move.pieceMoved}, From: ({move.startRow}, {move.startCol}), To: ({move.endRow}, {move.endCol})")
        
        piece_str = move.pieceMoved.value  # Get the actual string value from the enum
        log.debug(f"Piece string representation: {piece_str}")
        
        piece_color = piece_str[0]  # First character is the color (w/b)
        piece_type_char = piece_str[1]  # Second character is the piece type
        log.debug(f"Extracted color: {piece_color}, type char: {piece_type_char}")
        
        # Map the character to PieceType enum
        piece_type_map = {
            'K': PieceType.KING,
            'Q': PieceType.QUEEN,
            'B': PieceType.BISHOP,
            'N': PieceType.KNIGHT,
            'R': PieceType.ROOK,
            'p': PieceType.PAWN
        }
        
        try:
            piece_type = piece_type_map[piece_type_char]
            log.debug(f"Mapped to piece type: {piece_type}")
        except KeyError:
            log.error(f"Failed to map piece type character: {piece_type_char}")
            move.valid = False
            return
        
        # First check if it's the correct player's turn
        if (self.whiteToMove and piece_color != Player.WHITE) or (not self.whiteToMove and piece_color != Player.BLACK):
            move.valid = False
            log.warning(f"Invalid turn: {'White' if self.whiteToMove else 'Black'} to move, but {piece_color} piece selected")
            return

        validator = MoveValidatorFactory.get_validator(piece_type)
        if validator is None:
            log.error(f"No validator found for piece type: {piece_type}")
            move.valid = False
            return
            
        move.valid = validator.validate(move)
        log.debug(f"Move validation result for {piece_type} from {(move.startRow, move.startCol)} to {(move.endRow, move.endCol)}: {'Valid' if move.valid else 'Invalid'}")

    def swap_players(self):
        """
        Swaps the players
        """
        self.whiteToMove = not self.whiteToMove
        log.debug(f"Turn changed: {'White' if self.whiteToMove else 'Black'} to move")

    def makeMove(self, move):
        """
        Execute the move, including special moves like castling, en passant, and pawn promotion
        """
        if not move.valid:
            return

        # Store current en passant state for potential undo
        previousEnPassantPossible = self.enPassantPossible
        previousCastlingRights = CastlingRights(
            self.castlingRights.white_can_castle,
            self.castlingRights.black_can_castle
        )

        # Reset en passant possibility
        self.enPassantPossible = ()

        if move.isCastling:
            # Move the king
            self.board[move.startRow][move.startCol] = Square.EMPTY
            self.board[move.endRow][move.endCol] = move.pieceMoved
            # Move the rook
            self.board[move.rookMove.startRow][move.rookMove.startCol] = Square.EMPTY
            self.board[move.rookMove.endRow][move.rookMove.endCol] = \
                Square.wR if move.pieceMoved == Square.wK else Square.bR
        
        elif move.isEnPassant:
            # Move the pawn
            self.board[move.startRow][move.startCol] = Square.EMPTY
            self.board[move.endRow][move.endCol] = move.pieceMoved
            # Remove the captured pawn
            self.board[move.enPassantCaptureRow][move.enPassantCaptureCol] = Square.EMPTY
            # Store the captured piece for undo
            move.pieceCaptured = Square.wp if move.pieceMoved == Square.bp else Square.bp
        
        else:
            # Normal move or pawn promotion
            self.board[move.startRow][move.startCol] = Square.EMPTY
            if move.isPawnPromotion:
                self.board[move.endRow][move.endCol] = move.promotedPiece
            else:
                self.board[move.endRow][move.endCol] = move.pieceMoved

        # Update en passant possibility for two-square pawn moves
        if (move.pieceMoved == Square.wp or move.pieceMoved == Square.bp) and \
           abs(move.endRow - move.startRow) == 2:
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)

        # Update castling rights
        self.updateCastlingRights(move)
        
        # Log the move and swap players
        move.previousEnPassantPossible = previousEnPassantPossible
        move.previousCastlingRights = previousCastlingRights
        self.moveLog.append(move)
        self.swap_players()

    def undoMove(self):
        """
        Undo the last move, including special moves
        """
        if not self.moveLog:
            log.warning("Attempted to undo move but no moves in log")
            return
            
        move = self.moveLog.pop()
        if move.isCastling:
            # Restore king
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = Square.EMPTY
            # Restore rook
            self.board[move.rookMove.startRow][move.rookMove.startCol] = \
                Square.wR if move.pieceMoved == Square.wK else Square.bR
            self.board[move.rookMove.endRow][move.rookMove.endCol] = Square.EMPTY
        
        elif move.isEnPassant:
            # Restore moving pawn
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = Square.EMPTY
            # Restore captured pawn
            self.board[move.enPassantCaptureRow][move.enPassantCaptureCol] = move.pieceCaptured
        
        else:
            # Normal move or pawn promotion
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured

        # Restore en passant state
        self.enPassantPossible = move.previousEnPassantPossible
        # Restore castling rights
        self.castlingRights = move.previousCastlingRights
        self.swap_players()

    def updateCastlingRights(self, move):
        """
        Update castling rights based on the move
        """
        # If king moves or castles, lose castling rights
        if move.pieceMoved == Square.wK or move.isCastling:
            self.castlingRights.white_can_castle = False
        elif move.pieceMoved == Square.bK or move.isCastling:
            self.castlingRights.black_can_castle = False
        # If rook moves or is captured, lose that side's castling right
        elif move.pieceMoved == Square.wR:
            if move.startRow == 7:
                if move.startCol == 0:
                    self.castlingRights.white_can_castle = False
                elif move.startCol == 7:
                    self.castlingRights.white_can_castle = False
        elif move.pieceMoved == Square.bR:
            if move.startRow == 0:
                if move.startCol == 0:
                    self.castlingRights.black_can_castle = False
                elif move.startCol == 7:
                    self.castlingRights.black_can_castle = False
        # If rook is captured
        if move.pieceCaptured == Square.wR:
            if move.endRow == 7:
                if move.endCol == 0:
                    self.castlingRights.white_can_castle = False
                elif move.endCol == 7:
                    self.castlingRights.white_can_castle = False
        elif move.pieceCaptured == Square.bR:
            if move.endRow == 0:
                if move.endCol == 0:
                    self.castlingRights.black_can_castle = False
                elif move.endCol == 7:
                    self.castlingRights.black_can_castle = False


