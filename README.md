# Hero Shift - Early Demo

## Project Description
**Hero Shift** is a 2D platformer built in Python, where the core mechanic revolves around switching between three heroes with unique abilities (Ninja, Guard, Engineer). The project focuses on utilizing a state machine for game management and maintaining a modular code architecture.

## Current Progress (First Demo)
At the current stage, the following features have been implemented:
* **Menu System:** Main menu powered by a state machine (Menu, Level Select, Settings, Play, Win).
* **Physics and Movement:** Basic character movement, gravity, jumping system, and collision detection.
* **Map System:** Loading levels from the `.tmx` format (Tiled Map Editor).
* **Camera:** Dynamic camera following the player (Smooth Scrolling).
* **Visuals:** Implementation of custom background graphics (1280x720) and level tiles.
* **Win Mechanic:** Object system on the map (chest) that triggers the level completion screen.

## Technologies and Tools
* **Language:** Python 3.12+
* **Libraries:** Pygame-CE, PyTMX.
* **Graphics:** Canva (UI & Background), Piskel (Pixel Art Assets).
* **Map Editor:** Tiled Map Editor.
* **IDE:** Visual Studio Code.

## How to Run the Game
1. Ensure you have Python 3.12 or newer installed.
2. Install the required libraries:
   ```bash
   pip install -r requirements.txt
3. Run the game: python src/main.py

## Controls
* ** A / D or Arrow Keys: Move left/right.

* ** W / Spacebar or Up Arrow: Jump.

* ** ESC: Return to menu / Level selection.
