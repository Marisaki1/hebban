# ============================================================================
# FILE: src/scenes/pause.py
# ============================================================================
class PauseMenu(MenuState):
    """Pause menu overlay"""
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Paused"
        
        # Create menu items
        self.menu_items = [
            MenuItem("Resume", self.resume_game, SCREEN_WIDTH // 2, 400),
            MenuItem("Settings", self.show_settings, SCREEN_WIDTH // 2, 320),
            MenuItem("Save Game", self.save_game, SCREEN_WIDTH // 2, 240),
            MenuItem("Quit to Menu", self.quit_to_menu, SCREEN_WIDTH // 2, 160)
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
        """Save current game"""
        save_manager = self.director.get_system('save_manager')
        if save_manager:
            save_manager.save_game(1)
            # Show confirmation
            
    def quit_to_menu(self):
        """Return to main menu"""
        # Save before quitting
        save_manager = self.director.get_system('save_manager')
        if save_manager:
            save_manager.save_game(1)
            
        self.director.change_scene('main_menu')
        
    def draw(self):
        """Draw pause menu with dimmed background"""
        # Draw semi-transparent overlay
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            (0, 0, 0, 180)
        )
        
        # Draw menu
        super().draw()