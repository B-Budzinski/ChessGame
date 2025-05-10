"""
This is the main driver file. It will be responsible for handling user input and displaying current GameState object.
"""
import logging as log
import pygame as p
import src.game_engine as game_engine  # we are inside the same directory, hence no 'from ChessGame import ChessEngine' :)
from src.constants import WIDTH, HEIGHT, SQ_SIZE, MAX_FPS, IMAGES, DIMENSION

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
            p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE)
        )
    # Note: we can access an image by saying 'IMAGES['wp']'


"""
The main driver for out code. This will handle user input and update the graphics
"""


def main():

    screen = p.display.set_mode((WIDTH, HEIGHT))
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
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

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
                    move = game_engine.Move(playerClicks[0], playerClicks[1], gs.board)
                    log.debug(f"Attempting move from {playerClicks[0]} to {playerClicks[1]}")
                    gs.checkMoveValidity(move)
                    if move.valid:  # check move validity
                        gs.makeMove(move)
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
        clock.tick(MAX_FPS)
        p.display.flip()


"""
Responsible for all the graphics within a current game state.
"""
def drawGameState(screen, gs, sqSelected):
    drawBoard(screen)  # draw squares on the board
    if sqSelected != ():  # if a square is selected
        highlightSquare(screen, sqSelected)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares

"""
Highlight the selected square with a red border
"""
def highlightSquare(screen, square):
    if square != ():  # if square is selected
        row, col = square
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)  # transparency value -> 0 transparent; 255 opaque
        s.fill(p.Color('red'))
        screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))
        # Draw border
        p.draw.rect(screen, p.Color('red'), p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE), 2)

"""
Draw squares on the board. The top left square is always light.
If you add up the x, y positions of a square and the result is even it's a light square, if odd it's a dark square
"""


def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[
                ((r + c) % 2)
            ]  # if the remainder for division by 2 is 0 we will pick colors[0] (light color), if 1 we will pick colors[1] (dark color)
            p.draw.rect(
                screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            )


"""
Draw the pieces on the board using the current GameState.board
"""


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # not empty square
                screen.blit(
                    IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                )


if __name__ == "__main__":
    main()
