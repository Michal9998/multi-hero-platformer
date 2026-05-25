import pytmx
import pygame
import random
from settings import *

class FragilePlatform:
    def __init__(self, x, y, width, height, image):
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
        if self.is_broken:
            # Handle respawn sequence
            self.respawn_timer += 1
            if self.respawn_timer >= self.respawn_time:
                self.is_broken = False
                self.is_touched = False
                self.touch_timer = 0
                self.respawn_timer = 0
        else:
            # Detect player collision
            if self.rect.colliderect(player_rect):
                self.is_touched = True
                
            # If touched, start the countdown to break
            if self.is_touched:
                self.touch_timer += 1
                if self.touch_timer >= self.break_time:
                    self.is_broken = True

    def draw(self, surface, camera_x, camera_y):
        if not self.is_broken:
            offset_x = 0
            offset_y = 0
            
            # Apply screen shake effect during the second half of its lifespan
            if self.is_touched and self.touch_timer > self.break_time // 2:
                offset_x = random.randint(-2, 2)
                offset_y = random.randint(-2, 2)
            
            surface.blit(self.image, (self.rect.x - camera_x + offset_x, self.rect.y - camera_y + offset_y))

def load_level(filename):
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
    if not tmx_data: return
    
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            # Skip drawing the Fragile layer, as FragilePlatforms render themselves in main.py
            if layer.name == "Fragile":
                continue
                
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    surface.blit(tile, (x * tmx_data.tilewidth - camera_x, y * tmx_data.tileheight - camera_y))