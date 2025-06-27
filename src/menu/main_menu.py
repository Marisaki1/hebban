# src/menu/main_menu.py
"""
Fixed main menu that works with Arcade 3.0.0
"""
import arcade
from src.menu.menu_state import MenuState, MenuItem
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

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
        
    def join_game(self):
        """Navigate to join game menu"""
        try:
            self.director.push_scene("lobby_browser")
        except Exception as e:
            print(f"Error navigating to lobby_browser: {e}")
            # Fallback to existing scene
            self.director.push_scene("lobby_menu")
        
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
            arcade.exit()
        except Exception as e:
            print(f"Error exiting game: {e}")
            # Fallback exit methods
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
        
    def _draw_subtitle(self):
        """Draw subtitle with fallback methods"""
        subtitle = "A Platform Adventure"
        try:
            # Method 1: Try full parameters
            arcade.draw_text(
                subtitle,
                SCREEN_WIDTH // 2,
                550,
                arcade.color.WHITE,
                18,
                anchor_x="center",
                font_name="Arial"
            )
            return
        except:
            pass
        
        try:
            # Method 2: Try minimal parameters
            arcade.draw_text(subtitle, SCREEN_WIDTH // 2, 550, arcade.color.WHITE, 18)
            return
        except:
            pass
        
        try:
            # Method 3: Try Text class
            if hasattr(arcade, 'Text'):
                text_obj = arcade.Text(
                    subtitle, SCREEN_WIDTH // 2, 550, arcade.color.WHITE, 18,
                    anchor_x="center"
                )
                text_obj.draw()
                return
        except:
            pass
        
        # Fallback
        print(f"Subtitle: '{subtitle}'")