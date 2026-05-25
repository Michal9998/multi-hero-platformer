import pygame
from settings import *

class Player:
    def __init__(self, start_x, start_y):
        # Define distinct properties for each hero class
        self.hero_data = {
            "knight": {"size": (22, 54), "jumps": 1, "img_path": "assets/knight.png"},
            "ninja":  {"size": (22, 54), "jumps": 2, "img_path": "assets/ninja.png"},
            "miner":  {"size": (22, 31), "jumps": 1, "img_path": "assets/miner.png"}
        }
        
        # Load hero assets with colored rectangle fallbacks
        self.images = {}
        for name, data in self.hero_data.items():
            try:
                img = pygame.image.load(data["img_path"]).convert_alpha()
                self.images[name] = pygame.transform.scale(img, data["size"])
            except:
                self.images[name] = pygame.Surface(data["size"])
                color = RED if name == "knight" else GREEN if name == "ninja" else GOLD
                self.images[name].fill(color)

        # Set initial hero and hitbox
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
        
        # Jump tracking for multi-jump mechanics
        self.max_jumps = self.hero_data[self.current_hero]["jumps"]
        self.jumps_used = 0
        self.on_ground = False

    def switch_hero(self, hero_type, solid_blocks):
        if hero_type == self.current_hero: return
        
        new_w, new_h = self.hero_data[hero_type]["size"]
        
        # Create a test hitbox to ensure the new hero won't get stuck in walls
        test_rect = pygame.Rect(0, 0, new_w, new_h)
        test_rect.bottom = self.rect.bottom
        test_rect.centerx = self.rect.centerx
        
        for block in solid_blocks:
            if test_rect.colliderect(block):
                return  # Abort switch if the new hitbox collides with terrain
        
        # Apply new hero properties
        self.current_hero = hero_type
        self.image = self.images[hero_type]
        self.max_jumps = self.hero_data[hero_type]["jumps"]
        self.rect = test_rect

    def update(self, platforms, hazards):
        # The Knight ignores hazards (treats them as solid ground)
        solid_blocks = platforms.copy()
        if self.current_hero == "knight":
            solid_blocks.extend(hazards)

        # Handle horizontal movement input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed
        else:
            self.velocity_x = 0

        # Apply horizontal movement and resolve X-axis collisions
        self.rect.x += self.velocity_x
        for block in solid_blocks:
            if self.rect.colliderect(block):
                if self.velocity_x > 0: self.rect.right = block.left
                elif self.velocity_x < 0: self.rect.left = block.right

        # Apply gravity and resolve Y-axis collisions
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        self.on_ground = False

        for block in solid_blocks:
            if self.rect.colliderect(block):
                if self.velocity_y > 0: 
                    self.rect.bottom = block.top
                    self.velocity_y = 0
                    self.on_ground = True
                    self.jumps_used = 0  # Reset jumps upon landing
                elif self.velocity_y < 0: 
                    self.rect.top = block.bottom
                    self.velocity_y = 0

        # Handle death logic for non-Knight characters
        if self.current_hero != "knight":
            for hazard in hazards:
                if self.rect.colliderect(hazard):
                    self.respawn()

    def jump(self):
        # Allow jump if the hero hasn't exhausted their jump limit
        if self.jumps_used < self.max_jumps:
            self.velocity_y = self.jump_power
            self.jumps_used += 1
            self.on_ground = False

    def respawn(self):
        # Reset player to the start of the level
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.velocity_y = 0
        self.jumps_used = 0

    def draw(self, surface, camera_x, camera_y):
        # Render the player taking camera offset into account
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))