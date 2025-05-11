"""
This is the main driver file. It will be responsible for handling user input and displaying current GameState object.
"""
import logging as log
import pygame as p
import src.game_engine as game_engine
from src.constants import GameConstants, Square
from src.ui_renderer import UIRenderer
from src.resource_manager import ResourceManager

log.basicConfig(
    level=log.DEBUG,
    format="%(name)s - %(levelname)s - %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d  %H:%M:%S",
    handlers=[
        log.FileHandler("app.log", mode="a"),
        log.StreamHandler()  # This will output logs to console
    ]
)

def main():
    p.init()
    screen = p.display.set_mode((int(GameConstants.WIDTH), int(GameConstants.HEIGHT)))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    
    gs = game_engine.GameState()
    ui_renderer = UIRenderer(screen)
    ResourceManager.load_images()
    
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
                    playerClicks.append(sqSelected)  # append for both 1st and 2nd clicks
                    log.debug(f"Square selected at position: ({row}, {col})")
                if len(playerClicks) == 2:  # after second click
                    move = game_engine.Move(playerClicks[0], playerClicks[1], gs)
                    log.debug(f"Attempting move from {playerClicks[0]} to {playerClicks[1]}")
                    gs.checkMoveValidity(move)
                    if move.valid:  # check move validity
                        if move.isPawnPromotion:
                            promoted_piece = ui_renderer.show_promotion_dialog(gs.whiteToMove)
                            move.promotedPiece = getattr(Square, promoted_piece)
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
                    
        ui_renderer.draw_game_state(gs, sqSelected)
        clock.tick(int(GameConstants.MAX_FPS))
        p.display.flip()

if __name__ == "__main__":
    main()
