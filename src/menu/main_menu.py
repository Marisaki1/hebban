# src/menu/main_menu.py
"""
Fixed main menu that works with Arcade 3.0.0
"""
import arcade
from src.menu.menu_state import MenuState, MenuItem
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.arcade_compat import safe_draw_text

class MainMenu(MenuState):
    """Main menu of the game - Fixed for Arcade 3.0.0"""
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Heaven Burns Red"
        
        # Create menu items
        menu_y_start = 400
        menu_spacing = 70
        
        self.menu_items = [
            MenuItem(
                "Create Game",
                self.create_game,
                SCREEN_WIDTH // 2,
                menu_y_start
            ),
            MenuItem(
                "Join Game",
                self.join_game,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing
            ),
            MenuItem(
                "Leaderboard",
                self.show_leaderboard,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing * 2
            ),
            MenuItem(
                "Settings",
                self.show_settings,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing * 3
            ),
            MenuItem(
                "Exit",
                self.exit_game,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing * 4
            ),
        ]
        
        # Select first item by default
        if self.menu_items:
            self.menu_items[0].is_selected = True
            
    def create_game(self):
        """Navigate to create game menu"""
        try:
            self.director.push_scene("squad_select")
        except Exception as e:
            print(f"Error navigating to squad_select: {e}")
            # Try fallback navigation
            try:
                self.director.change_scene("squad_select")
            except Exception as e2:
                print(f"Fallback navigation failed: {e2}")
        
    def join_game(self):
        """Navigate to join game menu"""
        try:
            # Try lobby_browser first, fallback to lobby_menu
            if "lobby_browser" in self.director.scenes:
                self.director.push_scene("lobby_browser")
            else:
                self.director.push_scene("lobby_menu")
        except Exception as e:
            print(f"Error navigating to multiplayer: {e}")
            # Create a simple fallback
            try:
                self.director.push_scene("lobby_menu")
            except Exception as e2:
                print(f"Fallback multiplayer navigation failed: {e2}")
        
    def show_leaderboard(self):
        """Show global leaderboard"""
        try:
            self.director.push_scene("leaderboard")
        except Exception as e:
            print(f"Error navigating to leaderboard: {e}")
        
    def show_settings(self):
        """Show settings menu"""
        try:
            self.director.push_scene("settings")
        except Exception as e:
            print(f"Error navigating to settings: {e}")
        
    def exit_game(self):
        """Exit the game"""
        try:
            # Save before exiting
            if hasattr(self.director, 'systems') and 'save_manager' in self.director.systems:
                save_manager = self.director.systems['save_manager']
                if save_manager and save_manager.current_save:
                    save_manager.save_game(1)
                    print("Game saved before exit")
            
            # Try different exit methods
            if hasattr(arcade, 'exit'):
                arcade.exit()
            elif hasattr(arcade, 'close_window'):
                arcade.close_window()
            else:
                # Fallback to system exit
                import sys
                sys.exit()
        except Exception as e:
            print(f"Error exiting game: {e}")
            # Ultimate fallback
            try:
                import sys
                sys.exit()
            except:
                pass
        
    def draw(self):
        """Draw the main menu"""
        # Draw base menu (background, title, menu items)
        super().draw()
        
        # Draw additional subtitle
        self._draw_subtitle()
        
        # Draw version info
        self._draw_version_info()
        
    def _draw_subtitle(self):
        """Draw subtitle with fallback methods"""
        subtitle = "A Platform Adventure Game"
        try:
            safe_draw_text(
                subtitle,
                SCREEN_WIDTH // 2,
                550,
                arcade.color.WHITE,
                18,
                anchor_x="center"
            )
        except Exception as e:
            print(f"Error drawing subtitle: {e}")
        
    def _draw_version_info(self):
        """Draw version information"""
        try:
            # Get version info
            version_text = "Arcade 3.0.0 | Pillow 11.0.0"
            
            # Try to get actual versions
            try:
                from src.core.asset_manager import asset_manager
                version_info = asset_manager.get_version_info()
                version_text = f"Arcade {version_info.get('arcade', '3.0.0')} | Pillow {version_info.get('pillow', '11.0.0')}"
            except:
                pass
            
            safe_draw_text(
                version_text,
                SCREEN_WIDTH - 10,
                10,
                arcade.color.GRAY,
                12,
                anchor_x="right"
            )
        except Exception as e:
            print(f"Error drawing version info: {e}")
            
    def _draw_controls_hint(self):
        """Draw controls hint"""
        try:
            controls_text = "Use Arrow Keys or WASD to navigate, Enter to select"
            safe_draw_text(
                controls_text,
                SCREEN_WIDTH // 2,
                50,
                arcade.color.LIGHT_GRAY,
                14,
                anchor_x="center"
            )
        except Exception as e:
            print(f"Error drawing controls hint: {e}")
            
    def on_key_press(self, key, modifiers):
        """Handle additional key presses"""
        # Call parent implementation first
        super().on_key_press(key, modifiers)
        
        # Handle additional keys
        if key == arcade.key.F1:
            # Toggle debug info or help
            print("F1 pressed - Debug info")
            try:
                from src.core.asset_manager import asset_manager
                asset_manager.debug_info()
            except Exception as e:
                print(f"Debug info error: {e}")
                
        elif key == arcade.key.F11:
            # Toggle fullscreen (if supported)
            try:
                window = arcade.get_window()
                if hasattr(window, 'set_fullscreen'):
                    window.set_fullscreen(not window.fullscreen)
            except Exception as e:
                print(f"Fullscreen toggle error: {e}")
    
    def update(self, delta_time: float):
        """Update main menu"""
        super().update(delta_time)
        
        # Add any main menu specific updates here
        # For example, background animations, etc.