import logging as log


def validate_pawn(move):
    log.debug("found a pawn!")
    if move.pieceCaptured == "--" and (((move.startRow, move.startCol) == (move.endRow + 1, move.endCol)) or 
                                        ((move.startRow, move.startCol) == (move.endRow + 2, move.endCol))):
        move.valid = True

    elif move.pieceCaptured != "--" and (((move.startRow, move.startCol) == (move.endRow + 1, move.endCol - 1)) or 
                                        ((move.startRow, move.startCol) == (move.endRow + 1, move.endCol + 1))):
        move.valid = True
    else:
        move.valid = False