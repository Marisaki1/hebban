"""
Player character entity for Arcade 3.0.0
"""

import arcade
from typing import List, Optional
from src.input.input_manager import InputAction
from src.core.constants import ATTACK_COOLDOWN, COMBO_TIME_LIMIT, INVULNERABLE_TIME

class Player(arcade.Sprite):
    """Player character with movement, combat and abilities"""
    
    def __init__(self, character_data: dict, input_manager):
        super().__init__()
        
        # Character data
        self.character_data = character_data
        self.character_id = character_data.get('id', 'ruka')
        
        # Stats from character data
        self.max_health = character_data.get('health', 100)
        self.health = self.max_health
        self.move_speed = character_data.get('speed', 5)
        self.jump_power = character_data.get('jump_power', 15)
        self.attack_power = character_data.get('attack', 8)
        self.defense = character_data.get('defense', 6)
        self.abilities = character_data.get('abilities', [])
        
        # Set texture from asset manager
        self._load_texture()
        
        # Physics
        self.velocity = [0, 0]
        self.on_ground = False
        self.facing_right = True
        
        # Special abilities
        self.can_double_jump = 'Double Jump' in self.abilities
        self.has_double_jumped = False
        
        # Combat system
        self.is_attacking = False
        self.attack_cooldown = 0
        self.attack_combo = 0
        self.combo_timer = 0
        self.max_combo_time = COMBO_TIME_LIMIT
        
        # Status effects
        self.invulnerable = False
        self.invulnerable_time = 0
        self.attack_boost = 1.0
        self.defense_boost = 1.0
        
        # Game state
        self.score = 0
        
        # Input reference
        self.input_manager = input_manager
        
    def _load_texture(self):
        """Load character texture"""
        try:
            # Try to get texture from asset manager
            from src.core.game import HeavenBurnsRed
            game = arcade.get_window()
            if hasattr(game, 'asset_manager'):
                texture = game.asset_manager.get_texture(f"{self.character_id}_idle")
                if texture:
                    self.texture = texture
                    return
        except:
            pass
            
        # Fallback - no texture (will be invisible but functional)
        print(f"No texture found for character {self.character_id}")
        
    def update(self, delta_time: float, gravity_manager, platforms):
        """Update player state"""
        # Handle input
        self.handle_input()
        
        # Apply gravity
        if gravity_manager:
            gravity_manager.apply_gravity(self.velocity, None, delta_time)
        else:
            # Fallback gravity
            self.velocity[1] -= 0.5 * delta_time * 60
            
        # Apply movement
        self.center_x += self.velocity[0] * delta_time * 60
        self.center_y += self.velocity[1] * delta_time * 60
        
        # Check platform collisions
        self.check_platform_collisions(platforms)
        
        # Update timers
        self.update_timers(delta_time)
        
        # Keep on screen bounds
        self.check_screen_bounds()
        
    def handle_input(self):
        """Handle player input"""
        if not self.input_manager:
            return
            
        # Movement
        move_x, _ = self.input_manager.get_movement_vector()
        self.velocity[0] = move_x * self.move_speed
        
        # Update facing direction
        if move_x > 0:
            self.facing_right = True
        elif move_x < 0:
            self.facing_right = False
            
        # Jumping
        if self.input_manager.is_action_pressed(InputAction.JUMP):
            self.jump()
            
        # Combat
        if self.input_manager.is_action_pressed(InputAction.ACTION_1):
            self.attack(1)
        elif self.input_manager.is_action_pressed(InputAction.ACTION_2):
            self.attack(2)
            
    def jump(self):
        """Handle jumping with double jump ability"""
        if self.on_ground:
            # Normal jump
            self.velocity[1] = self.jump_power
            self.on_ground = False
            self.has_double_jumped = False
            
            # Play jump sound
            try:
                game = arcade.get_window()
                if hasattr(game, 'sound_manager'):
                    game.sound_manager.play_sfx("jump")
            except:
                pass
                
        elif self.can_double_jump and not self.has_double_jumped:
            # Double jump
            self.velocity[1] = self.jump_power * 0.8
            self.has_double_jumped = True
            
            # Create air dash effect if Yuki
            if self.character_id == 'yuki':
                try:
                    game = arcade.get_window()
                    if hasattr(game, 'particle_manager'):
                        game.particle_manager.create_effect('dust', self.center_x, self.center_y)
                except:
                    pass
                    
    def attack(self, attack_type: int):
        """Perform attack"""
        if self.attack_cooldown <= 0 and not self.is_attacking:
            self.is_attacking = True
            self.attack_cooldown = ATTACK_COOLDOWN
            
            # Update combo
            if self.combo_timer > 0:
                self.attack_combo += 1
            else:
                self.attack_combo = 1
            self.combo_timer = self.max_combo_time
            
            # Special attacks based on character
            self.perform_special_attack(attack_type)
            
            # Play attack sound
            try:
                game = arcade.get_window()
                if hasattr(game, 'sound_manager'):
                    if attack_type == 1:
                        game.sound_manager.play_sfx("dash_attack")
                    else:
                        game.sound_manager.play_sfx("quick_strike")
            except:
                pass
                
    def perform_special_attack(self, attack_type: int):
        """Perform character-specific special attacks"""
        # Ruka - Dash Attack
        if self.character_id == 'ruka' and attack_type == 1:
            if 'Dash Attack' in self.abilities:
                direction = 1 if self.facing_right else -1
                self.center_x += 100 * direction
                
                # Create impact effect
                try:
                    game = arcade.get_window()
                    if hasattr(game, 'particle_manager'):
                        game.particle_manager.create_effect('impact', self.center_x, self.center_y)
                except:
                    pass
                    
        # Yuki - Quick Strike
        elif self.character_id == 'yuki' and attack_type == 1:
            if 'Quick Strike' in self.abilities:
                # Multi-hit attack (handled in enemy collision)
                self.attack_combo += 2  # Bonus combo for multi-hit
                
        # Karen - Ground Pound
        elif self.character_id == 'karen' and attack_type == 2:
            if 'Ground Pound' in self.abilities and not self.on_ground:
                self.velocity[1] = -self.jump_power * 1.5  # Fast downward slam
                
    def check_platform_collisions(self, platforms):
        """Check and resolve platform collisions"""
        if not platforms:
            # Simple ground collision
            if self.center_y <= 100:
                self.center_y = 100
                self.velocity[1] = 0
                self.on_ground = True
                self.has_double_jumped = False
            else:
                self.on_ground = False
            return
            
        # Check collision with platform sprites
        self.on_ground = False
        
        platform_hits = arcade.check_for_collision_with_list(self, platforms)
        for platform in platform_hits:
            # Simple top collision (landing on platform)
            if self.velocity[1] <= 0 and self.center_y > platform.center_y:
                self.center_y = platform.top + self.height // 2
                self.velocity[1] = 0
                self.on_ground = True
                self.has_double_jumped = False
                break
                
    def check_screen_bounds(self):
        """Keep player within screen bounds"""
        # Left boundary
        if self.center_x < 32:
            self.center_x = 32
            
        # Right boundary (assuming level width of 2000)
        if self.center_x > 2000 - 32:
            self.center_x = 2000 - 32
            
        # Bottom boundary (fall death)
        if self.center_y < -100:
            self.take_damage(self.health)  # Instant death from falling
            
    def update_timers(self, delta_time: float):
        """Update various timers"""
        # Attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time
            
        # Combo timer
        if self.combo_timer > 0:
            self.combo_timer -= delta_time
            if self.combo_timer <= 0:
                self.attack_combo = 0
                
        # Invulnerability timer
        if self.invulnerable_time > 0:
            self.invulnerable_time -= delta_time
            if self.invulnerable_time <= 0:
                self.invulnerable = False
                
        # End attack state
        if self.is_attacking and self.attack_cooldown <= ATTACK_COOLDOWN * 0.5:
            self.is_attacking = False
            
    def take_damage(self, damage: int):
        """Take damage from enemy or environment"""
        if self.invulnerable:
            return
            
        # Apply defense
        actual_damage = max(1, int(damage / self.defense_boost))
        self.health -= actual_damage
        
        # Set invulnerability
        self.invulnerable = True
        self.invulnerable_time = INVULNERABLE_TIME
        
        # Reset combo on taking damage
        self.attack_combo = 0
        self.combo_timer = 0
        
        # Play hurt sound
        try:
            game = arcade.get_window()
            if hasattr(game, 'sound_manager'):
                game.sound_manager.play_sfx("hurt")
        except:
            pass
            
        # Check for death
        if self.health <= 0:
            self.health = 0
            # Death will be handled by the gameplay scene
            
    def heal(self, amount: int) -> int:
        """Heal the player"""
        old_health = self.health
        self.health = min(self.health + amount, self.max_health)
        actual_heal = self.health - old_health
        
        # Create healing effect
        if actual_heal > 0:
            try:
                game = arcade.get_window()
                if hasattr(game, 'particle_manager'):
                    game.particle_manager.create_effect('healing', self.center_x, self.center_y)
                if hasattr(game, 'sound_manager'):
                    game.sound_manager.play_sfx("collect_health")
            except:
                pass
                
        return actual_heal
        
    def add_score(self, points: int):
        """Add score points"""
        self.score += points
        
        # Play score sound
        try:
            game = arcade.get_window()
            if hasattr(game, 'sound_manager'):
                game.sound_manager.play_sfx("collect_coin")
        except:
            pass
            
    def get_attack_damage(self) -> int:
        """Get current attack damage with modifiers"""
        base_damage = self.attack_power
        combo_multiplier = 1.0 + (self.attack_combo - 1) * 0.2
        return int(base_damage * self.attack_boost * combo_multiplier)
        
    def reset_position(self, x: float, y: float):
        """Reset player position (for respawning)"""
        self.center_x = x
        self.center_y = y
        self.velocity = [0, 0]
        self.on_ground = False
        self.has_double_jumped = False
        
    def get_stats(self) -> dict:
        """Get current player stats for display"""
        return {
            'health': self.health,
            'max_health': self.max_health,
            'score': self.score,
            'combo': self.attack_combo,
            'facing_right': self.facing_right,
            'on_ground': self.on_ground,
            'is_attacking': self.is_attacking,
            'abilities': len(self.abilities)
        }