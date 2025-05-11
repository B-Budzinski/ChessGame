from abc import ABC, abstractmethod
import logging as log
from typing import List, Tuple
from src.constants import Square, Player, PieceType

class MoveValidator(ABC):
    @abstractmethod
    def validate(self, move) -> bool:
        pass
    
    def _is_path_clear(self, move, path_positions: List[Tuple[int, int]]) -> bool:
        """Check if there are any pieces between start and end position"""
        for row, col in path_positions[1:-1]:  # Exclude start and end squares
            if move.board[row][col] != Square.EMPTY:
                return False
        return True
    
    def _is_friendly_piece_at_destination(self, move) -> bool:
        """Check if destination contains a friendly piece"""
        if move.pieceCaptured == Square.EMPTY:
            return False
        moved_piece_color = Square(move.pieceMoved)[0]
        captured_piece_color = Square(move.pieceCaptured)[0]
        return moved_piece_color == captured_piece_color

    def _get_path_positions(self, move) -> List[Tuple[int, int]]:
        """Get all positions between start and end (inclusive)"""
        positions = []
        row_diff = move.endRow - move.startRow
        col_diff = move.endCol - move.startCol
        
        steps = max(abs(row_diff), abs(col_diff))
        row_step = row_diff // steps if steps > 0 else 0
        col_step = col_diff // steps if steps > 0 else 0
        
        for i in range(steps + 1):
            row = move.startRow + (i * row_step)
            col = move.startCol + (i * col_step)
            positions.append((row, col))
            
        return positions

class PawnMoveValidator(MoveValidator):
    def validate(self, move) -> bool:
        if self._is_friendly_piece_at_destination(move):
            return False
            
        piece_color = Square(move.pieceMoved)[0]
        direction = 1 if piece_color == Player.BLACK else -1
        
        # Check for pawn promotion
        if (piece_color == Player.WHITE and move.endRow == 0) or \
           (piece_color == Player.BLACK and move.endRow == 7):
            move.isPawnPromotion = True
            # promotedPiece will be set later when user selects the piece
        
        # Normal one-square move
        if move.pieceCaptured == Square.EMPTY and (
            (move.startRow + direction, move.startCol) == (move.endRow, move.endCol)
        ):
            return True
            
        # Initial two-square move
        if move.pieceCaptured == Square.EMPTY and (
            ((piece_color == Player.WHITE and move.startRow == 6) or 
             (piece_color == Player.BLACK and move.startRow == 1)) and
            (move.startRow + 2 * direction, move.startCol) == (move.endRow, move.endCol)
        ):
            # Check if the intermediate square is empty
            intermediate_row = move.startRow + direction
            if move.board[intermediate_row][move.startCol] != Square.EMPTY:
                return False
            return True
            
        # Regular capture moves
        if move.pieceCaptured != Square.EMPTY and (
            (move.startRow + direction, move.startCol - 1) == (move.endRow, move.endCol) or
            (move.startRow + direction, move.startCol + 1) == (move.endRow, move.endCol)
        ):
            return True
            
        # En passant
        if hasattr(move.gameState, 'enPassantPossible') and move.gameState.enPassantPossible:
            enPassant_row, enPassant_col = move.gameState.enPassantPossible
            if (move.endRow, move.endCol) == (enPassant_row, enPassant_col):
                # Verify it's a diagonal move
                if abs(move.startCol - move.endCol) == 1 and move.endRow == move.startRow + direction:
                    move.isEnPassant = True
                    # The captured pawn is on the same row as the starting position
                    move.enPassantCaptureRow = move.startRow
                    move.enPassantCaptureCol = move.endCol
                    return True
            
        return False

class RookMoveValidator(MoveValidator):
    def validate(self, move) -> bool:
        if not (move.startRow == move.endRow or move.startCol == move.endCol):
            return False
            
        if self._is_friendly_piece_at_destination(move):
            return False
            
        path = self._get_path_positions(move)
        return self._is_path_clear(move, path)

class KnightMoveValidator(MoveValidator):
    def validate(self, move) -> bool:
        if self._is_friendly_piece_at_destination(move):
            return False
            
        row_diff = abs(move.endRow - move.startRow)
        col_diff = abs(move.endCol - move.startCol)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

class BishopMoveValidator(MoveValidator):
    def validate(self, move) -> bool:
        if abs(move.endRow - move.startRow) != abs(move.endCol - move.startCol):
            return False
            
        if self._is_friendly_piece_at_destination(move):
            return False
            
        path = self._get_path_positions(move)
        return self._is_path_clear(move, path)

class QueenMoveValidator(MoveValidator):
    def validate(self, move) -> bool:
        # Queen combines Rook and Bishop movements
        is_straight = move.startRow == move.endRow or move.startCol == move.endCol
        is_diagonal = abs(move.endRow - move.startRow) == abs(move.endCol - move.startCol)
        
        if not (is_straight or is_diagonal):
            return False
            
        if self._is_friendly_piece_at_destination(move):
            return False
            
        path = self._get_path_positions(move)
        return self._is_path_clear(move, path)

class KingMoveValidator(MoveValidator):
    def validate(self, move) -> bool:
        if self._is_friendly_piece_at_destination(move):
            return False
            
        row_diff = abs(move.endRow - move.startRow)
        col_diff = abs(move.endCol - move.startCol)
        
        # Normal king moves
        if row_diff <= 1 and col_diff <= 1:
            return True
            
        # Castling
        if row_diff == 0 and col_diff == 2:
            # Check if this is a castling attempt
            is_white = Square(move.pieceMoved)[0] == Player.WHITE
            is_kingside = move.endCol > move.startCol
            
            # Verify king and rook positions
            if is_white and move.startRow != 7:
                return False
            if not is_white and move.startRow != 0:
                return False
            if move.startCol != 4:
                return False
                
            # Check castling rights
            if (is_white and not move.gameState.castlingRights.white_can_castle) or \
               (not is_white and not move.gameState.castlingRights.black_can_castle):
                return False
            
            # Check if squares between king and rook are empty
            rook_col = 7 if is_kingside else 0
            path = self._get_path_positions(move)
            if not self._is_path_clear(move, path):
                return False
                
            # Verify rook presence
            expected_rook = Square.wR if is_white else Square.bR
            if move.board[move.startRow][rook_col] != expected_rook:
                return False
                
            # Set castling info
            move.isCastling = True
            move.rookMove.startRow = move.startRow
            move.rookMove.startCol = rook_col
            move.rookMove.endRow = move.startRow
            move.rookMove.endCol = move.startCol + (1 if is_kingside else -1)
            
            return True
            
        return False

class MoveValidatorFactory:
    _validators = {
        PieceType.PAWN: PawnMoveValidator(),
        PieceType.ROOK: RookMoveValidator(),
        PieceType.KNIGHT: KnightMoveValidator(),
        PieceType.BISHOP: BishopMoveValidator(),
        PieceType.QUEEN: QueenMoveValidator(),
        PieceType.KING: KingMoveValidator()
    }

    @classmethod
    def get_validator(cls, piece_type: PieceType) -> MoveValidator:
        return cls._validators.get(piece_type)