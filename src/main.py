import pygame
import sys
from settings import *
from ui import Button
from player import Player
from level import load_level, draw_level

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hero Shift")

font = pygame.font.Font(None, 50)

try:
    menu_bg = pygame.image.load("assets/menu_bg.png")
    menu_bg = pygame.transform.scale(menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    menu_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_bg.fill((50, 50, 80))

try:
    chest_img = pygame.image.load("assets/chest.png")
    chest_img = pygame.transform.scale(chest_img, (32, 32))
except:
    chest_img = pygame.Surface((32, 32))
    chest_img.fill(GOLD)

# Funkcja pomocnicza do centrowania napisów
def draw_centered_text(surface, text, font, color, y):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
    surface.blit(text_surf, text_rect)

def main():
    clock = pygame.time.Clock()
    current_state = "MENU"
    
    # Matematyka centrowania przycisków
    center_x = (SCREEN_WIDTH // 2) - 100 # 100 to połowa szerokości przycisku (200)
    
    # UI Buttons
    play_button = Button(center_x, 250, 200, 60, "Play")
    settings_button = Button(center_x, 350, 200, 60, "Settings")
    back_button = Button(center_x, 450, 200, 60, "Back to Menu")
    
    # Przyciski poziomów wycentrowane jako blok
    lvl_start_x = (SCREEN_WIDTH // 2) - 230
    lvl1_button = Button(lvl_start_x, 250, 100, 60, "Level 1", locked=False)
    lvl2_button = Button(lvl_start_x + 120, 250, 100, 60, "Level 2", locked=True)
    lvl3_button = Button(lvl_start_x + 240, 250, 100, 60, "Level 3", locked=True)
    lvl4_button = Button(lvl_start_x + 360, 250, 100, 60, "Level 4", locked=True)
    
    # New Buttons
    in_game_menu_btn = Button(20, 20, 100, 40, "Menu")
    win_menu_btn = Button(center_x, 300, 200, 60, "Back to Menu")
    
    player = Player(100, 100)
    level_data, platforms, chest_rect = load_level("assets/level1.tmx")
    camera_x = 0

    running = True
    while running:
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
                if lvl1_button.is_clicked(event):
                    current_state = "PLAY"
                    level_data, platforms, chest_rect = load_level("assets/level1.tmx")
                    player.respawn()
                    
            elif current_state == "SETTINGS":
                if back_button.is_clicked(event):
                    current_state = "MENU"
            
            elif current_state == "WIN":
                if win_menu_btn.is_clicked(event):
                    current_state = "LEVEL_SELECT"
                    
            elif current_state == "PLAY":
                if in_game_menu_btn.is_clicked(event):
                    current_state = "LEVEL_SELECT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        current_state = "LEVEL_SELECT"
                    if event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_SPACE:
                        player.jump()

        # --- LOGIC UPDATES ---
        if current_state == "PLAY":
            player.update(platforms)

            if player.rect.y > SCREEN_HEIGHT + 100:
                player.respawn()
                
            if player.rect.colliderect(chest_rect):
                current_state = "WIN"

            camera_x = player.rect.centerx - (SCREEN_WIDTH // 2)
            if camera_x < 0:
                camera_x = 0

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
            back_button.draw(screen)
            
        elif current_state == "SETTINGS":
            screen.fill(DARK_GRAY)
            draw_centered_text(screen, "Settings Menu", font, WHITE, 150)
            back_button.draw(screen)
            
        elif current_state in ["PLAY", "WIN"]:
            screen.fill(SKY_BLUE)
            
            if level_data:
                draw_level(screen, level_data, camera_x)
                
            adjusted_chest_rect = chest_rect.copy()
            adjusted_chest_rect.x -= camera_x
            screen.blit(chest_img, adjusted_chest_rect)
            
            player.draw(screen, camera_x)
            
            if current_state == "PLAY":
                in_game_menu_btn.draw(screen)
                
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