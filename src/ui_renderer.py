import pygame as p
from src.constants import GameConstants, UIConstants

class UIRenderer:
    def __init__(self, screen):
        self.screen = screen

    def draw_game_state(self, gs, sq_selected):
        """Responsible for all the graphics within a current game state."""
        self.draw_board()  # draw squares on the board
        if sq_selected != ():  # if a square is selected
            self.highlight_square(sq_selected)
        self.draw_pieces(gs.board)  # draw pieces on top of those squares
        
        # Draw game state messages after everything else
        if gs.checkmate:
            text = f"Checkmate! {'Black' if gs.whiteToMove else 'White'} wins!"
            self.draw_text(text)
        elif gs.stalemate:
            self.draw_text("Stalemate!")
        elif gs.in_check:
            text = f"{'White' if gs.whiteToMove else 'Black'} is in check!"
            self.draw_text(text)

    def highlight_square(self, square):
        """Highlight the selected square with a red border"""
        if square != ():  # if square is selected
            row, col = square
            s = p.Surface((int(GameConstants.SQ_SIZE), int(GameConstants.SQ_SIZE)))
            s.set_alpha(UIConstants.TRANSPARENCY_ALPHA)
            s.fill(p.Color('red'))
            self.screen.blit(s, (col * int(GameConstants.SQ_SIZE), row * int(GameConstants.SQ_SIZE)))
            # Draw border
            p.draw.rect(self.screen, p.Color('red'), 
                       p.Rect(col * int(GameConstants.SQ_SIZE), row * int(GameConstants.SQ_SIZE), 
                             int(GameConstants.SQ_SIZE), int(GameConstants.SQ_SIZE)), 
                       UIConstants.BORDER_WIDTH)

    def draw_board(self):
        """Draw squares on the board. The top left square is always light."""
        colors = [p.Color("white"), p.Color("gray")]
        for r in range(int(GameConstants.DIMENSION)):
            for c in range(int(GameConstants.DIMENSION)):
                color = colors[((r + c) % 2)]
                p.draw.rect(
                    self.screen, color, 
                    p.Rect(c * int(GameConstants.SQ_SIZE), r * int(GameConstants.SQ_SIZE), 
                          int(GameConstants.SQ_SIZE), int(GameConstants.SQ_SIZE))
                )

    def draw_pieces(self, board):
        """Draw the pieces on the board using the current GameState.board"""
        from src.resource_manager import IMAGES
        for r in range(int(GameConstants.DIMENSION)):
            for c in range(int(GameConstants.DIMENSION)):
                piece = board[r][c]
                if piece != "--":  # not empty square
                    self.screen.blit(
                        IMAGES[piece], 
                        p.Rect(c * int(GameConstants.SQ_SIZE), r * int(GameConstants.SQ_SIZE), 
                              int(GameConstants.SQ_SIZE), int(GameConstants.SQ_SIZE))
                    )

    def draw_text(self, text):
        """Draw text in the center of the screen"""
        font = p.font.Font(None, 36)
        text_surface = font.render(text, True, p.Color('black'))
        text_rect = text_surface.get_rect()
        text_rect.center = (int(GameConstants.WIDTH) // 2, int(GameConstants.HEIGHT) // 2)
        self.screen.blit(text_surface, text_rect)

    def show_promotion_dialog(self, is_white_turn):
        """Show dialog for pawn promotion piece selection"""
        from src.resource_manager import IMAGES
        dialog_width = int(GameConstants.SQ_SIZE) * UIConstants.PROMOTION_DIALOG_WIDTH_SQUARES
        dialog_height = int(GameConstants.SQ_SIZE) * UIConstants.PROMOTION_DIALOG_HEIGHT_SQUARES
        dialog_x = (int(GameConstants.WIDTH) - dialog_width) // 2
        dialog_y = (int(GameConstants.HEIGHT) - dialog_height) // 2
        
        # Draw dialog background
        dialog_surface = p.Surface((dialog_width, dialog_height))
        dialog_surface.fill(p.Color('white'))
        p.draw.rect(dialog_surface, p.Color('black'), 
                   p.Rect(0, 0, dialog_width, dialog_height), UIConstants.BORDER_WIDTH)
        
        # Available pieces for promotion
        color_prefix = 'w' if is_white_turn else 'b'
        pieces = ['Q', 'R', 'B', 'N']
        piece_rects = []
        
        # Draw piece options
        for i, piece in enumerate(pieces):
            piece_img = IMAGES[color_prefix + piece]
            x = i * int(GameConstants.SQ_SIZE)
            piece_rects.append(p.Rect(dialog_x + x, dialog_y, 
                                    int(GameConstants.SQ_SIZE), int(GameConstants.SQ_SIZE)))
            dialog_surface.blit(piece_img, (x, 0))
        
        self.screen.blit(dialog_surface, (dialog_x, dialog_y))
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