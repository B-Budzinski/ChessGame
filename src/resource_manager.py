import pygame as p
from src.constants import GameConstants

# Global dictionary of images
IMAGES = {}

class ResourceManager:
    @staticmethod
    def load_images():
        """Initialize a global dictionary of images."""
        pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
        for piece in pieces:
            IMAGES[piece] = p.transform.scale(
                p.image.load("images/" + piece + ".png"), 
                (int(GameConstants.SQ_SIZE), int(GameConstants.SQ_SIZE))
            )