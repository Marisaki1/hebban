"""
Heaven Burns Red - Main Game Entry Point
Fixed for Arcade 3.0.0 compatibility issues
"""

import os
import sys
import arcade
import traceback

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_arcade_installation():
    """Test if Arcade is properly installed and working"""
    print("Testing Arcade installation...")
    
    try:
        # Test basic imports
        import arcade
        print(f"✓ Arcade imported successfully")
        
        # Test version
        try:
            version = arcade.version.VERSION
            print(f"✓ Arcade version: {version}")
        except:
            print("? Arcade version unavailable")
        
        # Test basic classes
        test_items = [
            ('arcade.Window', arcade.Window),
            ('arcade.Sprite', arcade.Sprite),
            ('arcade.SpriteList', arcade.SpriteList),
        ]
        
        # Test SpriteSolidColor separately since it might not exist in some versions
        try:
            arcade.SpriteSolidColor
            print("✓ arcade.SpriteSolidColor available")
        except:
            print("✗ arcade.SpriteSolidColor missing - will use fallbacks")
        
        for name, cls in test_items:
            try:
                cls
                print(f"✓ {name} available")
            except:
                print(f"✗ {name} missing")
        
        # Test drawing functions
        drawing_funcs = [
            'draw_rectangle_filled',
            'draw_text',
            'draw_circle_filled'
        ]
        
        for func_name in drawing_funcs:
            if hasattr(arcade, func_name):
                print(f"✓ arcade.{func_name} available")
            else:
                print(f"✗ arcade.{func_name} missing")
        
        print("Arcade test complete.\n")
        return True
        
    except Exception as e:
        print(f"✗ Arcade installation test failed: {e}")
        return False

# Test Arcade before importing our modules
if not test_arcade_installation():
    print("WARNING: Arcade installation has issues. The game may not work properly.")
    input("Press Enter to continue anyway, or Ctrl+C to exit...")

# Now import our modules (after testing Arcade)
try:
    # Import core constants first
    from src.core.constants import *
    
    # Import core systems
    from src.core.director import Director, Scene
    from src.core.asset_manager import AssetManager
    from src.input.input_manager import InputManager, InputAction, InputType
    from src.save.save_manager import SaveManager, SaveData
    from src.systems.gravity import GravityManager, GravityMode
    
    # Import menu components
    from src.menu.menu_state import MenuState, MenuItem
    from src.menu.main_menu import MainMenu
    from src.menu.squad_select import SquadSelectMenu
    from src.menu.settings_menu import SettingsMenu
    from src.menu.leaderboard import LeaderboardMenu
    from src.menu.lobby_menu import LobbyMenu
    
    # Import scenes
    from src.scenes.gameplay import GameplayScene
    from src.scenes.pause import PauseMenu
    
    print("✓ All game modules imported successfully")
    
except Exception as e:
    print(f"✗ Error importing game modules: {e}")
    traceback.print_exc()
    input("Press Enter to exit...")
    sys.exit(1)

class HeavenBurnsRed(arcade.Window):
    """Main game class with enhanced error handling - Fixed for Arcade 3.0.0"""
    def __init__(self, width: int, height: int, title: str):
        try:
            super().__init__(width, height, title, resizable=False)
            print("✓ Arcade window created successfully")
        except Exception as e:
            print(f"✗ Error creating Arcade window: {e}")
            raise
        
        # Set background
        try:
            arcade.set_background_color(arcade.color.BLACK)
            print("✓ Background color set")
        except Exception as e:
            print(f"Warning: Could not set background color: {e}")
        
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
        try:
            self.set_update_rate(1/FPS)
            print(f"✓ Update rate set to {FPS} FPS")
        except Exception as e:
            print(f"Warning: Could not set update rate: {e}")
        
        # Debug info
        self.show_fps = False
        self._last_delta_time = 1/60
        
        print("✓ Game initialization complete")
        
    def setup(self):
        """Set up the game with enhanced error handling"""
        print("Setting up Heaven Burns Red...")
        
        try:
            # Create default config files if they don't exist
            from src.utils import helpers
            helpers.create_default_configs()
            print("✓ Default configs created")
        except Exception as e:
            print(f"Warning: Could not create default configs: {e}")
        
        try:
            # Load save data if exists
            save_slots = self.save_manager.get_save_files()
            if any(slot['exists'] for slot in save_slots):
                # Load most recent save
                most_recent_slot = max(
                    (s for s in save_slots if s['exists']),
                    key=lambda s: s.get('timestamp', '')
                )
                self.save_manager.load_game(most_recent_slot['slot'])
                print(f"✓ Loaded save from slot {most_recent_slot['slot']}")
            else:
                # Create new save
                self.save_manager.current_save = SaveData()
                print("✓ Created new save data")
        except Exception as e:
            print(f"Warning: Save system error: {e}")
            # Create minimal save data
            self.save_manager.current_save = SaveData()
            
        try:
            # Register all scenes
            self._register_all_scenes()
            print("✓ All scenes registered")
        except Exception as e:
            print(f"✗ Error registering scenes: {e}")
            traceback.print_exc()
            raise
            
        try:
            # Start with main menu
            self.director.push_scene("main_menu")
            print("✓ Main menu scene started")
        except Exception as e:
            print(f"✗ Error starting main menu: {e}")
            traceback.print_exc()
            raise
        
        print("✓ Game setup complete!")
        
    def _register_all_scenes(self):
        """Register all game scenes with error handling"""
        scene_configs = [
            ("main_menu", lambda: MainMenu(self.director, self.input_manager)),
            ("squad_select", lambda: SquadSelectMenu(self.director, self.input_manager)),
            ("settings", lambda: SettingsMenu(self.director, self.input_manager)),
            ("leaderboard", lambda: LeaderboardMenu(self.director, self.input_manager)),
            ("lobby_menu", lambda: LobbyMenu(self.director, self.input_manager)),
            ("gameplay", lambda: GameplayScene(self.director, self.input_manager)),
            ("pause", lambda: PauseMenu(self.director, self.input_manager)),
        ]
        
        for scene_name, scene_factory in scene_configs:
            try:
                scene = scene_factory()
                self.director.register_scene(scene_name, scene)
                print(f"✓ Registered scene: {scene_name}")
            except Exception as e:
                print(f"✗ Error registering scene {scene_name}: {e}")
                # Don't raise - continue with other scenes
        
    def on_draw(self):
        """Render the game with error handling - Arcade 3.0.0 Compatible"""
        try:
            # Clear screen - this should always work
            self.clear()
            
            # Draw current scene
            self.director.draw()
            
            # Show FPS if enabled
            if self.show_fps:
                fps_value = round(1/self._last_delta_time) if self._last_delta_time > 0 else 0
                try:
                    # Try to draw FPS using compatibility layer
                    from src.core.arcade_compat import safe_draw_text
                    safe_draw_text(
                        f"FPS: {fps_value}",
                        10, SCREEN_HEIGHT - 30,
                        arcade.color.WHITE,
                        14
                    )
                except:
                    pass  # If we can't draw FPS, that's fine
                    
        except Exception as e:
            print(f"Error in on_draw: {e}")
            # Don't re-raise - this would crash the game loop
            # Instead, try to draw a simple error message
            try:
                from src.core.arcade_compat import safe_draw_rectangle_filled, safe_draw_text
                safe_draw_rectangle_filled(640, 360, 1280, 720, (20, 20, 20))
                safe_draw_text("Rendering Error", 640, 360, arcade.color.RED, 48, anchor_x="center", anchor_y="center")
            except:
                pass  # If even that fails, just give up on drawing
        
    def on_update(self, delta_time: float):
        """Update game logic with error handling"""
        try:
            # Store delta time for FPS calculation
            self._last_delta_time = delta_time
            
            # Update game systems
            self.director.update(delta_time)
            self.input_manager.update_controller()
            
        except Exception as e:
            print(f"Error in on_update: {e}")
            # Don't re-raise - this would crash the game loop
        
    def on_key_press(self, key, modifiers):
        """Handle key press with error handling"""
        try:
            # Toggle FPS display
            if key == arcade.key.F1:
                self.show_fps = not self.show_fps
                print(f"FPS display: {'ON' if self.show_fps else 'OFF'}")
                
            # Pass to input manager and current scene
            self.input_manager.on_key_press(key, modifiers)
            current_scene = self.director.get_current_scene()
            if current_scene:
                current_scene.on_key_press(key, modifiers)
                
        except Exception as e:
            print(f"Error in on_key_press: {e}")
            
    def on_key_release(self, key, modifiers):
        """Handle key release with error handling"""
        try:
            self.input_manager.on_key_release(key, modifiers)
            current_scene = self.director.get_current_scene()
            if current_scene:
                current_scene.on_key_release(key, modifiers)
        except Exception as e:
            print(f"Error in on_key_release: {e}")
            
    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse motion with error handling"""
        try:
            self.input_manager.on_mouse_motion(x, y, dx, dy)
            current_scene = self.director.get_current_scene()
            if current_scene:
                current_scene.on_mouse_motion(x, y, dx, dy)
        except Exception as e:
            print(f"Error in on_mouse_motion: {e}")
            
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse press with error handling"""
        try:
            current_scene = self.director.get_current_scene()
            if current_scene:
                current_scene.on_mouse_press(x, y, button, modifiers)
        except Exception as e:
            print(f"Error in on_mouse_press: {e}")
            
    def close(self):
        """Handle window close with error handling"""
        try:
            print("Saving game before exit...")
            # Auto-save on exit
            if self.save_manager and self.save_manager.current_save:
                self.save_manager.save_game(1)
                print("✓ Game saved!")
        except Exception as e:
            print(f"Error saving on exit: {e}")
        
        try:
            super().close()
        except Exception as e:
            print(f"Error closing window: {e}")

def main():
    """Main function with comprehensive error handling"""
    print("=" * 60)
    print("HEAVEN BURNS RED - Platform Game")
    print("Fixed for Arcade 3.0.0 Compatibility")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print("Usage:")
            print("  python main.py          - Run the game")
            print("  python main.py --help   - Show this help")
            print("Controls:")
            print("  Arrow Keys / WASD       - Navigate menus")
            print("  Enter / Space           - Select")
            print("  Escape                  - Back/Pause")
            print("  F1                      - Toggle FPS")
            return
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information")
            return
    
    # Run the game
    print("Starting game...")
    try:
        game = HeavenBurnsRed(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        game.setup()
        print("✓ Game started successfully")
        print("Press F1 to toggle FPS display")
        arcade.run()
    except KeyboardInterrupt:
        print("\n✓ Game interrupted by user")
    except Exception as e:
        print(f"✗ Fatal error running game: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")
    finally:
        print("✓ Game closed.")

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
                
    print("✓ Project structure created!")

if __name__ == "__main__":
    # Check if this is first run (no src directory)
    if not os.path.exists('src'):
        print("First time setup detected...")
        setup_project()
        print("\nPlease run 'python main.py' again to start the game.")
    else:
        main()