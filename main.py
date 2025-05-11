"""
Chess Game Main Module

This is the main driver module responsible for:
- Initializing the game window and resources
- Handling user input (mouse clicks and keyboard commands)
- Managing the game loop and state updates
- Coordinating between UI rendering and game logic
"""

import logging as log
import pygame as p
import src.game_engine as game_engine
from src.constants import GameConstants, Square
from src.ui_renderer import UIRenderer
from src.resource_manager import ResourceManager

# Configure logging to both file and console
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
    """
    Main game loop and initialization.
    
    This function:
    1. Initializes Pygame and creates the game window
    2. Sets up the game state and UI components
    3. Enters the main game loop to handle:
       - User input (mouse clicks for moves, 'z' key for undo)
       - Game state updates
       - Screen rendering
    4. Manages special game situations:
       - Pawn promotion dialogs
       - Move validation
       - Game termination
    """
    p.init()
    screen = p.display.set_mode((int(GameConstants.WIDTH), int(GameConstants.HEIGHT)))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    
    gs = game_engine.GameState()
    ui_renderer = UIRenderer(screen)
    ResourceManager.load_images()
    
    running = True
    sqSelected = ()  # no square selected initially, tracks last click (tuple: row, col)
    playerClicks = []  # tracks player clicks for moves (two tuples: [(6,4), (4,4)])
    log.info("Starting new chess game")
    
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                log.info("Game terminated by user")
                running = False
                
            # Mouse input handling
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x,y) location of mouse
                col = location[0] // int(GameConstants.SQ_SIZE)
                row = location[1] // int(GameConstants.SQ_SIZE)
                
                if sqSelected == (row, col):  # user clicked same square twice
                    log.debug(f"Square deselected at position: ({row}, {col})")
                    sqSelected = ()  # deselect
                    playerClicks = []  # clear player clicks
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                    log.debug(f"Square selected at position: ({row}, {col})")
                
                # Process move after second click
                if len(playerClicks) == 2:
                    move = game_engine.Move(playerClicks[0], playerClicks[1], gs)
                    log.debug(f"Attempting move from {playerClicks[0]} to {playerClicks[1]}")
                    
                    gs.checkMoveValidity(move)
                    if move.valid:
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
                        move.valid = True  # reset validity flag
            
            # Keyboard input handling
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo move on 'z' key press
                    log.debug("Undo move requested")
                    gs.undoMove()
        
        # Update display
        ui_renderer.draw_game_state(gs, sqSelected)
        clock.tick(int(GameConstants.MAX_FPS))
        p.display.flip()

if __name__ == "__main__":
    main()
