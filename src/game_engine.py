"""
This module is responsible for storing and managing the current state of a chess game,
including move validation, game state updates, and special move handling.
"""
import logging as log
from typing import Optional, List, Tuple
from src.constants import Square, Player, PieceType
from src.move_validation import MoveValidatorFactory
from src.moves import Move

class CastlingRights:
    def __init__(self, white_can_castle: bool = True, black_can_castle: bool = True):
        self.white_can_castle = white_can_castle
        self.black_can_castle = black_can_castle

class GameState:
    """
    Represents the current state of a chess game, including the board position,
    move history, and special conditions like castling rights and en-passant possibilities.
    """
    def __init__(self):
        # Board initialization
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
        
        # Game state flags
        self.whiteToMove: bool = True
        self.moveLog: List[Move] = []
        self.enPassantPossible: Tuple[int, int] = ()
        self.castlingRights = CastlingRights()
        
        # Game status flags
        self.in_check: bool = False
        self.checkmate: bool = False
        self.stalemate: bool = False
        
        log.info("New game state initialized")

    # Position and attack validation methods
    def is_square_under_attack(self, row: int, col: int, by_white: bool) -> bool:
        """Check if a square is under attack by any opponent piece."""
        opponent_pieces = []
        for piece in Square:
            if piece.name[0] == 'w' and by_white:
                opponent_pieces.append(piece)
            elif piece.name[0] == 'b' and not by_white:
                opponent_pieces.append(piece)

        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece in opponent_pieces:
                    test_move = Move((r, c), (row, col), self)
                    piece_type = self._get_piece_type(piece)
                    if piece_type:
                        validator = MoveValidatorFactory.get_validator(piece_type)
                        if validator and validator.validate(test_move):
                            return True
        return False

    def get_king_position(self) -> Optional[Tuple[int, int]]:
        """Find the current player's king position."""
        king_piece = Square.wK if self.whiteToMove else Square.bK
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == king_piece:
                    return (r, c)
        return None

    def is_in_check(self) -> bool:
        """Check if the current player's king is in check."""
        king_pos = self.get_king_position()
        if king_pos:
            return self.is_square_under_attack(king_pos[0], king_pos[1], not self.whiteToMove)
        return False

    # Move validation and execution methods
    def would_move_cause_check(self, move: Move) -> bool:
        """Test if making a move would put or leave own king in check."""
        original_board = [row[:] for row in self.board]
        original_white_to_move = self.whiteToMove
        
        self._apply_move_to_board(move)
        result = self.is_in_check()
        
        self.board = [row[:] for row in original_board]
        self.whiteToMove = original_white_to_move
        return result

    def checkMoveValidity(self, move: Move) -> None:
        """Validate a move according to piece rules and check conditions."""
        piece_type_char = Square(move.pieceMoved).name[1].lower()
        piece_color = Square(move.pieceMoved).name[0]
        
        if not self._is_correct_turn(piece_color):
            move.valid = False
            log.warning(f"Invalid turn: {'White' if self.whiteToMove else 'Black'} to move, but {piece_color} piece selected")
            return

        piece_type = self._get_piece_type(move.pieceMoved)
        if not piece_type:
            move.valid = False
            return

        validator = MoveValidatorFactory.get_validator(piece_type)
        if not validator:
            log.error(f"No validator found for piece type: {piece_type}")
            move.valid = False
            return

        move.valid = validator.validate(move) and not self.would_move_cause_check(move)
        log.debug(f"Move validation result for {piece_type} from {(move.startRow, move.startCol)} to {(move.endRow, move.endCol)}: {'Valid' if move.valid else 'Invalid'}")

    def makeMove(self, move: Move) -> None:
        """Execute a validated move and update game state."""
        if not move.valid:
            return

        # Store state for potential undo
        previous_state = self._store_previous_state()
        
        # Reset en passant possibility
        self.enPassantPossible = ()

        if move.isCastling:
            self._execute_castling_move(move)
        elif move.isEnPassant:
            self._execute_en_passant_move(move)
        else:
            self._execute_regular_move(move)

        # Update en passant possibility for pawn double moves
        self._update_en_passant_possibility(move)
        
        # Update castling rights
        self.updateCastlingRights(move)
        
        # Log move and update game state
        move.previousEnPassantPossible = previous_state["enPassantPossible"]
        move.previousCastlingRights = previous_state["castlingRights"]
        self.moveLog.append(move)
        self.swap_players()
        self.update_game_state()

    def undoMove(self) -> None:
        """Undo the last move and restore previous game state."""
        if not self.moveLog:
            log.warning("Attempted to undo move but no moves in log")
            return
            
        move = self.moveLog.pop()
        if move.isCastling:
            self._undo_castling_move(move)
        elif move.isEnPassant:
            self._undo_en_passant_move(move)
        else:
            self._undo_regular_move(move)

        # Restore previous state
        self.enPassantPossible = move.previousEnPassantPossible
        self.castlingRights = move.previousCastlingRights
        self.swap_players()

    # Helper methods
    def _get_piece_type(self, piece: Square) -> Optional[PieceType]:
        """Map a piece to its corresponding PieceType."""
        piece_type_map = {
            'r': PieceType.ROOK,
            'n': PieceType.KNIGHT,
            'b': PieceType.BISHOP,
            'q': PieceType.QUEEN,
            'k': PieceType.KING,
            'p': PieceType.PAWN
        }
        try:
            return piece_type_map[piece.name[1].lower()]
        except KeyError:
            log.error(f"Failed to map piece type for: {piece}")
            return None

    def _is_correct_turn(self, piece_color: str) -> bool:
        """Check if it's the correct player's turn."""
        return ((self.whiteToMove and piece_color == 'w') or 
                (not self.whiteToMove and piece_color == 'b'))

    def _store_previous_state(self) -> dict:
        """Store current state for potential undo."""
        return {
            "enPassantPossible": self.enPassantPossible,
            "castlingRights": CastlingRights(
                self.castlingRights.white_can_castle,
                self.castlingRights.black_can_castle
            )
        }

    def _apply_move_to_board(self, move: Move) -> None:
        """Apply a move to the board without state updates."""
        self.board[move.startRow][move.startCol] = Square.EMPTY
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.promotedPiece
        else:
            self.board[move.endRow][move.endCol] = move.pieceMoved

    def _execute_castling_move(self, move: Move) -> None:
        """Execute a castling move."""
        self.board[move.startRow][move.startCol] = Square.EMPTY
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.board[move.rookMove.startRow][move.rookMove.startCol] = Square.EMPTY
        self.board[move.rookMove.endRow][move.rookMove.endCol] = \
            Square.wR if move.pieceMoved == Square.wK else Square.bR

    def _execute_en_passant_move(self, move: Move) -> None:
        """Execute an en passant move."""
        self.board[move.startRow][move.startCol] = Square.EMPTY
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.board[move.enPassantCaptureRow][move.enPassantCaptureCol] = Square.EMPTY
        move.pieceCaptured = Square.wp if move.pieceMoved == Square.bp else Square.bp

    def _execute_regular_move(self, move: Move) -> None:
        """Execute a regular move or pawn promotion."""
        self._apply_move_to_board(move)

    def _undo_castling_move(self, move: Move) -> None:
        """Undo a castling move."""
        self.board[move.startRow][move.startCol] = move.pieceMoved
        self.board[move.endRow][move.endCol] = Square.EMPTY
        self.board[move.rookMove.startRow][move.rookMove.startCol] = \
            Square.wR if move.pieceMoved == Square.wK else Square.bR
        self.board[move.rookMove.endRow][move.rookMove.endCol] = Square.EMPTY

    def _undo_en_passant_move(self, move: Move) -> None:
        """Undo an en passant move."""
        self.board[move.startRow][move.startCol] = move.pieceMoved
        self.board[move.endRow][move.endCol] = Square.EMPTY
        self.board[move.enPassantCaptureRow][move.enPassantCaptureCol] = move.pieceCaptured

    def _undo_regular_move(self, move: Move) -> None:
        """Undo a regular move or pawn promotion."""
        self.board[move.startRow][move.startCol] = move.pieceMoved
        self.board[move.endRow][move.endCol] = move.pieceCaptured

    def _update_en_passant_possibility(self, move: Move) -> None:
        """Update en passant possibility after a pawn move."""
        if (move.pieceMoved in (Square.wp, Square.bp) and 
            abs(move.endRow - move.startRow) == 2):
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)

    def swap_players(self) -> None:
        """Switch the active player."""
        self.whiteToMove = not self.whiteToMove
        log.debug(f"Turn changed: {'White' if self.whiteToMove else 'Black'} to move")

    def updateCastlingRights(self, move: Move) -> None:
        """Update castling rights based on piece moves."""
        # King moves
        if move.pieceMoved == Square.wK or move.isCastling:
            self.castlingRights.white_can_castle = False
        elif move.pieceMoved == Square.bK or move.isCastling:
            self.castlingRights.black_can_castle = False
        
        # Rook moves
        self._update_rook_castling_rights(move)

    def _update_rook_castling_rights(self, move: Move) -> None:
        """Update castling rights specifically for rook moves or captures."""
        if move.pieceMoved == Square.wR and move.startRow == 7:
            if move.startCol in (0, 7):
                self.castlingRights.white_can_castle = False
        elif move.pieceMoved == Square.bR and move.startRow == 0:
            if move.startCol in (0, 7):
                self.castlingRights.black_can_castle = False
        
        # Rook captures
        if move.pieceCaptured == Square.wR and move.endRow == 7:
            if move.endCol in (0, 7):
                self.castlingRights.white_can_castle = False
        elif move.pieceCaptured == Square.bR and move.endRow == 0:
            if move.endCol in (0, 7):
                self.castlingRights.black_can_castle = False

    def get_all_possible_moves(self) -> List[Move]:
        """Get all valid moves for the current player."""
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if ((self.whiteToMove and piece.name.startswith('w')) or 
                    (not self.whiteToMove and piece.name.startswith('b'))):
                    for end_r in range(8):
                        for end_c in range(8):
                            move = Move((r, c), (end_r, end_c), self)
                            self.checkMoveValidity(move)
                            if move.valid:
                                moves.append(move)
        return moves

    def update_game_state(self) -> None:
        """Update check, checkmate, and stalemate status."""
        self.in_check = self.is_in_check()
        possible_moves = self.get_all_possible_moves()
        
        if not possible_moves:
            if self.in_check:
                self.checkmate = True
                log.info(f"Checkmate! {'Black' if self.whiteToMove else 'White'} wins!")
            else:
                self.stalemate = True
                log.info("Stalemate!")
        else:
            self.checkmate = False
            self.stalemate = False


