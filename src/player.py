# NOTE: Code, docstrings, and comments in this file were generated/refined with the assistance of AI.

"""
Player module containing the logic for the playable character.

This module defines the Player class, which handles movement, physics, 
hero switching mechanics, and rendering for the game's protagonist.
"""

import pygame
from settings import *

class Player:
    """
    Represents the player character in the game.
    
    Manages the state, physics, and abilities of the currently selected hero 
    (Knight, Ninja, or Miner), including collision detection and jumping.
    """
    
    def __init__(self, start_x, start_y):
        """
        Initialize the player character at the given starting coordinates.
        
        :param int start_x: The initial X-coordinate spawn position.
        :param int start_y: The initial Y-coordinate spawn position.
        """
        # Define distinct properties for each hero class
        self.hero_data = {
            "knight": {"size": (22, 54), "jumps": 1, "img_path": "assets/knight.png"},
            "ninja":  {"size": (22, 54), "jumps": 2, "img_path": "assets/ninja.png"},
            "miner":  {"size": (22, 31), "jumps": 1, "img_path": "assets/miner.png"}
        }
        
        # Load hero assets with colored rectangle fallbacks in case images are missing
        self.images = {}
        for name, data in self.hero_data.items():
            try:
                img = pygame.image.load(data["img_path"]).convert_alpha()
                self.images[name] = pygame.transform.scale(img, data["size"])
            except:
                self.images[name] = pygame.Surface(data["size"])
                color = RED if name == "knight" else GREEN if name == "ninja" else GOLD
                self.images[name].fill(color)

        # Set initial hero and bounding box (hitbox)
        self.current_hero = "knight"
        self.image = self.images[self.current_hero]
        
        width, height = self.hero_data[self.current_hero]["size"]
        self.rect = pygame.Rect(start_x, start_y, width, height)
        
        # Initialization of physics and state variables
        self.spawn_x = start_x
        self.spawn_y = start_y
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 5
        self.gravity = 0.6
        self.jump_power = -9
        
        # Jump tracking for multi-jump mechanics (e.g., Ninja's double jump)
        self.max_jumps = self.hero_data[self.current_hero]["jumps"]
        self.jumps_used = 0
        self.on_ground = False

    def switch_hero(self, hero_type, solid_blocks):
        """
        Attempt to switch the current hero to a new type.
        
        Checks if the new hero's hitbox would collide with any solid blocks 
        before confirming the switch to prevent the player from getting stuck inside walls.
        
        :param str hero_type: The name of the hero to switch to ('knight', 'ninja', 'miner').
        :param list solid_blocks: A list of pygame.Rect objects representing solid terrain.
        """
        if hero_type == self.current_hero: 
            return
        
        new_w, new_h = self.hero_data[hero_type]["size"]
        
        # Create a test hitbox aligned to the bottom center of the current player
        test_rect = pygame.Rect(0, 0, new_w, new_h)
        test_rect.bottom = self.rect.bottom
        test_rect.centerx = self.rect.centerx
        
        # Verify that the new hitbox does not overlap with existing terrain
        for block in solid_blocks:
            if test_rect.colliderect(block):
                return  # Abort switch if the new hitbox collides with terrain
        
        # Apply new hero properties if the area is clear
        self.current_hero = hero_type
        self.image = self.images[hero_type]
        self.max_jumps = self.hero_data[hero_type]["jumps"]
        self.rect = test_rect

    def update(self, platforms, hazards):
        """
        Update the player's position, apply physics, and handle collisions.
        
        Calculates horizontal movement based on user input, applies gravity, 
        resolves collisions with terrain, and checks for hazards.
        
        :param list platforms: A list of pygame.Rect objects representing normal solid ground.
        :param list hazards: A list of pygame.Rect objects representing dangerous terrain (e.g., spikes).
        """
        # The Knight is heavily armored and ignores hazards (treats them as solid ground)
        solid_blocks = platforms.copy()
        if self.current_hero == "knight":
            solid_blocks.extend(hazards)

        # Handle horizontal movement input (Arrow keys or A/D)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed
        else:
            self.velocity_x = 0

        # Apply horizontal movement and instantly resolve X-axis collisions
        self.rect.x += self.velocity_x
        for block in solid_blocks:
            if self.rect.colliderect(block):
                if self.velocity_x > 0: 
                    self.rect.right = block.left
                elif self.velocity_x < 0: 
                    self.rect.left = block.right

        # Apply gravity and instantly resolve Y-axis collisions
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        self.on_ground = False

        for block in solid_blocks:
            if self.rect.colliderect(block):
                # Player is falling and hits the ground
                if self.velocity_y > 0: 
                    self.rect.bottom = block.top
                    self.velocity_y = 0
                    self.on_ground = True
                    self.jumps_used = 0  # Reset available jumps upon landing
                # Player is jumping and hits a ceiling
                elif self.velocity_y < 0: 
                    self.rect.top = block.bottom
                    self.velocity_y = 0

        # Handle death logic for non-Knight characters
        if self.current_hero != "knight":
            for hazard in hazards:
                if self.rect.colliderect(hazard):
                    self.respawn()

    def jump(self):
        """
        Execute a jump action if the hero has remaining jumps available.
        
        This method fully supports both standard single jumps and multi-jumps 
        (like the Ninja's double jump mechanism).
        """
        # Allow jump if the hero hasn't exhausted their jump limit
        if self.jumps_used < self.max_jumps:
            self.velocity_y = self.jump_power
            self.jumps_used += 1
            self.on_ground = False

    def respawn(self):
        """
        Reset the player's position to the initial level spawn point.
        
        This is typically called when the player falls off the map or touches a hazard.
        It also resets vertical velocity and jump counters to prevent floating.
        """
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.velocity_y = 0
        self.jumps_used = 0

    def draw(self, surface, camera_x, camera_y):
        """
        Draw the player entity onto the specified surface.
        
        Adjusts the visual position of the player based on the current camera offset 
        to simulate a scrolling world.
        
        :param pygame.Surface surface: The Pygame surface to draw the player on.
        :param int camera_x: The current X offset of the camera.
        :param int camera_y: The current Y offset of the camera.
        """
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))