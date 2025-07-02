# src/entities/player.py - Fixed for Arcade 3.0.0
"""
Player character with full movement and combat - Fixed for Arcade 3.0.0
"""
import arcade
from src.systems.animation import Animation, AnimationController, AnimationState
from src.input.input_manager import InputAction
from typing import Optional, List

class Player(arcade.Sprite):
    """Player character with full movement and combat - Arcade 3.0.0 compatible"""
    def __init__(self, character_data: dict, input_manager):
        super().__init__()
        
        # Character data
        self.character_data = character_data
        self.character_id = character_data.get('id', 'unknown')
        self.player_id = None  # Set for multiplayer
        
        # Stats
        self.max_health = character_data.get('health', 100)
        self.health = self.max_health
        self.move_speed = character_data.get('speed', 5)
        self.jump_power = character_data.get('jump_power', 15)
        self.abilities = character_data.get('abilities', [])
        
        # Physics
        self.velocity = [0, 0]
        self.on_ground = False
        self.facing_right = True
        self.can_double_jump = 'Double Jump' in self.abilities
        self.has_double_jumped = False
        
        # Combat
        self.is_attacking = False
        self.attack_cooldown = 0
        self.attack_combo = 0
        self.combo_timer = 0
        self.max_combo_time = 2.0
        self.invulnerable = False
        self.invulnerable_time = 0
        
        # Buffs and effects
        self.attack_boost = 1.0
        self.defense_boost = 1.0
        self.active_powerups = []
        
        # Score tracking
        self.score = 0
        
        # Animation
        self.animation_controller = AnimationController()
        self.setup_animations()
        
        # Input
        self.input_manager = input_manager
        
        # Collision
        self.points = [
            [-16, -32], [16, -32],  # Bottom
            [16, 32], [-16, 32]     # Top
        ]
        
    def setup_animations(self):
        """Setup character animations using Arcade 3.0.0 compatible methods"""
        try:
            # Try to use sprite manager first
            from src.core.sprite_manager import sprite_manager
            self.animation_controller = sprite_manager.create_animation_controller(self.character_id)
            
            # Get a texture for the sprite
            portrait = sprite_manager.get_portrait(self.character_id)
            if portrait:
                self.texture = portrait
            
            print(f"✓ Loaded animations for {self.character_id}")
            return
        except Exception as e:
            print(f"Sprite manager failed for {self.character_id}: {e}")
        
        try:
            # Fallback to asset manager
            from src.core.asset_manager import asset_manager
            
            # Try to get character texture
            texture = asset_manager.get_texture(f'{self.character_id}_idle')
            if not texture:
                texture = asset_manager.get_texture('default_character')
            
            if texture:
                self.texture = texture
            
            # Create simple animations using single texture
            for state in AnimationState:
                animation = Animation([texture] if texture else [], 0.1, loop=(state != AnimationState.DEATH))
                self.animation_controller.add_animation(state, animation)
                
            print(f"✓ Created fallback animations for {self.character_id}")
            return
        except Exception as e:
            print(f"Asset manager fallback failed: {e}")
            
        try:
            # Ultimate fallback - create placeholder texture
            self._create_placeholder_texture()
        except Exception as e:
            print(f"Placeholder creation failed: {e}")
            
    def _create_placeholder_texture(self):
        """Create a placeholder texture using Arcade 3.0.0 methods"""
        try:
            # Method 1: Try Arcade 3.0.0 texture creation
            texture = arcade.Texture.create_filled(
                f"player_{self.character_id}", 
                (64, 64), 
                arcade.color.BLUE
            )
            self.texture = texture
        except Exception:
            try:
                # Method 2: Try Pillow 11.0.0 creation
                from PIL import Image
                image = Image.new('RGBA', (64, 64), (0, 100, 200, 255))
                texture = arcade.Texture(f"player_{self.character_id}_pil", image)
                self.texture = texture
            except Exception:
                # Method 3: No texture - sprite will use default
                pass
        
        # Create simple animation with available texture
        if self.texture:
            for state in AnimationState:
                animation = Animation([self.texture], 0.1, loop=(state != AnimationState.DEATH))
                self.animation_controller.add_animation(state, animation)
            
    def update(self, delta_time: float, gravity_manager, collision_map):
        """Update player state"""
        try:
            # Handle input
            self.handle_input()
            
            # Apply gravity
            zone_id = self.get_current_zone(collision_map)
            if gravity_manager:
                gravity_manager.apply_gravity(self.velocity, zone_id, delta_time)
            else:
                # Fallback gravity
                self.velocity[1] -= 0.5 * delta_time * 60
            
            # Apply movement
            self.center_x += self.velocity[0] * delta_time * 60
            self.center_y += self.velocity[1] * delta_time * 60
            
            # Check collisions
            self.check_collisions(collision_map)
            
            # Update combat timers
            if self.attack_cooldown > 0:
                self.attack_cooldown -= delta_time
                
            if self.invulnerable_time > 0:
                self.invulnerable_time -= delta_time
                if self.invulnerable_time <= 0:
                    self.invulnerable = False
                    
            # Update combo timer
            if self.attack_combo > 0:
                self.combo_timer -= delta_time
                if self.combo_timer <= 0:
                    self.attack_combo = 0
                    
            # Update powerups
            self.update_powerups(delta_time)
            
            # Update animation state
            self.update_animation_state()
            if self.animation_controller:
                self.animation_controller.update(delta_time)
                
                # Update texture from animation
                new_texture = self.animation_controller.get_current_texture()
                if new_texture:
                    self.texture = new_texture
                    
        except Exception as e:
            print(f"Player update error: {e}")
            
    def handle_input(self):
        """Handle player input"""
        try:
            if not self.input_manager:
                return
                
            # Movement
            move_x, _ = self.input_manager.get_movement_vector()
            self.velocity[0] = move_x * self.move_speed
            
            if move_x > 0:
                self.facing_right = True
            elif move_x < 0:
                self.facing_right = False
                
            # Jump
            if self.input_manager.is_action_pressed(InputAction.JUMP):
                self.jump()
                
            # Actions
            if self.input_manager.is_action_pressed(InputAction.ACTION_1):
                self.attack(1)
            elif self.input_manager.is_action_pressed(InputAction.ACTION_2):
                self.attack(2)
                
        except Exception as e:
            print(f"Input handling error: {e}")
            
    def jump(self):
        """Handle jumping"""
        try:
            if self.on_ground:
                self.velocity[1] = self.jump_power
                self.on_ground = False
                self.has_double_jumped = False
            elif self.can_double_jump and not self.has_double_jumped:
                self.velocity[1] = self.jump_power * 0.8
                self.has_double_jumped = True
        except Exception as e:
            print(f"Jump error: {e}")
            
    def attack(self, attack_type: int):
        """Perform attack"""
        try:
            if self.attack_cooldown <= 0 and not self.is_attacking:
                self.is_attacking = True
                self.attack_cooldown = 0.5
                
                # Update combo
                if self.combo_timer > 0:
                    self.attack_combo += 1
                else:
                    self.attack_combo = 1
                self.combo_timer = self.max_combo_time
                
                # Set animation
                if self.animation_controller:
                    if attack_type == 1:
                        self.animation_controller.change_state(AnimationState.ATTACK_1, force=True)
                    else:
                        self.animation_controller.change_state(AnimationState.ATTACK_2, force=True)
                        
                    self.animation_controller.lock_state()
                    
        except Exception as e:
            print(f"Attack error: {e}")
            
    def on_enemy_hit(self, enemy) -> int:
        """Called when player hits an enemy, returns damage dealt"""
        try:
            base_damage = self.character_data.get('attack', 10)
            combo_multiplier = 1.0 + (self.attack_combo - 1) * 0.2
            damage = int(base_damage * self.attack_boost * combo_multiplier)
            
            # Reset attack state
            self.is_attacking = False
            
            return damage
        except Exception as e:
            print(f"Enemy hit calculation error: {e}")
            return 10  # Default damage
            
    def take_damage(self, damage: int):
        """Take damage"""
        try:
            if not self.invulnerable:
                actual_damage = max(1, int(damage / self.defense_boost))
                self.health -= actual_damage
                self.invulnerable = True
                self.invulnerable_time = 1.0
                
                # Reset combo on taking damage
                self.attack_combo = 0
                self.combo_timer = 0
                
                if self.health <= 0:
                    self.health = 0
                    if self.animation_controller:
                        self.animation_controller.change_state(AnimationState.DEATH, force=True)
                else:
                    if self.animation_controller:
                        self.animation_controller.change_state(AnimationState.HURT, force=True)
                        
        except Exception as e:
            print(f"Take damage error: {e}")
                
    def update_powerups(self, delta_time: float):
        """Update active powerups"""
        try:
            expired_powerups = []
            
            for i, powerup in enumerate(self.active_powerups):
                powerup['duration'] -= delta_time
                if powerup['duration'] <= 0:
                    expired_powerups.append(i)
                    
                    # Remove powerup effect
                    if powerup['type'] == 'speed':
                        self.move_speed /= powerup.get('boost', 1.0)
                    elif powerup['type'] == 'damage':
                        self.attack_boost = 1.0
                    elif powerup['type'] == 'defense':
                        self.defense_boost = 1.0
                        
            # Remove expired powerups (in reverse order to maintain indices)
            for i in reversed(expired_powerups):
                self.active_powerups.pop(i)
                
        except Exception as e:
            print(f"Powerup update error: {e}")
            
    def check_collisions(self, collision_map):
        """Check and resolve collisions"""
        try:
            # Ground collision
            self.on_ground = False
            
            # Simple ground check - in full implementation use tilemap
            if self.center_y <= 100:  # Ground level
                self.center_y = 100
                self.velocity[1] = 0
                self.on_ground = True
                
            # Keep player on screen
            if self.center_x < 32:
                self.center_x = 32
            elif self.center_x > 2000 - 32:
                self.center_x = 2000 - 32
                
        except Exception as e:
            print(f"Collision check error: {e}")
            
    def get_current_zone(self, collision_map) -> Optional[str]:
        """Get current gravity zone"""
        # In full implementation, check tilemap for zone
        return None
        
    def update_animation_state(self):
        """Update animation based on current state"""
        try:
            if not self.animation_controller or self.animation_controller.state_locked:
                return
                
            if self.velocity[1] > 0:
                self.animation_controller.change_state(AnimationState.JUMP)
            elif self.velocity[1] < -1:
                self.animation_controller.change_state(AnimationState.FALL)
            elif abs(self.velocity[0]) > 0.1:
                self.animation_controller.change_state(AnimationState.RUN)
            else:
                self.animation_controller.change_state(AnimationState.IDLE)
                
        except Exception as e:
            print(f"Animation state update error: {e}")
            
    def set_animation_speed(self, animation_name: str, speed_multiplier: float):
        """Set animation speed for debugging/testing"""
        try:
            from src.core.sprite_manager import sprite_manager
            sprite_manager.set_character_animation_speed(self.character_id, animation_name, speed_multiplier)
            print(f"Animation speed change: {animation_name} -> {speed_multiplier}x")
        except Exception as e:
            print(f"Animation speed change failed: {e}")
        
    def heal(self, amount: int):
        """Heal the player"""
        try:
            old_health = self.health
            self.health = min(self.health + amount, self.max_health)
            return self.health - old_health
        except Exception as e:
            print(f"Heal error: {e}")
            return 0
        
    def add_score(self, points: int):
        """Add score points"""
        try:
            self.score += points
        except Exception as e:
            print(f"Add score error: {e}")
        
    def get_stats(self) -> dict:
        """Get current player stats"""
        try:
            return {
                'health': self.health,
                'max_health': self.max_health,
                'score': self.score,
                'combo': self.attack_combo,
                'facing_right': self.facing_right,
                'on_ground': self.on_ground,
                'is_attacking': self.is_attacking,
                'active_powerups': len(self.active_powerups)
            }
        except Exception as e:
            print(f"Get stats error: {e}")
            return {
                'health': 100,
                'max_health': 100,
                'score': 0,
                'combo': 0,
                'facing_right': True,
                'on_ground': True,
                'is_attacking': False,
                'active_powerups': 0
            }
            
    def add_powerup(self, powerup_type: str, duration: float, boost: float = 1.0):
        """Add a powerup effect"""
        try:
            # Apply immediate effect
            if powerup_type == 'speed':
                self.move_speed *= boost
            elif powerup_type == 'damage':
                self.attack_boost = boost
            elif powerup_type == 'defense':
                self.defense_boost = boost
            elif powerup_type == 'invincibility':
                self.invulnerable = True
                self.invulnerable_time = duration
                
            # Add to powerup list for tracking
            self.active_powerups.append({
                'type': powerup_type,
                'duration': duration,
                'boost': boost
            })
            
        except Exception as e:
            print(f"Add powerup error: {e}")
            
    def reset_position(self, x: float, y: float):
        """Reset player position (useful for respawning)"""
        try:
            self.center_x = x
            self.center_y = y
            self.velocity = [0, 0]
            self.on_ground = False
        except Exception as e:
            print(f"Reset position error: {e}")
            
    def debug_info(self) -> str:
        """Get debug information about the player"""
        try:
            return f"Player {self.character_id}: HP={self.health}/{self.max_health}, Pos=({self.center_x:.1f}, {self.center_y:.1f}), Vel=({self.velocity[0]:.1f}, {self.velocity[1]:.1f})"
        except Exception as e:
            return f"Player debug error: {e}"