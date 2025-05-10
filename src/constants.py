from enum import StrEnum

WIDTH = HEIGHT = 512  # 400 another good option, could go larger but the images are low res
DIMENSION = 8  # chessboard is 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations
IMAGES = {}

class PieceType(StrEnum):
    KING = 'K'
    QUEEN = 'Q'
    BISHOP = 'B'
    KNIGHT = 'N'
    ROOK = 'R'
    PAWN = 'p'

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