#!/usr/bin/env python3
"""
Heaven Burns Red - Main Game Entry Point
Complete implementation with all imports and integrations
"""

import os
import sys
import arcade
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

# ============================================================================
# FILE: src/core/constants.py (Complete Version)
# ============================================================================
# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Heaven Burns Red"

# Game settings
FPS = 60
GRAVITY = 0.5
PLAYER_MOVEMENT_SPEED = 5
JUMP_SPEED = 15

# UI Colors
UI_PRIMARY = arcade.color.CRIMSON
UI_SECONDARY = arcade.color.WHITE
UI_BACKGROUND = (20, 20, 20)
UI_HOVER = arcade.color.LIGHT_CRIMSON

# Networking
DEFAULT_PORT = 8080
MAX_PLAYERS = 8

# Character stats
DEFAULT_HEALTH = 100
DEFAULT_SPEED = 5
DEFAULT_JUMP_POWER = 15

# ============================================================================
# Import all necessary components
# ============================================================================
# First, add the src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.director import Director, Scene
from src.core.asset_manager import AssetManager
from src.input.input_manager import InputManager, InputAction, InputType
from src.save.save_manager import SaveManager, SaveData
from src.systems.gravity import GravityManager, GravityMode
from src.systems.animation import AnimationController, AnimationState, Animation
from src.menu.menu_state import MenuState, MenuItem
from src.menu.main_menu import MainMenu
from src.menu.squad_select import SquadSelectMenu, CharacterInfo
from src.menu.character_select import CharacterSelectMenu, CharacterGrid
from src.menu.settings_menu import SettingsMenu
from src.menu.leaderboard import LeaderboardMenu
from src.menu.lobby_menu import LobbyMenu
from src.scenes.gameplay import GameplayScene
from src.scenes.pause import PauseMenu
from src.networking.server import GameServer
from src.networking.client import GameClient
from src.networking.protocol import NetworkProtocol, MessageType

# ============================================================================
# Create missing menu imports that need to be defined
# ============================================================================
# Import from character select needs the proper implementation
# Let's add it to the squad_select file since they're related

# ============================================================================
# FILE: main.py - Complete Implementation
# ============================================================================
class HeavenBurnsRed(arcade.Window):
    """Main game class with all systems integrated"""
    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)
        
        # Core systems
        self.director = Director()
        self.input_manager = InputManager()
        self.asset_manager = AssetManager()
        self.save_manager = SaveManager()
        self.gravity_manager = GravityManager()
        
        # Networking (optional)
        self.game_client = None
        self.is_multiplayer = False
        
        # Register systems with director
        self.director.systems = {
            'input_manager': self.input_manager,
            'asset_manager': self.asset_manager,
            'save_manager': self.save_manager,
            'gravity_manager': self.gravity_manager,
            'game_client': self.game_client,
            'is_multiplayer': self.is_multiplayer
        }
        
        # Frame rate
        self.set_update_rate(1/FPS)
        
        # Debug info
        self.show_fps = False
        
    def setup(self):
        """Set up the game with all scenes"""
        print("Setting up Heaven Burns Red...")
        
        # Create default config files if they don't exist
        self._create_default_configs()
        
        # Load save data if exists
        save_slots = self.save_manager.get_save_files()
        if any(slot['exists'] for slot in save_slots):
            # Load most recent save
            most_recent_slot = max(
                (s for s in save_slots if s['exists']),
                key=lambda s: s['timestamp']
            )
            self.save_manager.load_game(most_recent_slot['slot'])
            print(f"Loaded save from slot {most_recent_slot['slot']}")
        else:
            # Create new save
            self.save_manager.current_save = SaveData()
            print("Created new save data")
            
        # Register all scenes
        self._register_all_scenes()
        
        # Start with main menu
        self.director.push_scene("main_menu")
        print("Game setup complete!")
        
    def _create_default_configs(self):
        """Create default configuration files if they don't exist"""
        import src.utils.helpers as helpers
        
        # Create config directory
        os.makedirs('config', exist_ok=True)
        
        # Default configurations
        configs = {
            'characters.json': {
                "characters": {
                    "31A": {
                        "ruka": {
                            "id": "ruka",
                            "name": "Ruka Kayamori",
                            "health": 100,
                            "speed": 6,
                            "jump_power": 15,
                            "abilities": ["Double Jump", "Dash Attack", "Leadership Boost"]
                        }
                    }
                }
            },
            'squads.json': {
                "squads": [
                    {
                        "id": "31A",
                        "name": "31A Squad",
                        "members": [
                            {"id": "ruka", "name": "Ruka", "health": 100, "speed": 6, "jump_power": 15, "abilities": ["Double Jump", "Dash Attack"]},
                            {"id": "yuki", "name": "Yuki", "health": 80, "speed": 8, "jump_power": 18, "abilities": ["Air Dash", "Quick Strike"]},
                            {"id": "karen", "name": "Karen", "health": 120, "speed": 4, "jump_power": 12, "abilities": ["Shield Bash", "Ground Pound"]},
                            {"id": "tsukasa", "name": "Tsukasa", "health": 90, "speed": 7, "jump_power": 16, "abilities": ["Teleport", "Energy Blast"]},
                            {"id": "megumi", "name": "Megumi", "health": 85, "speed": 7, "jump_power": 17, "abilities": ["Healing Aura", "Light Beam"]},
                            {"id": "ichigo", "name": "Ichigo", "health": 95, "speed": 6, "jump_power": 15, "abilities": ["Fire Ball", "Flame Dash"]}
                        ]
                    }
                ]
            }
        }
        
        for filename, content in configs.items():
            filepath = os.path.join('config', filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    json.dump(content, f, indent=2)
                print(f"Created default config: {filename}")
                
    def _register_all_scenes(self):
        """Register all game scenes"""
        # Menu scenes
        self.director.register_scene(
            "main_menu",
            MainMenu(self.director, self.input_manager)
        )
        self.director.register_scene(
            "squad_select",
            SquadSelectMenu(self.director, self.input_manager)
        )
        self.director.register_scene(
            "settings",
            SettingsMenu(self.director, self.input_manager)
        )
        self.director.register_scene(
            "leaderboard", 
            LeaderboardMenu(self.director, self.input_manager)
        )
        self.director.register_scene(
            "lobby_menu",
            LobbyMenu(self.director, self.input_manager)
        )
        self.director.register_scene(
            "lobby_browser",
            LobbyMenu(self.director, self.input_manager)  # Reuse for now
        )
        
        # Gameplay scenes
        self.director.register_scene(
            "gameplay",
            GameplayScene(self.director, self.input_manager)
        )
        self.director.register_scene(
            "pause",
            PauseMenu(self.director, self.input_manager)
        )
        
        # Character select is created dynamically when squad is selected
        
    def on_draw(self):
        """Render the game"""
        self.director.draw()
        
        # Show FPS if enabled
        if self.show_fps:
            arcade.draw_text(
                f"FPS: {arcade.get_fps():.0f}",
                10, SCREEN_HEIGHT - 30,
                arcade.color.WHITE,
                14
            )
        
    def update(self, delta_time: float):
        """Update game logic"""
        self.director.update(delta_time)
        self.input_manager.update_controller()
        
        # Process network messages if multiplayer
        if self.is_multiplayer and self.game_client:
            # This would be async in real implementation
            pass
        
    def on_key_press(self, key, modifiers):
        """Handle key press"""
        # Toggle FPS display
        if key == arcade.key.F1:
            self.show_fps = not self.show_fps
            
        # Pass to input manager and current scene
        self.input_manager.on_key_press(key, modifiers)
        current_scene = self.director.get_current_scene()
        if current_scene:
            current_scene.on_key_press(key, modifiers)
            
    def on_key_release(self, key, modifiers):
        """Handle key release"""
        self.input_manager.on_key_release(key, modifiers)
        current_scene = self.director.get_current_scene()
        if current_scene:
            current_scene.on_key_release(key, modifiers)
            
    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse motion"""
        current_scene = self.director.get_current_scene()
        if current_scene:
            current_scene.on_mouse_motion(x, y, dx, dy)
            
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse press"""
        current_scene = self.director.get_current_scene()
        if current_scene:
            current_scene.on_mouse_press(x, y, button, modifiers)
            
    def on_close(self):
        """Handle window close"""
        print("Saving game before exit...")
        # Auto-save on exit
        if self.save_manager.current_save:
            self.save_manager.save_game(1)
            print("Game saved!")
        super().on_close()

# ============================================================================
# Update SquadSelectMenu to properly handle character selection
# ============================================================================
def update_squad_select_menu():
    """Patch to add character selection transition"""
    original_select = SquadSelectMenu.select_item
    
    def new_select_item(self):
        if not self.showing_character_select:
            # Enter character selection for this squad
            self.showing_character_select = True
            squad = self.squads[self.selected_squad_index]
            self.character_info.set_character(squad['members'][0])
        else:
            # Character selected, create character select menu
            squad = self.squads[self.selected_squad_index]
            char_select = CharacterSelectMenu(
                self.director, 
                self.input_manager,
                squad
            )
            self.director.register_scene("character_select", char_select)
            self.director.push_scene("character_select")
            
    SquadSelectMenu.select_item = new_select_item

# Apply the patch
update_squad_select_menu()

# ============================================================================
# Main entry point
# ============================================================================
def main():
    """Main function with server option"""
    print("=" * 60)
    print("HEAVEN BURNS RED - Platform Game")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--server':
            # Run as server
            print("Starting multiplayer server...")
            server = GameServer()
            try:
                asyncio.run(server.start_server())
            except KeyboardInterrupt:
                print("\nServer stopped.")
        elif sys.argv[1] == '--help':
            print("Usage:")
            print("  python main.py          - Run the game")
            print("  python main.py --server - Run multiplayer server")
            print("  python main.py --help   - Show this help")
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        # Run as client/game
        print("Starting game...")
        try:
            game = HeavenBurnsRed(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
            game.setup()
            arcade.run()
        except Exception as e:
            print(f"Error running game: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("Game closed.")

# ============================================================================
# Project setup helper
# ============================================================================
def setup_project():
    """Create all necessary directories and files"""
    print("Setting up project structure...")
    
    # Create directories
    directories = [
        'src', 'src/core', 'src/input', 'src/menu', 'src/entities',
        'src/entities/enemies', 'src/entities/items', 'src/systems',
        'src/scenes', 'src/networking', 'src/save', 'src/ui', 'src/utils',
        'assets', 'assets/sprites', 'assets/sprites/characters',
        'assets/sprites/enemies', 'assets/sprites/items', 'assets/sprites/ui',
        'assets/sounds', 'assets/sounds/sfx', 'assets/sounds/music',
        'assets/levels', 'assets/fonts',
        'config', 'saves', 'docker', 'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
    # Create empty __init__.py files
    init_dirs = [
        'src', 'src/core', 'src/input', 'src/menu', 'src/entities',
        'src/entities/enemies', 'src/entities/items', 'src/systems',
        'src/scenes', 'src/networking', 'src/save', 'src/ui', 'src/utils'
    ]
    
    for directory in init_dirs:
        init_file = os.path.join(directory, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# Package initialization\n')
                
    print("Project structure created!")
    
    # Create requirements.txt if it doesn't exist
    if not os.path.exists('requirements.txt'):
        with open('requirements.txt', 'w') as f:
            f.write("""arcade==2.6.17
Pillow==10.0.0
pymunk==6.5.1
websockets==11.0.3
jsonschema==4.17.3
numpy==1.24.3
""")
        print("Created requirements.txt")
        
    print("\nSetup complete! To run the game:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run the game: python main.py")

if __name__ == "__main__":
    # Check if this is first run (no src directory)
    if not os.path.exists('src'):
        print("First time setup detected...")
        setup_project()
        print("\nPlease run 'python main.py' again to start the game.")
    else:
        main()

# ============================================================================
# END OF MAIN.PY
# ============================================================================