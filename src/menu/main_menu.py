import arcade
from src.menu.menu_state import MenuState, MenuItem
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.arcade_compat import safe_draw_text

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
        
        # Select first item by default
        if self.menu_items:
            self.menu_items[0].is_selected = True
            
    def create_game(self):
        """Navigate to create game menu"""
        self.director.push_scene("squad_select")
        
    def join_game(self):
        """Navigate to join game menu"""
        self.director.push_scene("lobby_browser")
        
    def show_leaderboard(self):
        """Show global leaderboard"""
        self.director.push_scene("leaderboard")
        
    def show_settings(self):
        """Show settings menu"""
        self.director.push_scene("settings")
        
    def exit_game(self):
        """Exit the game"""
        arcade.exit()
        
    def draw(self):
        """Draw the main menu"""
        super().draw()
        
        # Draw additional decorative elements
        safe_draw_text(
            "A Platform Adventure",
            SCREEN_WIDTH // 2,
            550,
            arcade.color.WHITE,
            18,
            anchor_x="center",
            font_name="Arial"
        )