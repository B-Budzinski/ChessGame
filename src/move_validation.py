from abc import ABC, abstractmethod
import logging as log
from typing import List, Tuple
from src.constants import Square, Player, PieceType, BoardPositions, MoveRules

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
            log.debug("Pawn validation failed: friendly piece at destination")
            return False
            
        piece_color = Square(move.pieceMoved)[0]
        direction = 1 if piece_color == Player.BLACK else -1
        log.debug(f"Pawn validation: piece_color={piece_color}, direction={direction}")
        
        # Check for pawn promotion
        if (piece_color == Player.WHITE and move.endRow == BoardPositions.EIGHTH_RANK) or \
           (piece_color == Player.BLACK and move.endRow == BoardPositions.FIRST_RANK):
            move.isPawnPromotion = True
            log.debug("Pawn validation: promotion detected")
        
        # Normal one-square move
        if move.pieceCaptured == Square.EMPTY and (
            (move.startRow + direction, move.startCol) == (move.endRow, move.endCol)
        ):
            log.debug("Pawn validation: valid one-square move")
            return True
            
        # Initial two-square move
        log.debug(f"Pawn validation: checking two-square move - startRow={move.startRow}, WHITE_PAWN_RANK={BoardPositions.WHITE_PAWN_RANK}")
        if move.pieceCaptured == Square.EMPTY and (
            ((piece_color == Player.WHITE and move.startRow == BoardPositions.WHITE_PAWN_RANK) or 
             (piece_color == Player.BLACK and move.startRow == BoardPositions.BLACK_PAWN_RANK))
        ):
            target_row = move.startRow + MoveRules.PAWN_FIRST_MOVE * direction
            log.debug(f"Pawn validation: two-square move - target_row={target_row}, endRow={move.endRow}")
            if (target_row, move.startCol) == (move.endRow, move.endCol):
                # Check if the intermediate square is empty
                intermediate_row = move.startRow + direction
                log.debug(f"Pawn validation: checking intermediate square at row {intermediate_row}")
                if move.board[intermediate_row][move.startCol] != Square.EMPTY:
                    log.debug("Pawn validation: intermediate square blocked")
                    return False
                log.debug("Pawn validation: valid two-square move")
                return True
            
        # Regular capture moves
        if move.pieceCaptured != Square.EMPTY and (
            (move.startRow + MoveRules.PAWN_REGULAR_MOVE * direction, move.startCol - 1) == (move.endRow, move.endCol) or
            (move.startRow + MoveRules.PAWN_REGULAR_MOVE * direction, move.startCol + 1) == (move.endRow, move.endCol)
        ):
            log.debug("Pawn validation: valid capture move")
            return True
            
        # En passant
        if hasattr(move.gameState, 'enPassantPossible') and move.gameState.enPassantPossible:
            enPassant_row, enPassant_col = move.gameState.enPassantPossible
            if (move.endRow, move.endCol) == (enPassant_row, enPassant_col):
                if abs(move.startCol - move.endCol) == MoveRules.PAWN_REGULAR_MOVE and \
                   move.endRow == move.startRow + direction:
                    move.isEnPassant = True
                    move.enPassantCaptureRow = move.startRow
                    move.enPassantCaptureCol = move.endCol
                    log.debug("Pawn validation: valid en passant move")
                    return True
        log.debug("Pawn validation: no valid move found")
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
        return (row_diff == MoveRules.PAWN_FIRST_MOVE and col_diff == MoveRules.PAWN_REGULAR_MOVE) or \
               (row_diff == MoveRules.PAWN_REGULAR_MOVE and col_diff == MoveRules.PAWN_FIRST_MOVE)

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
        if row_diff <= MoveRules.MAX_KING_MOVE and col_diff <= MoveRules.MAX_KING_MOVE:
            return True
            
        # Castling
        if row_diff == 0 and col_diff == MoveRules.KING_CASTLING_DISTANCE:
            # Check if this is a castling attempt
            is_white = Square(move.pieceMoved)[0] == Player.WHITE
            is_kingside = move.endCol > move.startCol
            
            # Verify king and rook positions
            if is_white and move.startRow != BoardPositions.WHITE_PIECES_RANK:
                return False
            if not is_white and move.startRow != BoardPositions.BLACK_PIECES_RANK:
                return False
            if move.startCol != BoardPositions.KING_START_FILE:
                return False
                
            # Check castling rights
            if (is_white and not move.gameState.castlingRights.white_can_castle) or \
               (not is_white and not move.gameState.castlingRights.black_can_castle):
                return False
            
            # Check if squares between king and rook are empty
            rook_col = BoardPositions.KINGSIDE_ROOK_FILE if is_kingside else BoardPositions.QUEENSIDE_ROOK_FILE
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