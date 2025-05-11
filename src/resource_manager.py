import pygame as p
from src.constants import GameConstants

# Global dictionary mapping piece identifiers to their image resources
IMAGES = {}

class ResourceManager:
    """
    Manages loading and scaling of game resources, specifically piece images.
    
    This class provides static methods to load chess piece images from the images directory
    and scale them to the appropriate size for the game board.
    """
    
    @staticmethod
    def load_images():
        """
        Load and scale chess piece images into the global IMAGES dictionary.
        
        Loads PNG images for all chess pieces from the images directory and scales them
        to match the square size defined in GameConstants. Images are stored in the global
        IMAGES dictionary with keys matching piece identifiers (e.g., 'wK' for white king).
        
        The following pieces are loaded:
        - White pieces: pawn (wp), rook (wR), knight (wN), bishop (wB), king (wK), queen (wQ)
        - Black pieces: pawn (bp), rook (bR), knight (bN), bishop (bB), king (bK), queen (bQ)
        """
        pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
        for piece in pieces:
            IMAGES[piece] = p.transform.scale(
                p.image.load("images/" + piece + ".png"), 
                (int(GameConstants.SQ_SIZE), int(GameConstants.SQ_SIZE))
            )