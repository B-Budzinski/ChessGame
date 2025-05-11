from enum import StrEnum, IntEnum

class GameConstants(StrEnum):
    WIDTH = '512'
    HEIGHT = '512'
    DIMENSION = '8'
    SQ_SIZE = '64'  # HEIGHT // DIMENSION (512 // 8)
    MAX_FPS = '15'

class UIConstants(IntEnum):
    TRANSPARENCY_ALPHA = 100
    BORDER_WIDTH = 2
    PROMOTION_DIALOG_WIDTH_SQUARES = 4
    PROMOTION_DIALOG_HEIGHT_SQUARES = 1

class ColorIndices(IntEnum):
    LIGHT = 0
    DARK = 1

class BoardPositions(IntEnum):
    FIRST_RANK = 7
    SECOND_RANK = 6
    THIRD_RANK = 5
    FOURTH_RANK = 4
    FIFTH_RANK = 3
    SIXTH_RANK = 2
    SEVENTH_RANK = 1
    EIGHTH_RANK = 0
    
    FIRST_FILE = 0
    SECOND_FILE = 1
    THIRD_FILE = 2
    FOURTH_FILE = 3
    FIFTH_FILE = 4
    SIXTH_FILE = 5
    SEVENTH_FILE = 6
    EIGHTH_FILE = 7

    # Updated to match actual board coordinates where white pawns start on rank 6
    WHITE_PAWN_RANK = 6  # Changed from SEVENTH_RANK
    BLACK_PAWN_RANK = 1
    WHITE_PIECES_RANK = 7  # Changed from EIGHTH_RANK
    BLACK_PIECES_RANK = 0
    KING_START_FILE = FIFTH_FILE
    KINGSIDE_ROOK_FILE = EIGHTH_FILE
    QUEENSIDE_ROOK_FILE = FIRST_FILE

class MoveRules(IntEnum):
    PAWN_FIRST_MOVE = 2
    PAWN_REGULAR_MOVE = 1
    KING_CASTLING_DISTANCE = 2
    MAX_KING_MOVE = 1

IMAGES = {}  # Keep this as a dict since it's mutable and will be populated dynamically

class PieceType(StrEnum):
    KING = 'K'
    QUEEN = 'Q'
    BISHOP = 'B'
    KNIGHT = 'N'
    ROOK = 'R'
    PAWN = 'p'  # Changed to lowercase 'p' to match Square enum

class Player(StrEnum):
    WHITE = 'w'
    BLACK = 'b'

class Square(StrEnum):
    EMPTY = '--'
    
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
        return cls(player + piece)