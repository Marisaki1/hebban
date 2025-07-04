"""
Main game class - Fixed startup and save handling for Arcade 3.0.0
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
from src.menu.continue_menu import ContinueMenu
from src.menu.save_select_menu import SaveSelectMenu
from src.scenes.gameplay import GameplayScene
from src.scenes.pause import PauseMenu

class HeavenBurnsRed(arcade.Window):
    """Main game class for Arcade 3.0.0 - Fixed startup flow"""
    
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
        
        # Game state flags
        self.is_new_game = True
        self.multiplayer_session_data = None
        self.pending_lobby_join = None  # For Join Game flow
        
        # Register systems with director
        self.director.systems = {
            'input_manager': self.input_manager,
            'asset_manager': self.asset_manager,
            'save_manager': self.save_manager,
            'gravity_manager': self.gravity_manager,
            'sound_manager': self.sound_manager,
            'particle_manager': self.particle_manager,
            'is_multiplayer': False,
            'game_client': None,
            'game_instance': self  # Reference to main game
        }
        
        # Set update rate
        self.set_update_rate(1/FPS)
        
    def setup(self):
        """Set up the game - NO auto-loading saves"""
        # Load game assets
        self.asset_manager.load_default_assets()
        
        # Initialize save manager but DON'T auto-load any saves
        # Player must explicitly choose New Game or Continue
        
        # Register all scenes
        self._register_scenes()
        
        # Start with main menu (completely fresh start)
        self.director.push_scene("main_menu")
        print("✓ Game started - Choose New Game or Continue")
        
    def start_new_game(self):
        """Start a completely fresh new game"""
        # Create completely fresh save data
        self.save_manager.current_save = SaveData()
        self.is_new_game = True
        self.multiplayer_session_data = None
        
        # Reset multiplayer flags
        self.director.systems['is_multiplayer'] = False
        self.director.systems['game_client'] = None
        
        print("✓ Starting completely new game")
        # Go to squad selection for character choice
        self.director.change_scene('squad_select')
        
    def show_continue_menu(self):
        """Show continue menu with save slot selection"""
        save_slots = self.save_manager.get_save_files()
        available_saves = [slot for slot in save_slots if slot['exists']]
        
        if not available_saves:
            print("No save files found - redirecting to New Game")
            self.start_new_game()
            return False
            
        # Go to save selection menu
        self.director.change_scene('save_select')
        return True
        
    def continue_from_save(self, slot_number: int):
        """Continue from specific save slot"""
        if self.save_manager.load_game(slot_number):
            self.is_new_game = False
            print(f"✓ Loaded save from slot {slot_number}")
            
            # Check if this was a multiplayer session
            game_data = self.save_manager.current_save.game_data
            if game_data.get('was_multiplayer', False):
                # Restore multiplayer session data and go to rejoin menu
                self.multiplayer_session_data = game_data.get('multiplayer_data', {})
                self.director.systems['is_multiplayer'] = True
                self.director.change_scene('continue_menu')
            else:
                # Single player continue - go directly to gameplay with saved character
                self.director.change_scene('gameplay')
            return True
        else:
            print(f"Failed to load save slot {slot_number}")
            return False
            
    def start_join_game_flow(self):
        """Start the Join Game flow - character select first, then lobby join"""
        # Create temporary save data for multiplayer session
        self.save_manager.current_save = SaveData()
        self.is_new_game = True
        
        # Set multiplayer mode
        self.director.systems['is_multiplayer'] = True
        self.pending_lobby_join = True
        
        print("✓ Starting Join Game flow - select character first")
        # Go to squad selection to choose character for multiplayer
        self.director.change_scene('squad_select')
        
    def complete_join_game_flow(self):
        """Complete join game flow after character selection"""
        if self.pending_lobby_join:
            self.pending_lobby_join = False
            # Go to lobby in join mode
            lobby_scene = self.director.scenes.get('lobby_menu')
            if lobby_scene:
                lobby_scene.set_join_mode()
            self.director.change_scene('lobby_menu')
            
    def save_multiplayer_session(self, lobby_data: dict):
        """Save multiplayer session data for continue"""
        if self.save_manager.current_save:
            game_data = self.save_manager.current_save.game_data
            game_data['was_multiplayer'] = True
            game_data['multiplayer_data'] = {
                'lobby_code': lobby_data.get('lobby_code'),
                'player_list': lobby_data.get('players', []),
                'host_id': lobby_data.get('host_id'),
                'selected_squad': game_data.get('selected_squad'),
                'selected_character': game_data.get('selected_character')
            }
            # Auto-save multiplayer session
            self.save_manager.save_game(1)
        
    def _register_scenes(self):
        """Register all game scenes"""
        scenes = {
            "main_menu": MainMenu(self.director, self.input_manager),
            "squad_select": SquadSelectMenu(self.director, self.input_manager),
            "character_select": CharacterSelectMenu,  # Created dynamically
            "settings": SettingsMenu(self.director, self.input_manager),
            "leaderboard": LeaderboardMenu(self.director, self.input_manager),
            "lobby_menu": LobbyMenu(self.director, self.input_manager),
            "continue_menu": ContinueMenu(self.director, self.input_manager),
            "save_select": SaveSelectMenu(self.director, self.input_manager),
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
        # Auto-save on exit if there's a current save
        if self.save_manager.current_save:
            self.save_manager.save_game(1)
        
        # Cleanup systems
        self.sound_manager.cleanup()
        self.particle_manager.clear()
        
        super().on_close()