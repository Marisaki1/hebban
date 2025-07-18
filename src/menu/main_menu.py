"""
Main menu with proper New Game/Continue distinction
"""

import arcade
from src.menu.menu_state import MenuState, MenuItem
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class MainMenu(MenuState):
    """Main menu with proper New Game/Continue options"""

    
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Heaven Burns Red"
        
        # Check for existing saves to show/hide Continue
        save_manager = self.director.get_system('save_manager')
        has_saves = False
        if save_manager:
            save_slots = save_manager.get_save_files()
            has_saves = any(slot['exists'] for slot in save_slots)
        
        # Create menu items based on save availability
        menu_y_start = 400
        menu_spacing = 70
        
        menu_items = [
            MenuItem(
                "New Game",
                self.new_game,
                SCREEN_WIDTH // 2,
                menu_y_start
            )
        ]
        
        # Only show Continue if saves exist
        if has_saves:
            menu_items.append(MenuItem(
                "Continue",
                self.continue_game,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing
            ))
            
        # Add other menu items
        other_items = [
            MenuItem(
                "Join Game", 
                self.join_game,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing * (2 if has_saves else 1)
            ),
            MenuItem(
                "Leaderboard",
                self.show_leaderboard,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing * (3 if has_saves else 2)
            ),
            MenuItem(
                "Settings",
                self.show_settings,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing * (4 if has_saves else 3)
            ),
            MenuItem(
                "Exit",
                self.exit_game,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing * (5 if has_saves else 4)
            ),
        ]
        
        menu_items.extend(other_items)
        self.menu_items = menu_items
        
        # Select first item
        if self.menu_items:
            self.menu_items[0].is_selected = True
            
    def new_game(self):
        """Start a completely new game"""
        print("NEW GAME button pressed")
        game_instance = self.director.get_system('game_instance')
        if game_instance:
            game_instance.start_new_game()
        else:
            print("Error: game_instance not found")
            
    def continue_game(self):
        """Show save selection menu for continuing"""
        game_instance = self.director.get_system('game_instance')
        if game_instance:
            success = game_instance.show_continue_menu()
            if not success:
                # No saves found, redirect to new game
                self.new_game()
        else:
            # Fallback - should not happen
            print("Error: game_instance not found")
        
    def join_game(self):
        """Start Join Game flow - character select first, then lobby join"""
        game_instance = self.director.get_system('game_instance')
        if game_instance:
            game_instance.start_join_game_flow()
        else:
            # Fallback - should not happen
            print("Error: game_instance not found")
        
    def show_leaderboard(self):
        """Show global leaderboard"""
        self.director.push_scene("leaderboard")
        
    def show_settings(self):
        """Show settings menu"""
        self.director.push_scene("settings")
        
    def exit_game(self):
        """Exit the game"""
        # Save before exiting if there's current save data
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