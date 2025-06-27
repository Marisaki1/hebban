"""
Heaven Burns Red - Main Game Entry Point
Updated for Arcade 3.0 compatibility - FIXED VERSION
"""

import os
import sys
import arcade
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import core constants first
from src.core.constants import *

# Import core systems
from src.core.director import Director, Scene
from src.core.asset_manager import AssetManager
from src.input.input_manager import InputManager, InputAction, InputType
from src.save.save_manager import SaveManager, SaveData
from src.systems.gravity import GravityManager, GravityMode
from src.systems.animation import AnimationController, AnimationState, Animation

# Import menu components
from src.menu.menu_state import MenuState, MenuItem
from src.menu.main_menu import MainMenu
from src.menu.squad_select import SquadSelectMenu, CharacterInfo
from src.menu.character_select import CharacterSelectMenu, CharacterGrid
from src.menu.settings_menu import SettingsMenu
from src.menu.leaderboard import LeaderboardMenu
from src.menu.lobby_menu import LobbyMenu

# Import scenes
from src.scenes.gameplay import GameplayScene
from src.scenes.pause import PauseMenu

# Import networking
from src.networking.server import GameServer
from src.networking.client import GameClient
from src.networking.protocol import NetworkProtocol, MessageType

# Import utilities
import src.utils.helpers as helpers

class HeavenBurnsRed(arcade.Window):
    """Main game class with Arcade 3.0 compatibility - FIXED"""
    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title, resizable=False)
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
        
        # Frame rate - Arcade 3.0 compatible
        self.set_update_rate(1/FPS)
        
        # Debug info
        self.show_fps = False
        
        # Store delta time for FPS calculation (renamed to avoid conflict)
        self._last_delta_time = 1/60
        
    def setup(self):
        """Set up the game with all scenes"""
        print("Setting up Heaven Burns Red...")
        
        # Create default config files if they don't exist
        helpers.create_default_configs()
        
        # Load save data if exists
        save_slots = self.save_manager.get_save_files()
        if any(slot['exists'] for slot in save_slots):
            # Load most recent save
            most_recent_slot = max(
                (s for s in save_slots if s['exists']),
                key=lambda s: s.get('timestamp', '')
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
        
    def on_draw(self):
        """Render the game - Arcade 3.0 Style"""
        # Clear screen - Arcade 3.0 automatically handles this
        self.clear()
        
        # Draw current scene
        self.director.draw()
        
        # Show FPS if enabled
        if self.show_fps:
            fps_value = round(1/self._last_delta_time) if self._last_delta_time > 0 else 0
            arcade.draw_text(
                f"FPS: {fps_value}",
                10, SCREEN_HEIGHT - 30,
                arcade.color.WHITE,
                14
            )
        
    def on_update(self, delta_time: float):
        """Update game logic"""
        # Store delta time for FPS calculation (using our own variable)
        self._last_delta_time = delta_time
        
        # Update game systems
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
        self.input_manager.on_mouse_motion(x, y, dx, dy)
        current_scene = self.director.get_current_scene()
        if current_scene:
            current_scene.on_mouse_motion(x, y, dx, dy)
            
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse press"""
        current_scene = self.director.get_current_scene()
        if current_scene:
            current_scene.on_mouse_press(x, y, button, modifiers)
            
    def close(self):
        """Handle window close"""
        print("Saving game before exit...")
        # Auto-save on exit
        if self.save_manager.current_save:
            self.save_manager.save_game(1)
            print("Game saved!")
        super().close()

def main():
    """Main function with server option"""
    print("=" * 60)
    print("HEAVEN BURNS RED - Platform Game")
    try:
        print(f"Running on Arcade {arcade.version.VERSION}")
    except:
        print(f"Running on Arcade (version info unavailable)")
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
            f.write("""arcade==3.0.0
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