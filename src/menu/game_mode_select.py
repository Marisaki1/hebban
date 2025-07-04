# src/menu/game_mode_select.py - Fixed to handle previous scene properly
"""
Fixed game mode selection menu with proper back navigation
"""

import arcade
from src.menu.menu_state import MenuState, MenuItem
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class GameModeSelectMenu(MenuState):
    """Choose between Single Player and Multiplayer - FIXED"""
    
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Choose Game Mode"
        self.scene_name = "game_mode_select"
        
        # Create menu items
        menu_y_start = 350
        menu_spacing = 80
        
        self.menu_items = [
            MenuItem(
                "Single Player",
                self.single_player,
                SCREEN_WIDTH // 2,
                menu_y_start
            ),
            MenuItem(
                "Multiplayer Lobby",
                self.multiplayer_lobby,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing
            ),
            MenuItem(
                "Back to Stage Select",
                self.go_back_to_stage,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing * 2
            )
        ]
        
        if self.menu_items:
            self.menu_items[0].is_selected = True
            
    def single_player(self):
        """Start single player game"""
        # Set single player mode
        self.director.systems['is_multiplayer'] = False
        self.director.change_scene('gameplay')
        
    def multiplayer_lobby(self):
        """Go to multiplayer lobby"""
        # Set multiplayer mode and go to lobby
        self.director.systems['is_multiplayer'] = True
        self.director.change_scene('lobby_menu')
        
    def go_back_to_stage(self):
        """FIXED: Go back to day select instead of character select"""
        # Pop this scene to go back to day select
        self.director.pop_scene()
        
    def draw(self):
        """Draw game mode selection"""
        # Draw base menu
        super().draw()
        
        # Draw description
        arcade.draw_text(
            "Select how you want to play:",
            SCREEN_WIDTH // 2,
            450,
            arcade.color.WHITE,
            18,
            anchor_x="center"
        )
        
        # Draw mode descriptions
        arcade.draw_text(
            "Single Player: Play alone against AI enemies",
            SCREEN_WIDTH // 2,
            280,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "Multiplayer: Create or join a lobby with friends",
            SCREEN_WIDTH // 2,
            200,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center"
        )
        
        # Show selected stage info
        save_manager = self.director.get_system('save_manager')
        if save_manager and save_manager.current_save:
            stage_info = save_manager.current_save.game_data.get('selected_stage', {})
            if stage_info:
                chapter_id = stage_info.get('chapter_id', '')
                day_id = stage_info.get('day_id', '')
                
                arcade.draw_text(
                    f"Selected: {chapter_id.title()} - {day_id.title()}",
                    SCREEN_WIDTH // 2,
                    100,
                    arcade.color.YELLOW,
                    14,
                    anchor_x="center"
                )