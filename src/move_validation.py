import logging as log
from src.constants import Square

def validate_pawn(move):
    log.debug("found a pawn!")
    if move.pieceCaptured == Square.EMPTY and (
        ((move.startRow, move.startCol) == (move.endRow + 1, move.endCol)) or 
        ((move.startRow, move.startCol) == (move.endRow + 2, move.endCol))
    ):
        move.valid = True
    elif move.pieceCaptured != Square.EMPTY and (
        ((move.startRow, move.startCol) == (move.endRow + 1, move.endCol - 1)) or 
        ((move.startRow, move.startCol) == (move.endRow + 1, move.endCol + 1))
    ):
        move.valid = True
    else:
        move.valid = False