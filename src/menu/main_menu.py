"""
Main menu for Heaven Burns Red
"""

import arcade
from src.menu.menu_state import MenuState, MenuItem
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class MainMenu(MenuState):
    """Main menu of the game"""
    
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
        
        # Select first item
        if self.menu_items:
            self.menu_items[0].is_selected = True
            
    def create_game(self):
        """Navigate to squad selection"""
        self.director.push_scene("squad_select")
        
    def join_game(self):
        """Navigate to multiplayer lobby"""
        self.director.push_scene("lobby_menu")
        
    def show_leaderboard(self):
        """Show global leaderboard"""
        self.director.push_scene("leaderboard")
        
    def show_settings(self):
        """Show settings menu"""
        self.director.push_scene("settings")
        
    def exit_game(self):
        """Exit the game"""
        # Save before exiting
        save_manager = self.director.get_system('save_manager')
        if save_manager and save_manager.current_save:
            save_manager.save_game(1)
            
        # Close the window
        arcade.close_window()
        
    def draw(self):
        """Draw the main menu"""
        # Draw base menu
        super().draw()
        
        # Draw subtitle
        arcade.draw_text(
            "A Platform Adventure Game",
            SCREEN_WIDTH // 2,
            550,
            arcade.color.WHITE,
            18,
            anchor_x="center"
        )
        
        # Draw controls hint
        arcade.draw_text(
            "Use Arrow Keys or WASD to navigate, Enter to select",
            SCREEN_WIDTH // 2,
            50,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center"
        )