import pygame
import pytmx
from pytmx.util_pygame import load_pygame

def load_level(filename):
    platforms = []
    chest_rect = pygame.Rect(0, 0, 32, 32)
    try:
        tmx_data = load_pygame(filename)
        for layer in tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid != 0: 
                        platforms.append(pygame.Rect(x * 32, y * 32, 32, 32))
            
            elif isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    if obj.name == "Chest":
                        chest_rect = pygame.Rect(obj.x, obj.y, obj.width or 32, obj.height or 32)
                        
        return tmx_data, platforms, chest_rect
    except Exception as e:
        print(f"Error loading map: {e}")
        return None, [], chest_rect

def draw_level(surface, tmx_data, camera_x):
    if not tmx_data: return
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    surface.blit(tile, (x * tmx_data.tilewidth - camera_x, y * tmx_data.tileheight))