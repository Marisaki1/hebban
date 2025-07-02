"""
Main game class - Clean Arcade 3.0.0 implementation
"""

import arcade
from src.core.constants import FPS
from src.core.director import Director
from src.core.asset_manager import AssetManager
from src.input.input_manager import InputManager
from src.save.save_manager import SaveManager, SaveData
from src.systems.gravity import GravityManager
from src.systems.sound_manager import SoundManager
from src.systems.particle_manager import ParticleManager

# Import all scenes
from src.menu.main_menu import MainMenu
from src.menu.squad_select import SquadSelectMenu
from src.menu.character_select import CharacterSelectMenu
from src.menu.settings_menu import SettingsMenu
from src.menu.leaderboard import LeaderboardMenu
from src.menu.lobby_menu import LobbyMenu
from src.scenes.gameplay import GameplayScene
from src.scenes.pause import PauseMenu

class HeavenBurnsRed(arcade.Window):
    """Main game class for Arcade 3.0.0"""
    
    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title, resizable=False)
        arcade.set_background_color(arcade.color.BLACK)
        
        # Core systems
        self.director = Director()
        self.input_manager = InputManager()
        self.asset_manager = AssetManager()
        self.save_manager = SaveManager()
        self.gravity_manager = GravityManager()
        self.sound_manager = SoundManager()
        self.particle_manager = ParticleManager()
        
        # Register systems with director
        self.director.systems = {
            'input_manager': self.input_manager,
            'asset_manager': self.asset_manager,
            'save_manager': self.save_manager,
            'gravity_manager': self.gravity_manager,
            'sound_manager': self.sound_manager,
            'particle_manager': self.particle_manager,
            'is_multiplayer': False,
            'game_client': None
        }
        
        # Set update rate
        self.set_update_rate(1/FPS)
        
    def setup(self):
        """Set up the game"""
        # Load/create save data
        save_slots = self.save_manager.get_save_files()
        if any(slot['exists'] for slot in save_slots):
            # Load most recent save
            most_recent = max(
                (s for s in save_slots if s['exists']),
                key=lambda s: s.get('timestamp', ''),
                default=None
            )
            if most_recent:
                self.save_manager.load_game(most_recent['slot'])
        else:
            # Create new save
            self.save_manager.current_save = SaveData()
            
        # Load game assets
        self.asset_manager.load_default_assets()
        
        # Register all scenes
        self._register_scenes()
        
        # Start with main menu
        self.director.push_scene("main_menu")
        
    def _register_scenes(self):
        """Register all game scenes"""
        scenes = {
            "main_menu": MainMenu(self.director, self.input_manager),
            "squad_select": SquadSelectMenu(self.director, self.input_manager),
            "character_select": CharacterSelectMenu,  # Created dynamically
            "settings": SettingsMenu(self.director, self.input_manager),
            "leaderboard": LeaderboardMenu(self.director, self.input_manager),
            "lobby_menu": LobbyMenu(self.director, self.input_manager),
            "gameplay": GameplayScene(self.director, self.input_manager),
            "pause": PauseMenu(self.director, self.input_manager),
        }
        
        for name, scene in scenes.items():
            if scene is not CharacterSelectMenu:  # Skip the class reference
                self.director.register_scene(name, scene)
                
    def on_draw(self):
        """Render the game"""
        self.clear()
        self.director.draw()
        
    def on_update(self, delta_time: float):
        """Update game logic"""
        self.director.update(delta_time)
        self.input_manager.update_controller()
        self.particle_manager.update(delta_time)
        
    def on_key_press(self, key, modifiers):
        """Handle key press"""
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
            
    def on_close(self):
        """Handle window close"""
        # Auto-save on exit
        if self.save_manager.current_save:
            self.save_manager.save_game(1)
        
        # Cleanup systems
        self.sound_manager.cleanup()
        self.particle_manager.clear()
        
        super().on_close()