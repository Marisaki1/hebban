# ============================================================================
# FILE: src/entities/player.py - Fixed version
# ============================================================================
import arcade
from src.systems.animation import Animation, AnimationController, AnimationState
from src.input.input_manager import InputAction
from typing import Optional, List

class Player(arcade.Sprite):
    """Player character with full movement and combat"""
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
        """Setup character animations"""
        # Import here to avoid circular imports
        from src.core.asset_manager import AssetManager
        
        asset_manager = AssetManager()
        
        # Create default animations using asset manager
        texture = asset_manager.get_texture('default_character')
        
        # For now, use single frame animations
        # In full implementation, load sprite sheets
        for state in AnimationState:
            self.animation_controller.add_animation(
                state,
                Animation([texture], 0.1, loop=(state != AnimationState.DEATH))
            )
            
    def update(self, delta_time: float, gravity_manager, collision_map):
        """Update player state"""
        # Handle input
        self.handle_input()
        
        # Apply gravity
        zone_id = self.get_current_zone(collision_map)
        gravity_manager.apply_gravity(self.velocity, zone_id, delta_time)
        
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
        self.animation_controller.update(delta_time)
        
        # Update texture
        texture = self.animation_controller.get_current_texture()
        if texture:
            self.texture = texture
            if not self.facing_right:
                # Flip texture horizontally
                self.texture = texture
                
    def handle_input(self):
        """Handle player input"""
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
            
    def jump(self):
        """Handle jumping"""
        if self.on_ground:
            self.velocity[1] = self.jump_power
            self.on_ground = False
            self.has_double_jumped = False
        elif self.can_double_jump and not self.has_double_jumped:
            self.velocity[1] = self.jump_power * 0.8
            self.has_double_jumped = True
            
    def attack(self, attack_type: int):
        """Perform attack"""
        if self.attack_cooldown <= 0 and not self.is_attacking:
            self.is_attacking = True
            self.attack_cooldown = 0.5
            
            # Update combo
            if self.combo_timer > 0:
                self.attack_combo += 1
            else:
                self.attack_combo = 1
            self.combo_timer = self.max_combo_time
            
            if attack_type == 1:
                self.animation_controller.change_state(AnimationState.ATTACK_1, force=True)
            else:
                self.animation_controller.change_state(AnimationState.ATTACK_2, force=True)
                
            self.animation_controller.lock_state()
            
    def on_enemy_hit(self, enemy) -> int:
        """Called when player hits an enemy, returns damage dealt"""
        base_damage = self.character_data.get('attack', 10)
        combo_multiplier = 1.0 + (self.attack_combo - 1) * 0.2
        damage = int(base_damage * self.attack_boost * combo_multiplier)
        
        # Reset attack state
        self.is_attacking = False
        
        return damage
        
    def take_damage(self, damage: int):
        """Take damage"""
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
                self.animation_controller.change_state(AnimationState.DEATH, force=True)
            else:
                self.animation_controller.change_state(AnimationState.HURT, force=True)
                
    def update_powerups(self, delta_time: float):
        """Update active powerups"""
        expired_powerups = []
        
        for i, powerup in enumerate(self.active_powerups):
            powerup['duration'] -= delta_time
            if powerup['duration'] <= 0:
                expired_powerups.append(i)
                
                # Remove powerup effect
                if powerup['type'] == 'speed':
                    self.move_speed /= powerup['boost']
                elif powerup['type'] == 'damage':
                    self.attack_boost = 1.0
                elif powerup['type'] == 'defense':
                    self.defense_boost = 1.0
                    
        # Remove expired powerups (in reverse order to maintain indices)
        for i in reversed(expired_powerups):
            self.active_powerups.pop(i)
            
    def check_collisions(self, collision_map):
        """Check and resolve collisions"""
        # Ground collision
        self.on_ground = False
        
        # Simple ground check - in full implementation use tilemap
        if self.center_y <= 100:  # Ground level
            self.center_y = 100
            self.velocity[1] = 0
            self.on_ground = True
            
    def get_current_zone(self, collision_map) -> Optional[str]:
        """Get current gravity zone"""
        # In full implementation, check tilemap for zone
        return None
        
    def update_animation_state(self):
        """Update animation based on current state"""
        if self.animation_controller.state_locked:
            return
            
        if self.velocity[1] > 0:
            self.animation_controller.change_state(AnimationState.JUMP)
        elif self.velocity[1] < -1:
            self.animation_controller.change_state(AnimationState.FALL)
        elif abs(self.velocity[0]) > 0.1:
            self.animation_controller.change_state(AnimationState.RUN)
        else:
            self.animation_controller.change_state(AnimationState.IDLE)
            
    def set_animation_speed(self, animation_name: str, speed_multiplier: float):
        """Set animation speed for debugging/testing"""
        # This is a debug function - in full implementation would use sprite manager
        print(f"Animation speed change: {animation_name} -> {speed_multiplier}x")
        
    def heal(self, amount: int):
        """Heal the player"""
        old_health = self.health
        self.health = min(self.health + amount, self.max_health)
        return self.health - old_health
        
    def add_score(self, points: int):
        """Add score points"""
        self.score += points
        
    def get_stats(self) -> dict:
        """Get current player stats"""
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