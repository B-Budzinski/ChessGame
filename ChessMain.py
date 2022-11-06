"""
This is the main driver file. It will be responsible for handling user input and displaying current GameState object.
"""

import pygame as p
import ChessEngine # we are inside the same directory, hence no 'from ChessGame import ChessEngine' :)

p.init()
WIDTH = HEIGHT = 512 # 400 another good option, could go larger but the images are low res
DIMENSION = 8 # chessboard is 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # for animations
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called only once in the main
'''

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # Note: we can access an image by saying 'IMAGES['wp']'


'''
The main driver for out code. This will handle user input and update the graphics
'''

def main():

    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    loadImages() # only doing this once, before the while loop
    running = True
    sqSelected = () # no square selected initially, keep track of the last click of the user (tuple: row, col))
    playerClicks = [] # keep track of player clicks (two tuples: [(6,4), (4,4)])

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() # (x,y) location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                
                if sqSelected == (row, col): # if the user clicked the same square
                    sqSelected = () # deselect
                    playerClicks = [] # clear player clicks

                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected) # append for both 1st and 2nd clicks
                    
                if len(playerClicks) == 2: # after second click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    gs.makeMove(move)
                    sqSelected = () # reset user clicks
                    playerClicks = []

            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # undo when 'z' key is pressed
                    gs.undoMove()


        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Responsible for all the graphics within a current game state.
'''
def drawGameState(screen, gs):
    drawBoard(screen) # draw squares on the board
    # add in piece highlighting or move suggestions (later)
    drawPieces(screen, gs.board) # draw pieces on top of those squares

'''
Draw squares on the board. The top left square is always light.
If you add up the x, y positions of a square and the result is even it's a light square, if odd it's a dark square
'''
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)] # if the remainder for division by 2 is 0 we will pick colors[0] (light color), if 1 we will pick colors[1] (dark color)
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draw the pieces on the board using the current GameState.board
'''
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": # not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))



if __name__ == "__main__":
    main()