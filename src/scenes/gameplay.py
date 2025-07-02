# src/scenes/gameplay.py - Fixed for Arcade 3.0
"""
Enhanced gameplay scene with sound and particle effects - Fixed for Arcade 3.0
"""

import arcade
import random
from src.core.director import Scene
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.player import Player
from src.entities.enemies.cancer_base import CancerEnemy
from src.ui.hud import HUD
from src.data.squad_data import get_character_data

def create_solid_color_sprite(width, height, color):
    """Create a solid color sprite using Arcade 3.0 methods"""
    try:
        # Method 1: Try Texture.create_filled (3.0 method)
        texture = arcade.Texture.create_filled(f"solid_{color}", (width, height), color)
        sprite = arcade.Sprite()
        sprite.texture = texture
        return sprite
    except Exception:
        pass
    
    try:
        # Method 2: Try creating with PIL if available
        from PIL import Image
        image = Image.new('RGBA', (width, height), color + (255,))
        texture = arcade.Texture(f"solid_{color}_pil", image)
        sprite = arcade.Sprite()
        sprite.texture = texture
        return sprite
    except Exception:
        pass
    
    try:
        # Method 3: Use basic sprite with default texture
        sprite = arcade.Sprite()
        # Set size properties
        sprite.width = width
        sprite.height = height
        return sprite
    except Exception as e:
        print(f"Failed to create solid color sprite: {e}")
        return arcade.Sprite()

class GameplayScene(Scene):
    """Main gameplay scene with all enhancements - Arcade 3.0 Compatible"""
    def __init__(self, director, input_manager):
        super().__init__(director)
        self.input_manager = input_manager
        
        # Get systems
        self.gravity_manager = director.get_system('gravity_manager')
        self.save_manager = director.get_system('save_manager')
        
        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.platform_list = arcade.SpriteList()
        self.item_list = arcade.SpriteList()
        
        # Player
        self.player = None
        
        # Game state
        self.score = 0
        self.current_level = 1
        self.game_over = False
        self.victory = False
        
        # Camera - Arcade 3.0 Style
        self.camera = None
        self.gui_camera = None
        
        # HUD
        self.hud = None
        
        # Multiplayer
        self.is_multiplayer = director.get_system('is_multiplayer')
        self.other_players = {}
        
        # Managers (with fallbacks)
        try:
            from src.core.sound_manager import sound_manager
            self.sound_manager = sound_manager
        except:
            self.sound_manager = None
            
        try:
            from src.effects.particle_system import particle_manager
            self.particle_manager = particle_manager
        except:
            self.particle_manager = None
        
    def on_enter(self):
        """Setup gameplay scene"""
        # Create cameras - Arcade 3.0 Style
        try:
            # Use standard Arcade 3.0 Camera
            self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.gui_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
            print("✓ Using Arcade 3.0 Camera")
        except Exception as e:
            print(f"✗ Camera creation failed: {e}")
            # Create dummy camera object
            self.camera = type('DummyCamera', (), {'use': lambda: None})()
            self.gui_camera = type('DummyCamera', (), {'use': lambda: None})()
        
        # Clear any existing particle effects
        if self.particle_manager:
            self.particle_manager.clear()
        
        # Create player with selected character
        character_data = self._get_selected_character()
        self.player = Player(character_data, self.input_manager)
        self.player.center_x = 200
        self.player.center_y = 200
        self.player_list.append(self.player)
        
        # Create HUD
        self.hud = HUD(self.player)
        
        # Load level
        self.load_level(self.current_level)
        
        # Spawn initial enemies
        self.spawn_enemies()
        
        # Play battle music
        if self.sound_manager:
            self.sound_manager.play_music("battle_theme")
        
        print(f"Gameplay started with character: {character_data['name']}")
        
    def on_exit(self):
        """Cleanup when leaving gameplay"""
        # Stop music
        if self.sound_manager:
            self.sound_manager.stop_music()
        
        # Clear particles
        if self.particle_manager:
            self.particle_manager.clear()
        
    def on_pause(self):
        """Pause gameplay"""
        if self.sound_manager:
            self.sound_manager.pause_music()
        
    def on_resume(self):
        """Resume gameplay"""
        if self.sound_manager:
            self.sound_manager.resume_music()
        
    def _get_selected_character(self) -> dict:
        """Get selected character data from save or default"""
        if self.save_manager and self.save_manager.current_save:
            # Get from save data
            squad_id = self.save_manager.current_save.game_data.get('selected_squad', '31A')
            char_id = self.save_manager.current_save.game_data.get('selected_character', 'ruka')
            
            # Get character data from squad data
            character = get_character_data(squad_id, char_id)
            if character:
                # Add the character ID if not present
                if 'id' not in character:
                    character['id'] = char_id
                return character
                
        # Default to Ruka if nothing selected
        return {
            'id': 'ruka',
            'name': 'Ruka Kayamori',
            'health': 100,
            'speed': 6,
            'jump_power': 15,
            'attack': 8,
            'defense': 6,
            'abilities': ['Double Jump', 'Dash Attack', 'Leadership Boost']
        }
            
    def load_level(self, level_num: int):
        """Load level data using proper Arcade 3.0 sprite creation"""
        # Create platforms using proper Arcade 3.0 methods
        platform_color = arcade.color.DARK_GRAY
        
        # Ground platforms
        for x in range(0, 2000, 200):
            platform = create_solid_color_sprite(200, 20, platform_color)
            platform.center_x = x
            platform.center_y = 50
            self.platform_list.append(platform)
            
        # Elevated platforms with variety
        platform_configs = [
            # (x, y, width, height)
            (400, 200, 150, 20),
            (800, 300, 150, 20),
            (1200, 250, 150, 20),
            (1600, 350, 150, 20),
            # Some vertical platforms
            (600, 150, 20, 100),
            (1000, 200, 20, 150),
            # Floating platforms
            (500, 400, 100, 20),
            (900, 450, 100, 20),
            (1300, 400, 100, 20),
        ]
        
        for x, y, width, height in platform_configs:
            platform = create_solid_color_sprite(width, height, platform_color)
            platform.center_x = x
            platform.center_y = y
            self.platform_list.append(platform)
            
    def spawn_enemies(self):
        """Spawn enemies in level"""
        enemy_configs = [
            # (x, y, size)
            (600, 150, 'small'),
            (1000, 150, 'small'),
            (1400, 300, 'medium'),
            (800, 400, 'small'),
            (1200, 400, 'medium'),
            (1800, 150, 'large'),
        ]
        
        for x, y, size in enemy_configs:
            enemy = CancerEnemy('basic', size)
            enemy.center_x = x
            enemy.center_y = y
            
            # Create a simple colored texture for enemy using new system
            enemy_colors = {
                'small': arcade.color.DARK_RED,
                'medium': arcade.color.DARK_ORANGE,
                'large': arcade.color.DARK_VIOLET
            }
            
            # Use the new sprite creation system
            try:
                enemy_sprite = create_solid_color_sprite(
                    int(64 * enemy.scale), 
                    int(64 * enemy.scale), 
                    enemy_colors.get(size, arcade.color.DARK_RED)
                )
                enemy.texture = enemy_sprite.texture
            except Exception as e:
                print(f"Error creating enemy texture: {e}")
                # Continue without texture - enemy will still function
            
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
                # Calculate damage and hit enemy
                damage = self.player.on_enemy_hit(enemy)
                enemy.take_damage(damage)
                
                # Update score based on combo
                base_score = 10 * enemy.scale
                combo_bonus = self.player.attack_combo * 5
                self.score += base_score + combo_bonus
                self.hud.score = self.score
                
                # Create hit effect
                if self.particle_manager:
                    self.particle_manager.create_effect('impact', enemy.center_x, enemy.center_y)
            else:
                # Enemy damages player
                self.player.take_damage(enemy.damage)
                
        # Update particle effects
        if self.particle_manager:
            self.particle_manager.update(delta_time)
        
        # Update HUD
        if self.hud:
            self.hud.update(delta_time)
        
        # Update camera to follow player
        self.center_camera_on_player()
        
        # Check win/lose conditions
        if self.player.health <= 0:
            self.game_over = True
            if self.sound_manager:
                self.sound_manager.stop_music()
                self.sound_manager.play_sfx("game_over")
            print("Game Over!")
            # Return to main menu after delay
            try:
                arcade.schedule(lambda dt: self.director.change_scene('main_menu'), 3.0)
            except:
                # Fallback if schedule doesn't work
                import threading
                threading.Timer(3.0, lambda: self.director.change_scene('main_menu')).start()
            
        # Check if all enemies defeated
        if len(self.enemy_list) == 0 and not self.victory:
            self.victory = True
            if self.sound_manager:
                self.sound_manager.play_sfx("victory")
            print(f"Level {self.current_level} Complete!")
            self.current_level += 1
            
            # Create victory effects
            if self.particle_manager:
                for _ in range(5):
                    x = self.player.center_x + random.randint(-100, 100)
                    y = self.player.center_y + random.randint(-50, 100)
                    self.particle_manager.create_effect('sparkle', x, y)
                
            # Spawn more enemies after a delay (for now)
            try:
                arcade.schedule(self.spawn_next_wave, 3.0)
            except:
                # Fallback
                import threading
                threading.Timer(3.0, self.spawn_next_wave).start()
            
    def spawn_next_wave(self, delta_time=None):
        """Spawn next wave of enemies"""
        try:
            arcade.unschedule(self.spawn_next_wave)
        except:
            pass
        self.victory = False
        self.spawn_enemies()
            
    def center_camera_on_player(self):
        """Center camera on player with bounds - Arcade 3.0 Style"""
        if not self.camera or not hasattr(self.camera, 'move_to'):
            return
            
        try:
            # Calculate camera position
            camera_x = self.player.center_x - SCREEN_WIDTH // 2
            camera_y = self.player.center_y - SCREEN_HEIGHT // 2
            
            # Don't let camera go too far negative
            camera_x = max(camera_x, 0)
            camera_y = max(camera_y, 0)
            
            # Update camera position using Arcade 3.0 method
            self.camera.move_to((camera_x, camera_y))
        except Exception as e:
            print(f"Camera update error: {e}")
        
    def draw(self):
        """Draw gameplay - Arcade 3.0 Style"""
        try:
            # Use game camera
            self.camera.use()
            
            # Draw game world using sprite lists
            self.platform_list.draw()
            self.enemy_list.draw()
            self.player_list.draw()
            self.item_list.draw()
            
            # Draw particle effects
            if self.particle_manager:
                self.particle_manager.draw()
                
        except Exception as e:
            print(f"Game camera draw error: {e}")
            # Fallback drawing without camera
            try:
                self.platform_list.draw()
                self.enemy_list.draw()
                self.player_list.draw()
                self.item_list.draw()
            except Exception as e2:
                print(f"Fallback draw error: {e2}")
        
        try:
            # Use GUI camera for HUD
            self.gui_camera.use()
            if self.hud:
                self.hud.draw()
                
        except Exception as e:
            print(f"GUI camera draw error: {e}")
            # Fallback HUD drawing without camera
            try:
                if self.hud:
                    self.hud.draw()
            except Exception as e2:
                print(f"Fallback HUD draw error: {e2}")
        
        try:
            # Draw debug info using direct arcade calls
            arcade.draw_text(
                f"Character: {self.player.character_data['name']}",
                10, SCREEN_HEIGHT - 80,
                arcade.color.WHITE,
                14
            )
            
            # Draw combo indicator
            if self.player.attack_combo > 0:
                combo_text = f"COMBO x{self.player.attack_combo}"
                arcade.draw_text(
                    combo_text,
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT - 100,
                    arcade.color.YELLOW,
                    24,
                    anchor_x="center"
                )
        except Exception as e:
            print(f"Debug info draw error: {e}")
        
    def on_key_press(self, key, modifiers):
        """Handle key press"""
        if key == arcade.key.ESCAPE:
            self.director.push_scene('pause')
            
        # Debug: Test particle effects with number keys 6-9
        elif key == arcade.key.KEY_6 and self.particle_manager:
            self.particle_manager.create_effect('impact', self.player.center_x, self.player.center_y)
            print("Impact effect")
        elif key == arcade.key.KEY_7 and self.particle_manager:
            self.particle_manager.create_effect('flame', self.player.center_x, self.player.center_y)
            print("Flame effect")
        elif key == arcade.key.KEY_8 and self.particle_manager:
            self.particle_manager.create_effect('healing', self.player.center_x, self.player.center_y)
            print("Healing effect")
        elif key == arcade.key.KEY_9 and self.particle_manager:
            self.particle_manager.create_effect('sparkle', self.player.center_x, self.player.center_y)
            print("Sparkle effect")