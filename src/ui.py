# NOTE: Code, docstrings, and comments in this file were generated/refined with the assistance of AI.

"""
User Interface module for interactive elements.

This module provides reusable UI components such as buttons and sliders
that handle their own rendering, state (like hover/locked), and input events.
"""

import pygame
from settings import *

# Initialize font module for UI elements
pygame.font.init()
small_font = pygame.font.Font(None, 36)

class Button:
    """
    A simple graphical user interface button.
    
    Supports hover visual effects, click detection, and a 'locked' state 
    which visually disables the button and ignores clicks (useful for level progression).
    """
    def __init__(self, x, y, width, height, text, locked=False):
        """
        Initialize a new button instance.
        
        :param int x: The X-coordinate for the top-left corner of the button.
        :param int y: The Y-coordinate for the top-left corner of the button.
        :param int width: The width of the button in pixels.
        :param int height: The height of the button in pixels.
        :param str text: The text label to display on the button.
        :param bool locked: If True, the button is rendered in gray and cannot be clicked.
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.locked = locked

    def draw(self, surface):
        """
        Render the button onto the given surface. 
        
        Colors are dynamically evaluated during each frame so they update 
        immediately if the locked state is changed externally.
        
        :param pygame.Surface surface: The target surface to draw the button on.
        """
        # Dynamic color selection based on the current locked state
        current_base_color = DARK_GRAY if self.locked else GRAY
        current_hover_color = DARK_GRAY if self.locked else WHITE

        mouse_pos = pygame.mouse.get_pos()
        
        # Check for hover state and apply hover color if not locked
        if self.rect.collidepoint(mouse_pos) and not self.locked:
            pygame.draw.rect(surface, current_hover_color, self.rect)
        else:
            pygame.draw.rect(surface, current_base_color, self.rect)
            
        # Draw a black border around the button for better visibility
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        # Render and center the text inside the button boundaries
        text_surf = small_font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        """
        Check if the button was clicked by the user.
        
        :param pygame.event.Event event: A Pygame event object to evaluate.
        :returns: True if a valid left-click occurred within bounds and the button is unlocked.
        :rtype: bool
        """
        # A locked button cannot trigger a click event
        if self.locked:
            return False
            
        # event.button == 1 corresponds to the left mouse button
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
                
        return False
    
class Slider:
    """
    A custom slider UI element to control float values smoothly.
    
    Particularly useful for settings like volume control, allowing the player 
    to click and drag a handle along a track.
    """
    def __init__(self, x, y, width, height, min_val, max_val, start_val):
        """
        Initialize a new slider instance.
        
        :param int x: The X-coordinate for the left edge of the slider track.
        :param int y: The Y-coordinate for the top edge of the slider track.
        :param int width: The total width of the slider track.
        :param int height: The thickness (height) of the slider track.
        :param float min_val: The minimum value (leftmost position).
        :param float max_val: The maximum value (rightmost position).
        :param float start_val: The initial value of the slider.
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = start_val
        self.is_dragging = False
        
        # Determine the radius of the draggable circle handle
        self.handle_radius = int(height * 1.2) 
        self.update_handle_pos()

    def update_handle_pos(self):
        """
        Calculate and update the physical X-coordinate of the handle 
        based on the slider's current logical value.
        """
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_x = self.rect.x + int(ratio * self.rect.width)

    def draw(self, surface):
        """
        Render the slider track, the filled portion, and the handle.
        
        :param pygame.Surface surface: The target surface to draw the slider on.
        """
        # Draw the background track of the slider (dark gray)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, border_radius=self.rect.height//2)
        
        # Draw the 'filled' active portion of the slider (blue)
        filled_rect = pygame.Rect(self.rect.x, self.rect.y, self.handle_x - self.rect.x, self.rect.height)
        pygame.draw.rect(surface, SKY_BLUE, filled_rect, border_radius=self.rect.height//2)
        
        # Draw the white circular handle that the player drags
        pygame.draw.circle(surface, WHITE, (self.handle_x, self.rect.centery), self.handle_radius)
        pygame.draw.circle(surface, BLACK, (self.handle_x, self.rect.centery), self.handle_radius, 2)

    def handle_event(self, event):
        """
        Process mouse events to handle the dragging mechanics of the slider.
        
        Evaluates mouse clicks, releases, and motion to update the slider's state.
        
        :param pygame.event.Event event: A Pygame event object to evaluate.
        """
        # Grabbing the slider handle with the left mouse button
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Create a vertically inflated hitbox to make it easier to click
            hitbox = self.rect.inflate(0, self.handle_radius * 4) 
            if hitbox.collidepoint(event.pos):
                self.is_dragging = True
                self.update_value_from_pos(event.pos[0])
                
        # Releasing the mouse button drops the handle
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False
            
        # Dragging the mouse while holding the button
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self.update_value_from_pos(event.pos[0])

    def update_value_from_pos(self, mouse_x):
        """
        Recalculate the slider's logical value based on the mouse's physical X-coordinate.
        
        :param int mouse_x: The current X-coordinate of the mouse cursor.
        """
        # Clamp the mouse X position to prevent the handle from going out of bounds
        mouse_x = max(self.rect.left, min(mouse_x, self.rect.right))
        
        # Calculate ratio and map it back to the value range
        ratio = (mouse_x - self.rect.left) / self.rect.width
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
        
        # Force the handle position to visually update
        self.update_handle_pos()