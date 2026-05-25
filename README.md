# Hero Shift - Demo 2

## Project Description
Hero Shift is a 2D platformer built in Python, where the core mechanic revolves around dynamically switching between three heroes with unique abilities (Knight, Ninja, Miner). The project focuses on utilizing a robust state machine for game management, a modular OOP code architecture, and intricate level design using Tiled Map Editor.

## Current Progress (Demo 2)

At the current stage, the core gameplay loop has been fully realized with the following features:

* **Dynamic Hero Switching:** Players can swap between three distinct classes on the fly:
    * **Knight:** A heavy tank with a single jump who treats standard hazards (spikes) as solid, walkable ground.
    * **Ninja:** An agile character equipped with a double jump to reach high platforms.
    * **Miner:** A compact character with a smaller hitbox to fit through tight spaces (single jump).
* **Advanced Obstacles & Interactions:**
    * **Hazards:** Spikes that kill standard characters upon touch.
    * **Fragile Platforms:** Blocks that tremble upon contact, break after a set duration, and respawn dynamically.
    * **Deadly Blocks:** Instant-kill zones that eliminate any character, regardless of class.
* **Expanded Level Design:** 5 fully playable levels with increasing difficulty, featuring location-based narrative triggers (e.g., Easter eggs and warnings).
* **Menu System:** Main menu powered by a state machine (Menu, Level Select, Settings, Play, Pause, Win).
* **Physics and Movement:** Advanced character movement, gravity, multi-jump system, and complex collision detection that updates in real-time based on the active hero's traits.
* **Camera:** Dynamic camera following the player (Smooth Scrolling) with map boundary clamping.

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
3. Run the game:
   ```bash
   python src/main.py

## Controls
* A / D or Arrow Keys: Move left/right.

* W / Spacebar or Up Arrow: Jump.
  
* 1 / 2 / 3: Switch Hero (1: Knight, 2: Ninja, 3: Miner).

* ESC: Return to menu / Level selection.
