# NOTE: Code, docstrings, and comments in this file were generated/refined with the assistance of AI.

"""
Level parsing and environment management module.

This module handles the loading of Tiled map files (.tmx), processing map layers,
extracting collision logic (hazards, deadly blocks, platforms), and rendering 
the static background environment. It also contains the logic for dynamic terrain,
specifically the FragilePlatform.
"""

import pytmx
import pygame
import random
from settings import *


class FragilePlatform:
    """
    A dynamic platform object that breaks a short time after being stepped on.
    
    Once broken, it loses its collision hitbox and disappears, 
    but will respawn after a set duration.
    """
    
    def __init__(self, x, y, width, height, image):
        """
        Initialize a new fragile platform instance.
        
        :param int x: The X-coordinate position of the platform.
        :param int y: The Y-coordinate position of the platform.
        :param int width: The width of the platform in pixels.
        :param int height: The height of the platform in pixels.
        :param pygame.Surface image: The graphic tile to render.
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.image = image
        
        # State variables
        self.is_touched = False
        self.is_broken = False
        
        # Timers
        self.touch_timer = 0
        self.respawn_timer = 0
        
        # Time values in frames (Assuming 60 FPS)
        self.break_time = 60    # 1 second until the platform breaks
        self.respawn_time = 180 # 3 seconds until it respawns

    def update(self, player_rect):
        """
        Update the state of the fragile platform.
        
        Checks for collision with the player, manages the countdown to breaking,
        and handles the automatic respawn sequence.
        
        :param pygame.Rect player_rect: A hitbox representing the area just beneath the player's feet.
        """
        if self.is_broken:
            # Handle respawn sequence
            self.respawn_timer += 1
            if self.respawn_timer >= self.respawn_time:
                self.is_broken = False
                self.is_touched = False
                self.touch_timer = 0
                self.respawn_timer = 0
        else:
            # Detect if the player steps on the platform
            if self.rect.colliderect(player_rect):
                self.is_touched = True
                
            # If touched, start the countdown to break
            if self.is_touched:
                self.touch_timer += 1
                if self.touch_timer >= self.break_time:
                    self.is_broken = True

    def draw(self, surface, camera_x, camera_y):
        """
        Draw the platform on the screen.
        
        If the platform is touched and close to breaking, a visual 
        "screen shake" effect is applied to warn the player.
        
        :param pygame.Surface surface: The surface to draw the platform on.
        :param int camera_x: The current X offset of the camera.
        :param int camera_y: The current Y offset of the camera.
        """
        if not self.is_broken:
            offset_x = 0
            offset_y = 0
            
            # Apply screen shake effect during the second half of its lifespan
            if self.is_touched and self.touch_timer > self.break_time // 2:
                offset_x = random.randint(-2, 2)
                offset_y = random.randint(-2, 2)
            
            surface.blit(self.image, (self.rect.x - camera_x + offset_x, self.rect.y - camera_y + offset_y))


def load_level(filename):
    """
    Parse a .tmx map file and extract environmental data for the game engine.
    
    This function reads layers from Tiled map editor files and categorizes tiles 
    into standard platforms, hazards (like spikes), deadly blocks (like acid), 
    and dynamic fragile platforms. It also finds key objects like spawn points.
    
    :param str filename: The file path to the .tmx map asset.
    :returns: A tuple containing:
        - tmx_data (pytmx.TiledMap): The raw map object (or None if failed).
        - platforms (list): A list of pygame.Rect objects for standard ground.
        - hazards (list): A list of pygame.Rect objects for hazards.
        - fragile_platforms (list): A list of instantiated FragilePlatform objects.
        - deadly_blocks (list): A list of pygame.Rect objects for instant death areas.
        - chest_rect (pygame.Rect): The hitbox of the level's exit/win condition.
        - spawn_pos (tuple): An (X, Y) coordinate tuple for player spawning.
    :rtype: tuple
    """
    # Load Tiled map data safely
    try:
        tmx_data = pytmx.load_pygame(filename, pixelalpha=True)
    except:
        return None, [], [], [], [], pygame.Rect(0,0,32,32), (100, 100)

    # Initialize environment lists
    platforms = []
    hazards = []
    fragile_platforms = []
    deadly_blocks = []
    
    # Default objects in case they are missing from the map
    chest_rect = pygame.Rect(0, 0, 32, 32)
    spawn_pos = (100, 100)

    # Parse map layers
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                if gid:
                    # Calculate true position based on tile dimensions
                    rect = pygame.Rect(x * tmx_data.tilewidth, y * tmx_data.tileheight, tmx_data.tilewidth, tmx_data.tileheight)
                    
                    # Sort tiles into logic arrays based on layer name
                    if layer.name == "Hazards":
                        hazards.append(rect)
                    elif layer.name == "Deadly":       
                        deadly_blocks.append(rect)
                    elif layer.name == "Fragile":
                        # Instantiate special FragilePlatform objects instead of raw Rects
                        img = tmx_data.get_tile_image_by_gid(gid)
                        fragile_platforms.append(FragilePlatform(rect.x, rect.y, rect.width, rect.height, img))
                    else:
                        platforms.append(rect)
                        
        elif isinstance(layer, pytmx.TiledObjectGroup):
            # Parse dynamic map objects (Spawn Point, Goal Chest)
            for obj in layer:
                if obj.name:
                    name_lower = obj.name.lower()
                    if name_lower == "chest":
                        chest_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    elif name_lower == "spawn":
                        spawn_pos = (obj.x, obj.y)

    return tmx_data, platforms, hazards, fragile_platforms, deadly_blocks, chest_rect, spawn_pos


def draw_level(surface, tmx_data, camera_x, camera_y):
    """
    Render static environment tiles onto the game surface.
    
    Iterates over all visible tile layers and draws them, shifting their position 
    based on the camera's coordinates. Note: The "Fragile" layer is skipped, 
    as those dynamic platforms render themselves.
    
    :param pygame.Surface surface: The target surface to draw the tiles on.
    :param pytmx.TiledMap tmx_data: The loaded map object containing tile logic.
    :param int camera_x: The X offset for rendering.
    :param int camera_y: The Y offset for rendering.
    """
    if not tmx_data: 
        return
    
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            # Skip drawing the Fragile layer, as FragilePlatforms render themselves in main.py
            if layer.name == "Fragile":
                continue
                
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    surface.blit(tile, (x * tmx_data.tilewidth - camera_x, y * tmx_data.tileheight - camera_y))