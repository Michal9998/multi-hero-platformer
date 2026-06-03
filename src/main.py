# NOTE: Code, docstrings, and comments in this file were generated/refined with the assistance of AI.

"""
Main module for the Hero Shift game.

This module initializes the Pygame engine, handles the main game loop,
manages the state machine (MENU, LEVEL_SELECT, PLAY, SETTINGS, PAUSE, WIN), 
and orchestrates the rendering and event handling for the entire game.
"""

import pygame
import sys
from settings import *
from ui import Button, Slider
from player import Player
from level import load_level, draw_level
import json
import os

# Ensure the executable looks for assets in its current directory (PyInstaller fix)
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

SAVE_FILE = "save_data.json"


def load_progress():
    """
    Load the player's level progress from the save file.

    Reads the JSON save file to determine the highest unlocked level.
    If the file does not exist or an error occurs, it defaults to level 1.

    :returns: The highest unlocked level number.
    :rtype: int
    """
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                return data.get("unlocked_level", 1)
        except:
            return 1
    return 1


def save_progress(level):
    """
    Save the player's level progress to the save file.

    Writes the newly unlocked level to a JSON file to persist progress
    between game sessions.

    :param int level: The highest level number that the player has unlocked.
    """
    with open(SAVE_FILE, "w") as f:
        json.dump({"unlocked_level": level}, f)


# --- INITIALIZATION & ASSETS ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hero Shift")

font = pygame.font.Font(None, 50)

# Load main menu background
try:
    menu_bg = pygame.image.load("assets/menu_bg.png")
    menu_bg = pygame.transform.scale(menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    menu_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_bg.fill((50, 50, 80))

# Load chest image (win condition object)
try:
    chest_img = pygame.image.load("assets/chest.png")
    chest_img = pygame.transform.scale(chest_img, (32, 32))
except:
    chest_img = pygame.Surface((32, 32))
    chest_img.fill(GOLD)

# Load settings and level selection background
try:
    settings_bg = pygame.image.load("assets/settings_bg.png").convert()
    settings_bg = pygame.transform.scale(settings_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    settings_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    settings_bg.fill(DARK_GRAY)

# --- AUDIO SETUP ---
try:
    pygame.mixer.music.load("assets/bg_music.ogg")
    pygame.mixer.music.set_volume(0.3)  # Default to 30% to prevent loud starts
    pygame.mixer.music.play(-1)         # -1 means loop indefinitely
except:
    print("Warning: bg_music.ogg not found or audio initialization failed.")


def draw_centered_text(surface, text, font, color, y):
    """
    Render and draw centered text on a given surface.

    :param pygame.Surface surface: The surface to draw the text on.
    :param str text: The string of text to display.
    :param pygame.font.Font font: The Pygame font object to use.
    :param tuple color: The RGB color tuple for the text.
    :param int y: The y-coordinate for the center of the text.
    """
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
    surface.blit(text_surf, text_rect)


def main():
    """
    The main game loop and entry point of the application.

    Initializes UI elements, handles the game state machine, processes
    player input, updates game physics, and renders graphics to the screen.
    """
    global screen
    clock = pygame.time.Clock()
    current_state = "MENU"
    current_level = 1
    
    # Internal resolution for pixel-art scaling (Maintains arcade feel)
    GAME_WIDTH = 640
    GAME_HEIGHT = 360
    game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    
    # Load saved game progress to determine unlocked levels
    unlocked_level = load_progress()

    # Audio control variables
    music_volume = 0.30
    is_music_on = True

    # --- UI ELEMENTS SETUP ---
    center_x = (SCREEN_WIDTH // 2) - 100 
    
    play_button = Button(center_x, 250, 200, 60, "Play")
    settings_button = Button(center_x, 350, 200, 60, "Settings")
    quit_button = Button(center_x, 450, 200, 60, "Quit")  
    back_button = Button(center_x, 550, 200, 60, "Back")
    
    lvl_start_x = (SCREEN_WIDTH // 2) - 290
    
    # Level button locks depend on the loaded save file progress
    lvl1_button = Button(lvl_start_x, 250, 100, 60, "Level 1", locked=False)
    lvl2_button = Button(lvl_start_x + 120, 250, 100, 60, "Level 2", locked=(unlocked_level < 2)) 
    lvl3_button = Button(lvl_start_x + 240, 250, 100, 60, "Level 3", locked=(unlocked_level < 3))
    lvl4_button = Button(lvl_start_x + 360, 250, 100, 60, "Level 4", locked=(unlocked_level < 4))
    lvl5_button = Button(lvl_start_x + 480, 250, 100, 60, "Level 5", locked=(unlocked_level < 5))
    
    pause_btn = Button(20, 20, 100, 40, "Pause")
    resume_btn = Button(center_x, 250, 200, 60, "Resume")
    pause_settings_btn = Button(center_x, 350, 200, 60, "Settings")
    quit_to_menu_btn = Button(center_x, 450, 200, 60, "Exit to Menu")
    win_menu_btn = Button(center_x, 300, 200, 60, "Back to Menu")

    # --- SETTINGS UI (Two-column layout) ---
    right_col_x = (SCREEN_WIDTH // 2) + 20  
    is_fullscreen = False
    fullscreen_btn = Button(right_col_x, 200, 300, 50, "Windowed") 
    music_toggle_btn = Button(right_col_x, 280, 300, 50, "ON")
    volume_slider = Slider(right_col_x, 380, 300, 10, 0.0, 1.0, music_volume)
    unlock_all_btn = Button(right_col_x, 440, 145, 50, "Unlock All")
    reset_save_btn = Button(right_col_x + 155, 440, 145, 50, "Reset Save")
    # ---------------------------------------
    
    # State tracking to ensure the 'Back' button in settings returns to the correct menu
    previous_state = "MENU"
    
    # Load default initial level (Level 1)
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
                    previous_state = "MENU"
                    current_state = "SETTINGS"
                if quit_button.is_clicked(event): 
                    running = False
                    
            elif current_state == "LEVEL_SELECT":
                if back_button.is_clicked(event):
                    current_state = "MENU"
                
                # Dynamic level loading logic
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
                    current_state = previous_state
                    
                if fullscreen_btn.is_clicked(event):
                    is_fullscreen = not is_fullscreen 
                    
                    if is_fullscreen:
                        # pygame.SCALED prevents Windows resolution distortion
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
                        fullscreen_btn.text = "Mode: Fullscreen"
                    else:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                        fullscreen_btn.text = "Mode: Windowed"
                        
                # Developer tools for progress management
                if unlock_all_btn.is_clicked(event):
                    unlocked_level = 5
                    save_progress(5)
                    lvl2_button.locked = lvl3_button.locked = lvl4_button.locked = lvl5_button.locked = False
                    
                if reset_save_btn.is_clicked(event):
                    unlocked_level = 1
                    save_progress(1)
                    lvl2_button.locked = lvl3_button.locked = lvl4_button.locked = lvl5_button.locked = True
                
                # --- AUDIO LOGIC ---
                if music_toggle_btn.is_clicked(event):
                    is_music_on = not is_music_on
                    if is_music_on:
                        pygame.mixer.music.unpause()
                        music_toggle_btn.text = "Music: ON"
                    else:
                        pygame.mixer.music.pause()
                        music_toggle_btn.text = "Music: OFF"

                # Handle slider dragging and update engine volume
                volume_slider.handle_event(event)
                if music_volume != volume_slider.val:
                    music_volume = volume_slider.val
                    pygame.mixer.music.set_volume(music_volume)
            
            elif current_state == "WIN":
                if win_menu_btn.is_clicked(event):
                    current_state = "LEVEL_SELECT"
                    
            elif current_state == "PLAY":
                if pause_btn.is_clicked(event):
                    current_state = "PAUSE"
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        current_state = "PAUSE"
                    
                    # Core Mechanic: Hero switching logic
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        if event.key == pygame.K_1: target_hero = "knight"
                        elif event.key == pygame.K_2: target_hero = "ninja"
                        elif event.key == pygame.K_3: target_hero = "miner"
                        
                        # Get active fragile blocks for collision check during switch
                        active_fragile_rects = [fp.rect for fp in fragile_platforms if not fp.is_broken]
                        solid_blocks = platforms + active_fragile_rects
                        
                        # Knight treats hazards (spikes) as solid walkable ground
                        if target_hero == "knight":
                            solid_blocks.extend(hazards)
                            
                        player.switch_hero(target_hero, solid_blocks)
                        
                    if event.key in [pygame.K_UP, pygame.K_w, pygame.K_SPACE]:
                        player.jump()
                        
            elif current_state == "PAUSE":
                if resume_btn.is_clicked(event):
                    current_state = "PLAY"
                if pause_settings_btn.is_clicked(event):
                    previous_state = "PAUSE"     
                    current_state = "SETTINGS"
                if quit_to_menu_btn.is_clicked(event):
                    current_state = "LEVEL_SELECT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        current_state = "PLAY"

        # --- GAME LOGIC & PHYSICS ---
        if current_state == "PLAY":
            
            # Sensor rect to detect platforms directly beneath the player
            sensor_rect = player.rect.move(0, 1)
            
            # Update fragile platforms based on player contact
            active_fragile_rects = []
            for fp in fragile_platforms:
                fp.update(sensor_rect) 
                if not fp.is_broken:
                    active_fragile_rects.append(fp.rect)

            all_platforms = platforms + active_fragile_rects
            
            # Update player physics
            player.update(all_platforms, hazards)

            # Death mechanics: Deadly blocks 
            # Inflate is used to make the death hitbox slightly forgiving
            death_hitbox = player.rect.inflate(-4, -4) 
            for d_rect in deadly_blocks:
                if death_hitbox.colliderect(d_rect):
                    player.respawn() 
            
            # Camera logic and win condition handling
            if level_data:
                map_width = level_data.width * level_data.tilewidth
                map_height = level_data.height * level_data.tileheight

                # Death mechanics: Falling off the map boundaries
                if player.rect.y > map_height + 100:
                    player.respawn()
                
                # Check for level completion
                if player.rect.colliderect(chest_rect):
                    current_state = "WIN"
                    
                    # Unlock the next level if the current one is the highest achieved
                    if current_level == unlocked_level and unlocked_level < 5:
                        unlocked_level += 1
                        save_progress(unlocked_level)
                        # Dynamically update the lock state on UI buttons
                        lvl2_button.locked = (unlocked_level < 2)
                        lvl3_button.locked = (unlocked_level < 3)
                        lvl4_button.locked = (unlocked_level < 4)
                        lvl5_button.locked = (unlocked_level < 5)

                # Smooth camera tracking (clamp to player position)
                camera_x = player.rect.centerx - (GAME_WIDTH // 2)
                camera_y = player.rect.centery - (GAME_HEIGHT // 2)
                
                # Restrict camera from showing areas outside the map boundaries
                if camera_x < 0: camera_x = 0
                if camera_x > map_width - GAME_WIDTH: camera_x = map_width - GAME_WIDTH
                    
                if camera_y < 0: camera_y = 0
                if camera_y > map_height - GAME_HEIGHT: camera_y = map_height - GAME_HEIGHT

                # Center the camera statically if the map is smaller than the screen
                if map_width < GAME_WIDTH: camera_x = -(GAME_WIDTH - map_width) // 2
                if map_height < GAME_HEIGHT: camera_y = -(GAME_HEIGHT - map_height) // 2

        # --- RENDERING ---
        if current_state == "MENU":
            screen.blit(menu_bg, (0, 0))
            play_button.draw(screen)
            settings_button.draw(screen)
            quit_button.draw(screen)
            
        elif current_state == "LEVEL_SELECT":
            screen.blit(settings_bg, (0, 0)) 
            draw_centered_text(screen, "Select Level", font, WHITE, 150)
            lvl1_button.draw(screen)
            lvl2_button.draw(screen)
            lvl3_button.draw(screen)
            lvl4_button.draw(screen)
            lvl5_button.draw(screen)
            back_button.draw(screen)
            
        elif current_state == "SETTINGS":
            screen.blit(settings_bg, (0, 0))
            draw_centered_text(screen, "Settings Menu", font, WHITE, 100)
            
            # --- DRAW LEFT COLUMN LABELS ---
            label_font = pygame.font.Font(None, 45)
            
            def draw_label(text, y):
                txt_surf = label_font.render(text, True, WHITE)
                # Align text to the right edge of the left column (center of the screen)
                txt_rect = txt_surf.get_rect(midright=((SCREEN_WIDTH // 2) - 10, y + 25))
                screen.blit(txt_surf, txt_rect)

            draw_label("Display Mode:", 200)
            draw_label("Background Music:", 280)
            
            display_vol = int(round(music_volume * 100))
            draw_label(f"Music Volume: {display_vol}%", 360)
            
            draw_label("Game Progress:", 440)

            # --- DRAW RIGHT COLUMN INTERACTIVE ELEMENTS ---
            fullscreen_btn.draw(screen)
            music_toggle_btn.draw(screen)
            volume_slider.draw(screen)
            unlock_all_btn.draw(screen)
            reset_save_btn.draw(screen)
            
            back_button.draw(screen)
            
        elif current_state in ["PLAY", "PAUSE", "WIN"]:
            game_surface.fill(SKY_BLUE)
            
            # Draw level environment (tiles)
            if level_data:
                draw_level(game_surface, level_data, camera_x, camera_y)
            
            # Draw interactive dynamic objects
            for fp in fragile_platforms:
                fp.draw(game_surface, camera_x, camera_y)
                
            temp_chest_rect = chest_rect.copy()
            temp_chest_rect.x -= camera_x
            temp_chest_rect.y -= camera_y
            game_surface.blit(chest_img, temp_chest_rect)
            
            # Draw player entity
            player.draw(game_surface, camera_x, camera_y)
            
            # Scale the low-res game surface up to the native screen resolution
            scaled_game = pygame.transform.scale(game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_game, (0, 0))
            
            # Draw UI overlays on top of the rendered game frame
            if current_state == "PLAY":
                pause_btn.draw(screen)

                # Level 5 Easter Egg / Spooky Text trigger
                if current_level == 5 and 300 < player.rect.x < 700:
                    draw_centered_text(screen, "Do not trust your eyes...", font, RED, 100)
                
            elif current_state == "PAUSE":
                # Create a semi-transparent dark overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(150)
                overlay.fill(BLACK)
                screen.blit(overlay, (0, 0))
                
                draw_centered_text(screen, "GAME PAUSED", font, WHITE, 200)
                resume_btn.draw(screen)
                pause_settings_btn.draw(screen)
                quit_to_menu_btn.draw(screen)
                
            elif current_state == "WIN":
                # Create a semi-transparent dark overlay for the victory screen
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