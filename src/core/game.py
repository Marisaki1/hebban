# ============================================================================
# FILE: src/core/game.py - Updated with all systems
# ============================================================================
class HeavenBurnsRed(arcade.Window):
    """Main game class with all systems integrated"""
    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)
        
        # Core systems
        self.director = Director()
        self.input_manager = InputManager()
        self.asset_manager = AssetManager()
        self.save_manager = SaveManager()
        self.gravity_manager = GravityManager()
        
        # Register systems with director
        self.director.systems = {
            'input_manager': self.input_manager,
            'asset_manager': self.asset_manager,
            'save_manager': self.save_manager,
            'gravity_manager': self.gravity_manager,
            'is_multiplayer': False
        }
        
        # Frame rate
        self.set_update_rate(1/FPS)
        
    def setup(self):
        """Set up the game with all scenes"""
        # Load save data if exists
        save_slots = self.save_manager.get_save_files()
        if any(slot['exists'] for slot in save_slots):
            # Load most recent save
            self.save_manager.load_game(1)
        else:
            # Create new save
            self.save_manager.current_save = SaveData()
            
        # Register all scenes
        self.director.register_scene(
            "main_menu",
            MainMenu(self.director, self.input_manager)
        )
        self.director.register_scene(
            "squad_select",
            SquadSelectMenu(self.director, self.input_manager)
        )
        self.director.register_scene(
            "settings",
            SettingsMenu(self.director, self.input_manager)
        )
        self.director.register_scene(
            "leaderboard", 
            LeaderboardMenu(self.director, self.input_manager)
        )
        self.director.register_scene(
            "lobby_menu",
            LobbyMenu(self.director, self.input_manager)
        )
        
        # Start with main menu
        self.director.push_scene("main_menu")
        
    def on_draw(self):
        """Render the game"""
        self.director.draw()
        
    def update(self, delta_time: float):
        """Update game logic"""
        self.director.update(delta_time)
        self.input_manager.update_controller()
        
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
        # Auto-save on exit
        if self.save_manager.current_save:
            self.save_manager.save_game(1)
        super().on_close()