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
        self.in_check = False
        self.checkmate = False
        self.stalemate = False

    def is_square_under_attack(self, row: int, col: int, by_white: bool) -> bool:
        """
        Check if a square is under attack by any opponent piece
        This method uses basic piece movement rules without the check validation
        to avoid infinite recursion
        """
        opponent_pieces = []
        for piece in Square:
            if piece.name[0] == 'w' and by_white:
                opponent_pieces.append(piece)
            elif piece.name[0] == 'b' and not by_white:
                opponent_pieces.append(piece)

        # Try moving each opponent piece to the target square
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece in opponent_pieces:
                    test_move = Move((r, c), (row, col), self)
                    
                    # Get piece type for basic move validation
                    piece_type_char = Square(piece).name[1].lower()
                    piece_type_map = {
                        'r': PieceType.ROOK,
                        'n': PieceType.KNIGHT,
                        'b': PieceType.BISHOP,
                        'q': PieceType.QUEEN,
                        'k': PieceType.KING,
                        'p': PieceType.PAWN
                    }
                    piece_type = piece_type_map.get(piece_type_char)
                    
                    if piece_type:
                        validator = MoveValidatorFactory.get_validator(piece_type)
                        if validator and validator.validate(test_move):
                            return True
        return False

    def get_king_position(self) -> tuple:
        """Helper method to find the current player's king position"""
        king_piece = Square.wK if self.whiteToMove else Square.bK
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == king_piece:
                    return (r, c)
        return None  # Should never happen in a valid game

    def is_in_check(self) -> bool:
        """
        Check if the current player's king is in check
        """
        king_pos = self.get_king_position()
        if king_pos:
            return self.is_square_under_attack(king_pos[0], king_pos[1], not self.whiteToMove)
        return False

    def would_move_cause_check(self, move: Move) -> bool:
        """
        Test if making a move would put or leave own king in check
        """
        # Store original board state
        original_board = [row[:] for row in self.board]
        original_white_to_move = self.whiteToMove
        
        # Make move temporarily
        self.board[move.startRow][move.startCol] = Square.EMPTY
        self.board[move.endRow][move.endCol] = move.pieceMoved

        # Special handling for castling
        if move.isCastling:
            rook_start = (move.rookMove.startRow, move.rookMove.startCol)
            rook_end = (move.rookMove.endRow, move.rookMove.endCol)
            rook_piece = original_board[rook_start[0]][rook_start[1]]
            self.board[rook_start[0]][rook_start[1]] = Square.EMPTY
            self.board[rook_end[0]][rook_end[1]] = rook_piece

        # Check if king is in check
        result = self.is_in_check()

        # Restore original board state
        self.board = [row[:] for row in original_board]
        self.whiteToMove = original_white_to_move

        return result

    def checkMoveValidity(self, move: Move):
        """
        Takes Move as parameter and determines if it's valid
        """
        piece_type_char = Square(move.pieceMoved).name[1].lower()
        piece_color = Square(move.pieceMoved)[0]
        
        # First check if it's the correct player's turn
        if (self.whiteToMove and piece_color != Player.WHITE) or (not self.whiteToMove and piece_color != Player.BLACK):
            move.valid = False
            log.warning(f"Invalid turn: {'White' if self.whiteToMove else 'Black'} to move, but {piece_color} piece selected")
            return

        piece_type_map = {
            'r': PieceType.ROOK,
            'n': PieceType.KNIGHT,
            'b': PieceType.BISHOP,
            'q': PieceType.QUEEN,
            'k': PieceType.KING,
            'p': PieceType.PAWN
        }
        
        try:
            piece_type = piece_type_map[piece_type_char]
            log.debug(f"Mapped to piece type: {piece_type}")
        except KeyError:
            log.error(f"Failed to map piece type character: {piece_type_char}")
            move.valid = False
            return

        validator = MoveValidatorFactory.get_validator(piece_type)
        if validator is None:
            log.error(f"No validator found for piece type: {piece_type}")
            move.valid = False
            return

        # First validate the move according to piece rules
        move.valid = validator.validate(move)
        
        # Then check if the move would leave/put own king in check
        if move.valid:
            if self.would_move_cause_check(move):
                move.valid = False
                log.debug("Move would result in check - invalid")

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
        
        # After making the move and swapping players, update game state
        self.update_game_state()

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

    def get_all_possible_moves(self) -> list:
        """
        Get all possible moves for the current player
        """
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                # Check if piece belongs to current player
                if ((self.whiteToMove and piece.name.startswith('w')) or 
                    (not self.whiteToMove and piece.name.startswith('b'))):
                    # Try moving to every square
                    for end_r in range(8):
                        for end_c in range(8):
                            move = Move((r, c), (end_r, end_c), self)
                            self.checkMoveValidity(move)
                            if move.valid:
                                moves.append(move)
        return moves

    def update_game_state(self):
        """
        Update check, checkmate, and stalemate status
        """
        self.in_check = self.is_in_check()
        possible_moves = self.get_all_possible_moves()
        
        if len(possible_moves) == 0:
            if self.in_check:
                self.checkmate = True
                log.info(f"Checkmate! {'Black' if self.whiteToMove else 'White'} wins!")
            else:
                self.stalemate = True
                log.info("Stalemate!")
        else:
            self.checkmate = False
            self.stalemate = False


