"""
Fixed gameplay scene with proper character loading and game over handling
"""

import arcade
import random
from src.core.director import Scene
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.player import Player
from src.entities.enemy import CancerEnemy, EnemySpawner
from src.data.squad_data import get_character_data
from src.ui.hud import HUD

class GameplayScene(Scene):
    """Main gameplay scene with FIXED character loading and game over handling"""
    
    def __init__(self, director, input_manager):
        super().__init__(director)
        self.input_manager = input_manager
        
        # Get systems
        self.gravity_manager = director.get_system('gravity_manager')
        self.save_manager = director.get_system('save_manager')
        self.sound_manager = director.get_system('sound_manager')
        self.particle_manager = director.get_system('particle_manager')
        self.asset_manager = director.get_system('asset_manager')
        
        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.platform_list = arcade.SpriteList()
        self.item_list = arcade.SpriteList()
        
        # Game objects
        self.player = None
        self.hud = None
        self.enemy_spawner = EnemySpawner()
        
        # Cameras
        self.camera = None
        self.gui_camera = None
        
        # Game state
        self.current_level = 1
        self.score = 0
        self.game_over = False
        self.game_over_processed = False  # Prevent multiple game over callbacks
        self.victory = False
        self.level_timer = 0
        self.spawn_timer = 0
        
        # Level progression
        self.enemies_defeated = 0
        self.enemies_per_wave = 5
        self.current_wave = 1
 
        # FIXED: Single callback tracking to prevent multiple schedules
        self.game_over_callback_scheduled = False
        
    def on_enter(self):
        """Setup gameplay scene"""
        # FIXED: Reset all game over states
        self.game_over = False
        self.game_over_processed = False
        self.game_over_callback_scheduled = False
        self.scheduled_callbacks = []
        self.victory = False
        
        # Create cameras
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.gui_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Clear particle effects
        if self.particle_manager:
            self.particle_manager.clear()
            
        # FIXED: Create player with proper character loading
        character_data = self._get_selected_character()
        if character_data:
            self.player = Player(character_data, self.input_manager)
            self.player.center_x = 200
            self.player.center_y = 200
            self.player_list.append(self.player)
            
            print(f"✓ Gameplay started with {character_data['name']} ({character_data['id']})")
        else:
            print("ERROR: Failed to load character data!")
            # Fallback to default character
            default_char = {
                'id': 'ruka',
                'name': 'Ruka Kayamori',
                'health': 100,
                'speed': 6,
                'jump_power': 15,
                'attack': 8,
                'defense': 6,
                'abilities': ['Double Jump', 'Dash Attack', 'Leadership Boost']
            }
            self.player = Player(default_char, self.input_manager)
            self.player.center_x = 200
            self.player.center_y = 200
            self.player_list.append(self.player)
            print("⚠ Used fallback character (Ruka)")
        
        # Create HUD
        self.hud = HUD(self.player)
        
        # Load level
        self.load_level()
        
        # Setup enemy spawner
        self.setup_enemy_spawns()
        
        # Spawn initial enemies
        self.spawn_initial_enemies()
        
        # Start background music
        if self.sound_manager:
            self.sound_manager.play_music("battle_theme")
            
    def on_exit(self):
        """Cleanup when leaving gameplay"""
        # Clear scheduled callbacks
        self.clear_scheduled_callbacks()
        
        if self.sound_manager:
            self.sound_manager.stop_music()
        if self.particle_manager:
            self.particle_manager.clear()
            
    def clear_scheduled_callbacks(self):
            """Clear all scheduled callbacks to prevent conflicts"""
            if hasattr(self, 'scheduled_callbacks'):
                for callback in self.scheduled_callbacks:
                    try:
                        arcade.unschedule(callback)
                    except:
                        pass
                self.scheduled_callbacks.clear()
            
    def schedule_callback(self, callback, delay: float):
            """Schedule a callback and track it"""
            if not hasattr(self, 'scheduled_callbacks'):
                self.scheduled_callbacks = []
            self.scheduled_callbacks.append(callback)
            arcade.schedule(callback, delay)
        
    def on_pause(self):
        """Pause gameplay"""
        if self.sound_manager:
            self.sound_manager.pause_music()
            
    def on_resume(self):
        """Resume gameplay"""
        if self.sound_manager:
            self.sound_manager.resume_music()
            
    def _get_selected_character(self) -> dict:
        """FIXED: Get selected character data from save"""
        if self.save_manager and self.save_manager.current_save:
            game_data = self.save_manager.current_save.game_data
            squad_id = game_data.get('selected_squad', '31A')
            char_id = game_data.get('selected_character', 'ruka')
            
            print(f"Loading character: {char_id} from squad: {squad_id}")
            
            character = get_character_data(squad_id, char_id)
            if character:
                print(f"✓ Successfully loaded character: {character['name']}")
                return character
            else:
                print(f"ERROR: Character {char_id} not found in squad {squad_id}")
        else:
            print("ERROR: No save manager or save data available")
                
        # Return None to trigger fallback
        return None
        
    def load_level(self):
        """Load level platforms and environment"""
        # Create ground platforms
        for x in range(0, 2000, 200):
            platform = self.asset_manager.create_sprite("platform")
            platform.center_x = x + 100
            platform.center_y = 50
            self.platform_list.append(platform)
            
        # Create elevated platforms
        platform_configs = [
            # (x, y, width_multiplier)
            (400, 200, 1),
            (700, 150, 1),
            (1000, 250, 1),
            (1300, 200, 1),
            (1600, 300, 1),
            (1900, 180, 1),
            
            # Floating platforms
            (500, 350, 0.5),
            (800, 400, 0.5),
            (1100, 450, 0.5),
            (1400, 380, 0.5),
            
            # Vertical platforms (walls)
            (600, 120, 0.3),
            (1200, 150, 0.3),
        ]
        
        for x, y, scale in platform_configs:
            platform = self.asset_manager.create_sprite("platform")
            platform.center_x = x
            platform.center_y = y
            platform.scale = scale
            self.platform_list.append(platform)
            
    def setup_enemy_spawns(self):
        """Setup enemy spawn points"""
        spawn_points = [
            (600, 200, "basic", "small"),
            (1000, 200, "basic", "small"),
            (1400, 200, "basic", "medium"),
            (800, 300, "basic", "small"),
            (1200, 300, "basic", "medium"),
            (1600, 200, "basic", "large"),
        ]
        
        for x, y, enemy_type, size in spawn_points:
            self.enemy_spawner.add_spawn_point(x, y, enemy_type, size)
            
    def spawn_initial_enemies(self):
        """Spawn initial wave of enemies"""
        initial_wave = [
            {'x': 600, 'y': 200, 'type': 'basic', 'size': 'small'},
            {'x': 1000, 'y': 200, 'type': 'basic', 'size': 'small'},
            {'x': 1400, 'y': 200, 'type': 'basic', 'size': 'medium'},
        ]
        
        self.enemy_spawner.spawn_wave(self.enemy_list, initial_wave)
        
    def update(self, delta_time: float):
        """Update gameplay"""
        if self.game_over:
            return
            
        # Update level timer
        self.level_timer += delta_time
        
        # Update player
        self.player.update(delta_time, self.gravity_manager, self.platform_list)
        
        # Update enemies
        for enemy in self.enemy_list:
            enemy.update(delta_time, self.player_list, self.gravity_manager)
            
        # Update enemy spawner
        self.enemy_spawner.update(delta_time, self.enemy_list)
        
        # Check player-enemy collisions
        self.check_combat_collisions()
        
        # Update particle effects
        if self.particle_manager:
            self.particle_manager.update(delta_time)
            
        # Update HUD
        if self.hud:
            self.hud.update(delta_time)
            
        # Update camera
        self.update_camera()
        
        # Check win/lose conditions
        self.check_game_conditions()
        
    def check_combat_collisions(self):
        """Check player-enemy combat collisions"""
        hit_enemies = arcade.check_for_collision_with_list(self.player, self.enemy_list)
        
        for enemy in hit_enemies:
            if self.player.is_attacking:
                # Player hits enemy
                damage = self.player.get_attack_damage()
                enemy.take_damage(damage)
                
                # Add score based on enemy and combo
                base_score = enemy.score_value
                combo_bonus = self.player.attack_combo * 5
                score_gained = base_score + combo_bonus
                
                self.player.add_score(score_gained)
                self.score += score_gained
                if self.hud:
                    self.hud.score = self.score
                    
                # Check if enemy died
                if enemy.health <= 0:
                    self.enemies_defeated += 1
                    
                    # Create death effect
                    if self.particle_manager:
                        self.particle_manager.create_effect('explosion', enemy.center_x, enemy.center_y)
                        
            else:
                # Enemy hits player (if not invulnerable)
                if not self.player.invulnerable:
                    self.player.take_damage(enemy.damage)
                    
                    # Knockback effect
                    direction = 1 if enemy.center_x < self.player.center_x else -1
                    self.player.velocity[0] += direction * 5
                    
    def update_camera(self):
        """Update camera to follow player"""
        # Calculate camera position centered on player
        camera_x = self.player.center_x - SCREEN_WIDTH // 2
        camera_y = self.player.center_y - SCREEN_HEIGHT // 2
        
        # Clamp camera to level bounds
        camera_x = max(0, min(camera_x, 2000 - SCREEN_WIDTH))
        camera_y = max(0, camera_y)
        
        # Apply camera position
        self.camera.move_to((camera_x, camera_y))
        
    def check_game_conditions(self):
        """Check for win/lose conditions"""
        # FIXED: Check player death (only process once)
        if self.player.health <= 0 and not self.game_over_processed:
            self.handle_game_over()
            return
            
        # Check wave completion
        if len(self.enemy_list) == 0 and not self.victory:
            self.complete_wave()
            
        # Check fall death
        if self.player.center_y < -100 and not self.game_over_processed:
            self.player.take_damage(self.player.health)
            
    def handle_game_over(self):
        """FIXED: Handle game over (called only once)"""
        if self.game_over_processed:
            return
            
        self.game_over = True
        self.game_over_processed = True
        
        print("Game Over - Returning to main menu in 3 seconds")
        
        # Save progress before game over
        self.save_game_progress()
        
        if self.sound_manager:
            self.sound_manager.stop_music()
            self.sound_manager.play_sfx("game_over")
            
        # FIXED: Use a simpler callback approach
        def return_to_menu(dt):
            try:
                # Clear the scheduled callback first
                arcade.unschedule(return_to_menu)
                # Change scene
                self.director.change_scene('main_menu')
            except Exception as e:
                print(f"Error returning to menu: {e}")
                
        # Schedule only once
        arcade.schedule(return_to_menu, 3.0)
        
    def save_game_progress(self):
        """Save current game progress"""
        if self.save_manager and self.save_manager.current_save:
            game_data = self.save_manager.current_save.game_data
            progress = game_data.get('progress', {})
            
            # Update progress
            progress['total_score'] = max(progress.get('total_score', 0), self.score)
            progress['last_wave'] = self.current_wave
            progress['play_time'] = progress.get('play_time', 0) + self.level_timer
            
            game_data['progress'] = progress
            
            # Auto-save
            self.save_manager.save_game(1)
            
    def complete_wave(self):
        """Complete current wave and spawn next"""
        if self.victory:
            return
            
        self.victory = True
        self.current_wave += 1
        
        if self.sound_manager:
            self.sound_manager.play_sfx("victory")
            
        # Create victory effects
        if self.particle_manager:
            for _ in range(5):
                x = self.player.center_x + random.randint(-100, 100)
                y = self.player.center_y + random.randint(-50, 100)
                self.particle_manager.create_effect('sparkle', x, y)
                
        # Spawn next wave after delay
        def spawn_next(dt):
            self.spawn_next_wave()
            
        arcade.schedule(spawn_next, 3.0)
        
    def spawn_next_wave(self):
        """Spawn next wave of enemies"""
        self.victory = False
        
        # Increase difficulty
        wave_configs = {
            2: [
                {'x': 500, 'y': 200, 'type': 'basic', 'size': 'small'},
                {'x': 800, 'y': 200, 'type': 'basic', 'size': 'medium'},
                {'x': 1100, 'y': 200, 'type': 'basic', 'size': 'small'},
                {'x': 1400, 'y': 200, 'type': 'basic', 'size': 'medium'},
            ],
            3: [
                {'x': 400, 'y': 200, 'type': 'basic', 'size': 'medium'},
                {'x': 700, 'y': 200, 'type': 'basic', 'size': 'small'},
                {'x': 1000, 'y': 200, 'type': 'basic', 'size': 'large'},
                {'x': 1300, 'y': 200, 'type': 'basic', 'size': 'medium'},
                {'x': 1600, 'y': 200, 'type': 'basic', 'size': 'small'},
            ],
            4: [
                {'x': 600, 'y': 200, 'type': 'basic', 'size': 'large'},
                {'x': 1200, 'y': 200, 'type': 'basic', 'size': 'boss'},
            ]
        }
        
        wave_config = wave_configs.get(self.current_wave, wave_configs[4])
        self.enemy_spawner.spawn_wave(self.enemy_list, wave_config)
        
    def on_key_press(self, key, modifiers):
        """Handle key press"""
        if key == arcade.key.ESCAPE and not self.game_over:
            self.director.push_scene('pause')
            
    def draw(self):
        """Draw gameplay scene"""
        # Use game camera
        self.camera.use()
        
        # Draw game world
        self.platform_list.draw()
        self.enemy_list.draw()
        self.player_list.draw()
        self.item_list.draw()
        
        # Draw particle effects
        if self.particle_manager:
            self.particle_manager.draw()
            
        # Use GUI camera for HUD
        self.gui_camera.use()
        
        # Draw HUD
        if self.hud:
            self.hud.draw()
            
        # Draw game state indicators
        self.draw_game_info()
        
    def draw_game_info(self):
        """Draw additional game information"""
        # Wave indicator
        arcade.draw_text(
            f"Wave {self.current_wave}",
            10, SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            16
        )
        
        # Enemy counter
        arcade.draw_text(
            f"Enemies: {len(self.enemy_list)}",
            10, SCREEN_HEIGHT - 60,
            arcade.color.WHITE,
            14
        )
        
        # Level timer
        minutes = int(self.level_timer // 60)
        seconds = int(self.level_timer % 60)
        arcade.draw_text(
            f"Time: {minutes:02d}:{seconds:02d}",
            10, SCREEN_HEIGHT - 90,
            arcade.color.WHITE,
            14
        )
        
        # Victory/Game Over messages
        if self.victory:
            arcade.draw_text(
                f"Wave {self.current_wave - 1} Complete!",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                arcade.color.YELLOW,
                32,
                anchor_x="center",
                anchor_y="center"
            )
        elif self.game_over:
            arcade.draw_text(
                "GAME OVER",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                arcade.color.RED,
                48,
                anchor_x="center",
                anchor_y="center"
            )
            
            arcade.draw_text(
                "Returning to Main Menu...",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 60,
                arcade.color.WHITE,
                20,
                anchor_x="center",
                anchor_y="center"
            )