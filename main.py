"""
This is the main driver file. It will be responsible for handling user input and displaying current GameState object.
"""
import logging as log
import pygame as p
import src.game_engine as game_engine
from src.constants import (
    GameConstants, 
    UIConstants, 
    IMAGES, 
    Square)

log.basicConfig(
    level=log.DEBUG,
    format="%(name)s - %(levelname)s - %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d  %H:%M:%S",
    handlers=[
        log.FileHandler("app.log", mode="a"),
        log.StreamHandler()  # This will output logs to console
    ]
)


p.init()

"""
Initialize a global dictionary of images. This will be called only once in the main
"""


def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load("images/" + piece + ".png"), (int(GameConstants.SQ_SIZE), int(GameConstants.SQ_SIZE))
        )
    # Note: we can access an image by saying 'IMAGES['wp']'


"""
The main driver for out code. This will handle user input and update the graphics
"""


def showPromotionDialog(screen, is_white_turn):
    """Show dialog for pawn promotion piece selection"""
    dialog_width = int(GameConstants.SQ_SIZE) * UIConstants.PROMOTION_DIALOG_WIDTH_SQUARES
    dialog_height = int(GameConstants.SQ_SIZE) * UIConstants.PROMOTION_DIALOG_HEIGHT_SQUARES
    dialog_x = (int(GameConstants.WIDTH) - dialog_width) // 2
    dialog_y = (int(GameConstants.HEIGHT) - dialog_height) // 2
    
    # Draw dialog background
    dialog_surface = p.Surface((dialog_width, dialog_height))
    dialog_surface.fill(p.Color('white'))
    p.draw.rect(dialog_surface, p.Color('black'), p.Rect(0, 0, dialog_width, dialog_height), UIConstants.BORDER_WIDTH)
    
    # Available pieces for promotion
    color_prefix = 'w' if is_white_turn else 'b'
    pieces = ['Q', 'R', 'B', 'N']
    piece_rects = []
    
    # Draw piece options
    for i, piece in enumerate(pieces):
        piece_img = IMAGES[color_prefix + piece]
        x = i * int(GameConstants.SQ_SIZE)
        piece_rects.append(p.Rect(dialog_x + x, dialog_y, int(GameConstants.SQ_SIZE), int(GameConstants.SQ_SIZE)))
        dialog_surface.blit(piece_img, (x, 0))
    
    screen.blit(dialog_surface, (dialog_x, dialog_y))
    p.display.flip()
    
    # Wait for user selection
    waiting = True
    while waiting:
        for e in p.event.get():
            if e.type == p.MOUSEBUTTONDOWN:
                mouse_pos = p.mouse.get_pos()
                for i, rect in enumerate(piece_rects):
                    if rect.collidepoint(mouse_pos):
                        return color_prefix + pieces[i]
    return color_prefix + 'Q'  # Default to Queen if dialog is closed

def main():
    screen = p.display.set_mode((int(GameConstants.WIDTH), int(GameConstants.HEIGHT)))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = game_engine.GameState()
    loadImages()  # only doing this once, before the while loop
    running = True
    sqSelected = ()  # no square selected initially, keep track of the last click of the user (tuple: row, col))
    playerClicks = []  # keep track of player clicks (two tuples: [(6,4), (4,4)])

    log.info("Starting new chess game")

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                log.info("Game terminated by user")
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x,y) location of mouse
                col = location[0] // int(GameConstants.SQ_SIZE)
                row = location[1] // int(GameConstants.SQ_SIZE)

                if sqSelected == (row, col):  # if the user clicked the same square
                    log.debug(f"Square deselected at position: ({row}, {col})")
                    sqSelected = ()  # deselect
                    playerClicks = []  # clear player clicks

                else:
                    sqSelected = (row, col)
                    playerClicks.append(
                        sqSelected
                    )  # append for both 1st and 2nd clicks
                    log.debug(f"Square selected at position: ({row}, {col})")

                if len(playerClicks) == 2:  # after second click
                    move = game_engine.Move(playerClicks[0], playerClicks[1], gs)
                    log.debug(f"Attempting move from {playerClicks[0]} to {playerClicks[1]}")
                    gs.checkMoveValidity(move)
                    if move.valid:  # check move validity
                        if move.isPawnPromotion:
                            promoted_piece = showPromotionDialog(screen, gs.whiteToMove)
                            move.promotedPiece = getattr(Square, promoted_piece)
                        gs.makeMove(move)
                        
                        # Display check status
                        if gs.in_check and not gs.checkmate:
                            text = f"{'White' if gs.whiteToMove else 'Black'} is in check!"
                            drawText(screen, text)
                        elif gs.checkmate:
                            text = f"Checkmate! {'Black' if gs.whiteToMove else 'White'} wins!"
                            drawText(screen, text)
                        elif gs.stalemate:
                            drawText(screen, "Stalemate!")
                            
                        sqSelected = ()  # reset user clicks
                        playerClicks = []
                    else:
                        log.warning(f"Invalid move attempted from {playerClicks[0]} to {playerClicks[1]}")
                        sqSelected = ()  # reset user clicks
                        playerClicks = []
                        move.valid = True # switch back to True
                        

            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when 'z' key is pressed
                    log.debug("Undo move requested")
                    gs.undoMove()

        drawGameState(screen, gs, sqSelected)
        clock.tick(int(GameConstants.MAX_FPS))
        p.display.flip()

def drawText(screen, text):
    font = p.font.Font(None, 36)
    text_surface = font.render(text, True, p.Color('black'))
    text_rect = text_surface.get_rect()
    text_rect.center = (int(GameConstants.WIDTH) // 2, int(GameConstants.HEIGHT) // 2)
    screen.blit(text_surface, text_rect)

"""
Responsible for all the graphics within a current game state.
"""
def drawGameState(screen, gs, sqSelected):
    drawBoard(screen)  # draw squares on the board
    if sqSelected != ():  # if a square is selected
        highlightSquare(screen, sqSelected)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares
    
    # Draw game state messages after everything else
    if gs.checkmate:
        text = f"Checkmate! {'Black' if gs.whiteToMove else 'White'} wins!"
        drawText(screen, text)
    elif gs.stalemate:
        drawText(screen, "Stalemate!")
    elif gs.in_check:
        text = f"{'White' if gs.whiteToMove else 'Black'} is in check!"
        drawText(screen, text)

"""
Highlight the selected square with a red border
"""
def highlightSquare(screen, square):
    if square != ():  # if square is selected
        row, col = square
        s = p.Surface((int(GameConstants.SQ_SIZE), int(GameConstants.SQ_SIZE)))
        s.set_alpha(UIConstants.TRANSPARENCY_ALPHA)  # transparency value -> 0 transparent; 255 opaque
        s.fill(p.Color('red'))
        screen.blit(s, (col * int(GameConstants.SQ_SIZE), row * int(GameConstants.SQ_SIZE)))
        # Draw border
        p.draw.rect(screen, p.Color('red'), p.Rect(col * int(GameConstants.SQ_SIZE), row * int(GameConstants.SQ_SIZE), int(GameConstants.SQ_SIZE), int(GameConstants.SQ_SIZE)), UIConstants.BORDER_WIDTH)

"""
Draw squares on the board. The top left square is always light.
If you add up the x, y positions of a square and the result is even it's a light square, if odd it's a dark square
"""


def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(int(GameConstants.DIMENSION)):
        for c in range(int(GameConstants.DIMENSION)):
            color = colors[
                ((r + c) % 2)
            ]  # if even, pick light color (colors[LIGHT]), if odd pick dark color (colors[DARK])
            p.draw.rect(
                screen, color, p.Rect(c * int(GameConstants.SQ_SIZE), r * int(GameConstants.SQ_SIZE), int(GameConstants.SQ_SIZE), int(GameConstants.SQ_SIZE))
            )


"""
Draw the pieces on the board using the current GameState.board
"""


def drawPieces(screen, board):
    for r in range(int(GameConstants.DIMENSION)):
        for c in range(int(GameConstants.DIMENSION)):
            piece = board[r][c]
            if piece != "--":  # not empty square
                screen.blit(
                    IMAGES[piece], p.Rect(c * int(GameConstants.SQ_SIZE), r * int(GameConstants.SQ_SIZE), int(GameConstants.SQ_SIZE), int(GameConstants.SQ_SIZE))
                )


if __name__ == "__main__":
    main()
