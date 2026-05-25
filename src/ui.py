import pygame
from settings import *

# Initialize font module for UI elements
pygame.font.init()
small_font = pygame.font.Font(None, 36)

class Button:
    """
    A simple graphical user interface button that supports hover effects,
    click detection, and a 'locked' state for level progression.
    """
    def __init__(self, x, y, width, height, text, locked=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.locked = locked
        
        # Determine base and hover colors based on the locked state
        self.color = DARK_GRAY if locked else GRAY
        self.hover_color = DARK_GRAY if locked else WHITE

    def draw(self, surface):
        """
        Renders the button onto the given surface, applying hover effects
        if the mouse is over the button and it is not locked.
        """
        mouse_pos = pygame.mouse.get_pos()
        
        # Check for hover state
        if self.rect.collidepoint(mouse_pos) and not self.locked:
            pygame.draw.rect(surface, self.hover_color, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
            
        # Draw a black border around the button
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        # Render and center the text inside the button
        text_surf = small_font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        """
        Checks if the button was clicked.
        Returns True if a valid left-click occurred within the button's bounds.
        """
        # A locked button cannot be clicked
        if self.locked:
            return False
            
        # event.button == 1 corresponds to the left mouse button
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
                
        return False