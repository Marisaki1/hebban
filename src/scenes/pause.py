"""
Pause menu overlay
"""

import arcade
from src.menu.menu_state import MenuState, MenuItem
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class PauseMenu(MenuState):
    """Pause menu overlay during gameplay"""
    
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Paused"
        self.scene_name = "pause"
        
        # Create menu items
        menu_y_start = 350
        menu_spacing = 60
        
        self.menu_items = [
            MenuItem(
                "Resume Game",
                self.resume_game,
                SCREEN_WIDTH // 2,
                menu_y_start
            ),
            MenuItem(
                "Settings",
                self.show_settings,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing
            ),
            MenuItem(
                "Save Game",
                self.save_game,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing * 2
            ),
            MenuItem(
                "Quit to Menu",
                self.quit_to_menu,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing * 3
            )
        ]
        
        if self.menu_items:
            self.menu_items[0].is_selected = True
            
    def resume_game(self):
        """Resume gameplay"""
        self.director.pop_scene()
        
    def show_settings(self):
        """Show settings menu"""
        self.director.push_scene('settings')
        
    def save_game(self):
        """Save current game progress"""
        save_manager = self.director.get_system('save_manager')
        if save_manager and save_manager.current_save:
            # Update play time and progress before saving
            self.update_save_progress()
            
            # Save to slot 1
            success = save_manager.save_game(1)
            
            # Show save confirmation
            if success:
                self.show_save_confirmation()
                
    def update_save_progress(self):
        """Update save data with current progress"""
        save_manager = self.director.get_system('save_manager')
        if not save_manager or not save_manager.current_save:
            return
            
        # Get current gameplay scene to extract progress data
        gameplay_scene = None
        for scene in self.director.scene_stack:
            if hasattr(scene, 'player') and hasattr(scene, 'current_wave'):
                gameplay_scene = scene
                break
                
        if gameplay_scene:
            game_data = save_manager.current_save.game_data
            progress = game_data.get('progress', {})
            
            # Update progress
            progress['current_level'] = gameplay_scene.current_level
            progress['total_score'] = max(progress.get('total_score', 0), gameplay_scene.score)
            
            # Add current level to completed if player has progressed
            if gameplay_scene.current_wave > 1:
                completed = progress.get('completed_levels', [])
                level_id = f"level_{gameplay_scene.current_level}"
                if level_id not in completed:
                    completed.append(level_id)
                    progress['completed_levels'] = completed
                    
            game_data['progress'] = progress
            
    def show_save_confirmation(self):
        """Show save confirmation (placeholder)"""
        # In a full implementation, this would show a temporary message
        print("Game saved successfully!")
        
    def quit_to_menu(self):
        """Return to main menu"""
        # Auto-save before quitting
        self.save_game()
        
        # Return to main menu
        self.director.change_scene('main_menu')
        
    def draw(self):
        """Draw pause menu with dimmed background"""
        # Draw semi-transparent overlay over the game
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            (0, 0, 0, 150)  # Semi-transparent black
        )
        
        # Draw pause menu background
        menu_width = 400
        menu_height = 350
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            menu_width, menu_height,
            arcade.color.DARK_BLUE_GRAY
        )
        arcade.draw_rectangle_outline(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            menu_width, menu_height,
            arcade.color.WHITE, 3
        )
        
        # Draw title
        arcade.draw_text(
            self.title,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 120,
            arcade.color.CRIMSON,
            36,
            anchor_x="center"
        )
        
        # Draw menu items
        for item in self.menu_items:
            item.draw()
            
        # Draw controls hint
        arcade.draw_text(
            "Use Arrow Keys to navigate, Enter to select",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 140,
            arcade.color.LIGHT_GRAY,
            12,
            anchor_x="center"
        )