import pygame
from settings import *

# Initialize font module
pygame.font.init()
small_font = pygame.font.Font(None, 36)

class Button:
    def __init__(self, x, y, width, height, text, locked=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.locked = locked
        self.color = DARK_GRAY if locked else GRAY
        self.hover_color = DARK_GRAY if locked else WHITE

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos) and not self.locked:
            pygame.draw.rect(surface, self.hover_color, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
            
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        text_surf = small_font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if self.locked:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False