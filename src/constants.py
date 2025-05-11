from enum import StrEnum, IntEnum

class GameConstants(StrEnum):
    """
    Basic game window and board configuration constants.
    All values are strings for compatibility with pygame configuration.
    """
    WIDTH = '512'
    HEIGHT = '512'
    DIMENSION = '8'
    SQ_SIZE = '64'  # HEIGHT // DIMENSION (512 // 8)
    MAX_FPS = '15'

class UIConstants(IntEnum):
    """
    User interface rendering constants for visual elements.
    """
    TRANSPARENCY_ALPHA = 100  # Alpha value for semi-transparent UI elements
    BORDER_WIDTH = 2  # Width of borders in pixels
    PROMOTION_DIALOG_WIDTH_SQUARES = 4  # Width of pawn promotion dialog in squares
    PROMOTION_DIALOG_HEIGHT_SQUARES = 1  # Height of pawn promotion dialog in squares

class ColorIndices(IntEnum):
    """
    Indices for chess board square colors.
    Used in rendering the checkerboard pattern.
    """
    LIGHT = 0
    DARK = 1

class BoardPositions(IntEnum):
    """
    Chess board coordinate system constants.
    
    Ranks (rows) are numbered 0-7 from top to bottom.
    Files (columns) are numbered 0-7 from left to right.
    Special positions for specific piece setups are also defined.
    """
    # Ranks (rows)
    FIRST_RANK = 7
    SECOND_RANK = 6
    THIRD_RANK = 5
    FOURTH_RANK = 4
    FIFTH_RANK = 3
    SIXTH_RANK = 2
    SEVENTH_RANK = 1
    EIGHTH_RANK = 0
    
    # Files (columns)
    FIRST_FILE = 0
    SECOND_FILE = 1
    THIRD_FILE = 2
    FOURTH_FILE = 3
    FIFTH_FILE = 4
    SIXTH_FILE = 5
    SEVENTH_FILE = 6
    EIGHTH_FILE = 7
    
    # Special positions
    WHITE_PAWN_RANK = 6
    BLACK_PAWN_RANK = 1
    WHITE_PIECES_RANK = 7
    BLACK_PIECES_RANK = 0
    KING_START_FILE = FIFTH_FILE
    KINGSIDE_ROOK_FILE = EIGHTH_FILE
    QUEENSIDE_ROOK_FILE = FIRST_FILE

class MoveRules(IntEnum):
    """
    Constants defining legal move distances for different pieces.
    Used in move validation.
    """
    PAWN_FIRST_MOVE = 2  # Number of squares a pawn can move on its first move
    PAWN_REGULAR_MOVE = 1  # Normal pawn move distance
    KING_CASTLING_DISTANCE = 2  # Number of squares the king moves during castling
    MAX_KING_MOVE = 1  # Maximum distance for normal king moves

# Global dictionary for piece images, populated at runtime
IMAGES = {}

class PieceType(StrEnum):
    """
    Chess piece type identifiers.
    Used in combination with Player enum to create unique piece identifiers.
    """
    KING = 'K'
    QUEEN = 'Q'
    BISHOP = 'B'
    KNIGHT = 'N'
    ROOK = 'R'
    PAWN = 'p'  # Lowercase to match Square enum convention

class Player(StrEnum):
    """
    Player color identifiers.
    Combined with PieceType to create unique piece identifiers.
    """
    WHITE = 'w'
    BLACK = 'b'

class Square(StrEnum):
    """
    Chess square state identifiers.
    Combines player color (w/b) with piece type to represent board positions.
    """
    EMPTY = '--'  # Represents an empty square
    
    # White pieces
    wK = 'wK'
    wQ = 'wQ'
    wB = 'wB'
    wN = 'wN'
    wR = 'wR'
    wp = 'wp'
    
    # Black pieces
    bK = 'bK'
    bQ = 'bQ'
    bB = 'bB'
    bN = 'bN'
    bR = 'bR'
    bp = 'bp'

    @classmethod
    def get_piece(cls, player: Player, piece: PieceType) -> 'Square':
        """
        Create a Square enum value from player color and piece type.
        
        Args:
            player: Player enum value (WHITE/BLACK)
            piece: PieceType enum value
            
        Returns:
            Square: The corresponding Square enum value for the piece
        """
        return cls(player + piece)