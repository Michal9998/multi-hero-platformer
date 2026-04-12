import pygame
from settings import *

# Load player image safely
try:
    player_img = pygame.image.load("assets/player.png")
    player_img = pygame.transform.scale(player_img, (32, 64))
except:
    player_img = pygame.Surface((32, 64))
    player_img.fill(RED)

class Player:
    def __init__(self, start_x, start_y):
        self.image = player_img
        self.rect = pygame.Rect(start_x, start_y, 24, 60) 
        self.spawn_x = start_x
        self.spawn_y = start_y
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 5
        self.gravity = 0.5
        self.jump_power = -11
        self.on_ground = False

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed
        else:
            self.velocity_x = 0

        self.rect.x += self.velocity_x
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity_x > 0: 
                    self.rect.right = platform.left
                elif self.velocity_x < 0: 
                    self.rect.left = platform.right

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity_y > 0: 
                    self.rect.bottom = platform.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0: 
                    self.rect.top = platform.bottom
                    self.velocity_y = 0

    def jump(self):
        if self.on_ground or abs(self.velocity_y) < 1:
            self.velocity_y = self.jump_power

    def respawn(self):
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.velocity_y = 0

    def draw(self, surface, camera_x):
        img_rect = self.image.get_rect(center=self.rect.center)
        img_rect.x -= camera_x 
        surface.blit(self.image, img_rect)