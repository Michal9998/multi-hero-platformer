# NOTE: Code, docstrings, and comments in this file were generated/refined with the assistance of AI.

"""
Settings and constants module for the Hero Shift game.

This module contains global configuration variables used throughout the project, 
including the main window dimensions and standard RGB color definitions. 
Keeping these values centralized ensures consistency and makes global visual tweaks easier.
"""

import pygame

# --- SCREEN CONFIGURATION ---
# The default logical resolution of the game window
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# --- COLOR DEFINITIONS (RGB Tuples) ---
# Standard colors used for text, borders, and general UI elements
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Specific colors used for character placeholders and environmental features
RED = (200, 50, 50)         # Placeholder color for the Knight hero
GREEN = (50, 200, 50)       # Placeholder color for the Ninja hero
SKY_BLUE = (135, 206, 235)  # Background color used during the 'PLAY' state
GOLD = (255, 215, 0)        # Goal chest, victory text, and placeholder for the Miner hero