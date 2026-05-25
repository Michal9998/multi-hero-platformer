import pygame
import sys
from settings import *
from ui import Button
from player import Player
from level import load_level, draw_level

# --- INITIALIZATION & ASSETS ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hero Shift")

font = pygame.font.Font(None, 50)

# Load background
try:
    menu_bg = pygame.image.load("assets/menu_bg.png")
    menu_bg = pygame.transform.scale(menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    menu_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_bg.fill((50, 50, 80))

# Load chest image
try:
    chest_img = pygame.image.load("assets/chest.png")
    chest_img = pygame.transform.scale(chest_img, (32, 32))
except:
    chest_img = pygame.Surface((32, 32))
    chest_img.fill(GOLD)

def draw_centered_text(surface, text, font, color, y):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
    surface.blit(text_surf, text_rect)

def main():
    clock = pygame.time.Clock()
    current_state = "MENU"
    current_level = 1
    
    # Internal resolution for pixel-art scaling
    GAME_WIDTH = 640
    GAME_HEIGHT = 360
    game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    
    # --- UI ELEMENTS SETUP ---
    center_x = (SCREEN_WIDTH // 2) - 100 
    
    play_button = Button(center_x, 250, 200, 60, "Play")
    settings_button = Button(center_x, 350, 200, 60, "Settings")
    back_button = Button(center_x, 450, 200, 60, "Back to Menu")
    
    lvl_start_x = (SCREEN_WIDTH // 2) - 230
    
    lvl1_button = Button(lvl_start_x, 250, 100, 60, "Level 1", locked=False)
    lvl2_button = Button(lvl_start_x + 120, 250, 100, 60, "Level 2", locked=False) 
    lvl3_button = Button(lvl_start_x + 240, 250, 100, 60, "Level 3", locked=False)
    lvl4_button = Button(lvl_start_x + 360, 250, 100, 60, "Level 4", locked=False)
    lvl5_button = Button(lvl_start_x + 480, 250, 100, 60, "Level 5", locked=False)
    
    pause_btn = Button(20, 20, 100, 40, "Pause")
    resume_btn = Button(center_x, 300, 200, 60, "Resume")
    quit_to_menu_btn = Button(center_x, 400, 200, 60, "Exit to Menu")
    win_menu_btn = Button(center_x, 300, 200, 60, "Back to Menu")
    
    # Load default initial level
    level_data, platforms, hazards, fragile_platforms, deadly_blocks, chest_rect, spawn_pos = load_level("assets/level1.tmx")    
    player = Player(spawn_pos[0], spawn_pos[1])
    
    camera_x = 0
    camera_y = 0

    # --- MAIN GAME LOOP ---
    running = True
    while running:
        
        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if current_state == "MENU":
                if play_button.is_clicked(event):
                    current_state = "LEVEL_SELECT"
                if settings_button.is_clicked(event):
                    current_state = "SETTINGS"
                    
            elif current_state == "LEVEL_SELECT":
                if back_button.is_clicked(event):
                    current_state = "MENU"
                
                # Level loading logic
                if lvl1_button.is_clicked(event):
                    current_state = "PLAY"
                    current_level = 1
                    level_data, platforms, hazards, fragile_platforms, deadly_blocks, chest_rect, spawn_pos = load_level("assets/level1.tmx")
                    player.spawn_x, player.spawn_y = spawn_pos
                    player.respawn()
                
                if lvl2_button.is_clicked(event):
                    current_state = "PLAY"
                    current_level = 2
                    level_data, platforms, hazards, fragile_platforms, deadly_blocks, chest_rect, spawn_pos = load_level("assets/level2.tmx")
                    player.spawn_x, player.spawn_y = spawn_pos
                    player.respawn()
                    
                if lvl3_button.is_clicked(event):
                    current_state = "PLAY"
                    current_level = 3
                    level_data, platforms, hazards, fragile_platforms, deadly_blocks, chest_rect, spawn_pos = load_level("assets/level3.tmx")
                    player.spawn_x, player.spawn_y = spawn_pos
                    player.respawn()
                    
                if lvl4_button.is_clicked(event):
                    current_state = "PLAY"
                    current_level = 4
                    level_data, platforms, hazards, fragile_platforms, deadly_blocks, chest_rect, spawn_pos = load_level("assets/level4.tmx")
                    player.spawn_x, player.spawn_y = spawn_pos
                    player.respawn()  
                    
                if lvl5_button.is_clicked(event):
                    current_state = "PLAY"
                    current_level = 5
                    level_data, platforms, hazards, fragile_platforms, deadly_blocks, chest_rect, spawn_pos = load_level("assets/level5.tmx")
                    player.spawn_x, player.spawn_y = spawn_pos
                    player.respawn()
                    
            elif current_state == "SETTINGS":
                if back_button.is_clicked(event):
                    current_state = "MENU"
            
            elif current_state == "WIN":
                if win_menu_btn.is_clicked(event):
                    current_state = "LEVEL_SELECT"
                    
            elif current_state == "PLAY":
                if pause_btn.is_clicked(event):
                    current_state = "PAUSE"
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        current_state = "PAUSE"
                    
                    # Hero switching logic
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        if event.key == pygame.K_1: target_hero = "knight"
                        elif event.key == pygame.K_2: target_hero = "ninja"
                        elif event.key == pygame.K_3: target_hero = "miner"
                        
                        # Get active fragile blocks for collision check during switch
                        active_fragile_rects = [fp.rect for fp in fragile_platforms if not fp.is_broken]
                        solid_blocks = platforms + active_fragile_rects
                        
                        # Knight treats hazards (spikes) as solid ground
                        if target_hero == "knight":
                            solid_blocks.extend(hazards)
                            
                        player.switch_hero(target_hero, solid_blocks)
                        
                    if event.key in [pygame.K_UP, pygame.K_w, pygame.K_SPACE]:
                        player.jump()
                        
            elif current_state == "PAUSE":
                if resume_btn.is_clicked(event):
                    current_state = "PLAY"
                if quit_to_menu_btn.is_clicked(event):
                    current_state = "LEVEL_SELECT"
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        current_state = "PLAY"

        # --- GAME LOGIC & PHYSICS ---
        if current_state == "PLAY":
            
            # Sensor rect to detect platforms directly beneath the player
            sensor_rect = player.rect.move(0, 1)
            
            # Update fragile platforms
            active_fragile_rects = []
            for fp in fragile_platforms:
                fp.update(sensor_rect) 
                if not fp.is_broken:
                    active_fragile_rects.append(fp.rect)

            all_platforms = platforms + active_fragile_rects
            
            # Update player physics
            player.update(all_platforms, hazards)

            # Death mechanics: Deadly blocks
            death_hitbox = player.rect.inflate(-4, -4) 
            for d_rect in deadly_blocks:
                if death_hitbox.colliderect(d_rect):
                    player.respawn() 
            
            # Camera logic and win condition
            if level_data:
                map_width = level_data.width * level_data.tilewidth
                map_height = level_data.height * level_data.tileheight

                # Death mechanics: Falling off the map
                if player.rect.y > map_height + 100:
                    player.respawn()
                
                if player.rect.colliderect(chest_rect):
                    current_state = "WIN"

                # Camera clamping
                camera_x = player.rect.centerx - (GAME_WIDTH // 2)
                camera_y = player.rect.centery - (GAME_HEIGHT // 2)
                
                if camera_x < 0: camera_x = 0
                if camera_x > map_width - GAME_WIDTH: camera_x = map_width - GAME_WIDTH
                    
                if camera_y < 0: camera_y = 0
                if camera_y > map_height - GAME_HEIGHT: camera_y = map_height - GAME_HEIGHT

                # Center camera if map is smaller than the screen
                if map_width < GAME_WIDTH: camera_x = -(GAME_WIDTH - map_width) // 2
                if map_height < GAME_HEIGHT: camera_y = -(GAME_HEIGHT - map_height) // 2

        # --- RENDERING ---
        if current_state == "MENU":
            screen.blit(menu_bg, (0, 0))
            play_button.draw(screen)
            settings_button.draw(screen)
            
        elif current_state == "LEVEL_SELECT":
            screen.fill((70, 70, 100))
            draw_centered_text(screen, "Select Level", font, WHITE, 150)
            lvl1_button.draw(screen)
            lvl2_button.draw(screen)
            lvl3_button.draw(screen)
            lvl4_button.draw(screen)
            lvl5_button.draw(screen)
            back_button.draw(screen)
            
        elif current_state == "SETTINGS":
            screen.fill(DARK_GRAY)
            draw_centered_text(screen, "Settings Menu", font, WHITE, 150)
            back_button.draw(screen)
            
        elif current_state in ["PLAY", "PAUSE", "WIN"]:
            game_surface.fill(SKY_BLUE)
            
            # Draw level environment
            if level_data:
                draw_level(game_surface, level_data, camera_x, camera_y)
            
            for fp in fragile_platforms:
                fp.draw(game_surface, camera_x, camera_y)
                
            temp_chest_rect = chest_rect.copy()
            temp_chest_rect.x -= camera_x
            temp_chest_rect.y -= camera_y
            game_surface.blit(chest_img, temp_chest_rect)
            
            # Draw player
            player.draw(game_surface, camera_x, camera_y)
            
            # Scale up to screen resolution
            scaled_game = pygame.transform.scale(game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_game, (0, 0))
            
            # Draw UI overlays based on state
            if current_state == "PLAY":
                pause_btn.draw(screen)

                # Level 5 Easter Egg / Spooky Text
                if current_level == 5 and 800 < player.rect.x < 1600:
                    draw_centered_text(screen, "Do not trust your eyes...", font, RED, 100)
                
            elif current_state == "PAUSE":
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(150)
                overlay.fill(BLACK)
                screen.blit(overlay, (0, 0))
                
                draw_centered_text(screen, "GAME PAUSED", font, WHITE, 200)
                resume_btn.draw(screen)
                quit_to_menu_btn.draw(screen)
                
            elif current_state == "WIN":
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(150)
                overlay.fill(BLACK)
                screen.blit(overlay, (0, 0))
                
                draw_centered_text(screen, "Level Completed!", font, GOLD, 200)
                win_menu_btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()