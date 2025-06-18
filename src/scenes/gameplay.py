# ============================================================================
# FILE: src/scenes/gameplay.py
# ============================================================================
from src.core.director import Scene
from src.entities.player import Player
from src.entities.enemies.cancer_base import CancerEnemy
from src.ui.hud import HUD
import random

class GameplayScene(Scene):
    """Main gameplay scene"""
    def __init__(self, director, input_manager):
        super().__init__(director)
        self.input_manager = input_manager
        
        # Get systems
        self.asset_manager = director.get_system('asset_manager')
        self.gravity_manager = director.get_system('gravity_manager')
        self.save_manager = director.get_system('save_manager')
        
        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.platform_list = arcade.SpriteList()
        self.item_list = arcade.SpriteList()
        
        # Game state
        self.score = 0
        self.current_level = 1
        self.game_over = False
        
        # Camera
        self.camera = None
        self.gui_camera = None
        
        # HUD
        self.hud = None
        
        # Multiplayer
        self.is_multiplayer = director.get_system('is_multiplayer')
        self.other_players = {}
        
    def on_enter(self):
        """Setup gameplay scene"""
        # Create cameras
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.gui_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Create player
        character_data = self._get_selected_character()
        self.player = Player(character_data, self.asset_manager, self.input_manager)
        self.player.center_x = 200
        self.player.center_y = 200
        self.player_list.append(self.player)
        
        # Create HUD
        self.hud = HUD(self.player)
        
        # Load level
        self.load_level(self.current_level)
        
        # Spawn initial enemies
        self.spawn_enemies()
        
    def _get_selected_character(self) -> dict:
        """Get selected character data"""
        if self.save_manager.current_save:
            # Get from save data
            squad_id = self.save_manager.current_save.game_data.get('selected_squad', '31A')
            char_id = self.save_manager.current_save.game_data.get('selected_character', 'ruka')
            
            # Load from config (simplified for demo)
            return {
                'id': char_id,
                'name': 'Ruka',
                'health': 100,
                'speed': 6,
                'jump_power': 15,
                'abilities': ['Double Jump', 'Dash Attack']
            }
            
    def load_level(self, level_num: int):
        """Load level data"""
        # Create simple test platforms
        for x in range(0, 2000, 200):
            platform = arcade.Sprite()
            platform.center_x = x
            platform.center_y = 50
            platform.width = 200
            platform.height = 20
            platform.texture = self.asset_manager.get_texture('default_ui_button')
            self.platform_list.append(platform)
            
        # Add some elevated platforms
        positions = [(400, 200), (800, 300), (1200, 250), (1600, 350)]
        for x, y in positions:
            platform = arcade.Sprite()
            platform.center_x = x
            platform.center_y = y
            platform.width = 150
            platform.height = 20
            platform.texture = self.asset_manager.get_texture('default_ui_button')
            self.platform_list.append(platform)
            
    def spawn_enemies(self):
        """Spawn enemies in level"""
        enemy_positions = [(600, 150), (1000, 150), (1400, 250)]
        
        for x, y in enemy_positions:
            size = random.choice(['small', 'medium', 'large'])
            enemy = CancerEnemy('basic', size)
            enemy.center_x = x
            enemy.center_y = y
            enemy.texture = self.asset_manager.get_texture('default_enemy')
            self.enemy_list.append(enemy)
            
    def update(self, delta_time: float):
        """Update gameplay"""
        if self.game_over:
            return
            
        # Update player
        self.player.update(delta_time, self.gravity_manager, self.platform_list)
        
        # Update enemies
        for enemy in self.enemy_list:
            enemy.update(delta_time, self.player_list, self.gravity_manager)
            
        # Check player-enemy collisions
        hit_enemies = arcade.check_for_collision_with_list(self.player, self.enemy_list)
        for enemy in hit_enemies:
            if self.player.is_attacking:
                enemy.take_damage(10)
                self.score += 10 * enemy.scale
                
        # Update camera to follow player
        self.center_camera_on_player()
        
        # Check win/lose conditions
        if self.player.health <= 0:
            self.game_over = True
            self.director.push_scene('game_over')
            
    def center_camera_on_player(self):
        """Center camera on player with bounds"""
        screen_center_x = self.player.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player.center_y - (self.camera.viewport_height / 2)
        
        # Don't let camera go negative
        screen_center_x = max(screen_center_x, 0)
        screen_center_y = max(screen_center_y, 0)
        
        self.camera.move_to((screen_center_x, screen_center_y))
        
    def draw(self):
        """Draw gameplay"""
        arcade.start_render()
        
        # Use game camera
        self.camera.use()
        
        # Draw game world
        self.platform_list.draw()
        self.enemy_list.draw()
        self.player_list.draw()
        self.item_list.draw()
        
        # Use GUI camera for HUD
        self.gui_camera.use()
        self.hud.draw()
        
    def on_key_press(self, key, modifiers):
        """Handle key press"""
        if key == arcade.key.ESCAPE:
            self.director.push_scene('pause')