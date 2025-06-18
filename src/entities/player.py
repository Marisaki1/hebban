# ============================================================================
# FILE: src/entities/player.py
# ============================================================================
import arcade
from src.systems.animation import AnimationController, AnimationState
from src.input.input_manager import InputAction
from typing import Optional, List

class Player(arcade.Sprite):
    """Player character with full movement and combat"""
    def __init__(self, character_data: dict, asset_manager, input_manager):
        super().__init__()
        
        # Character data
        self.character_data = character_data
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
        self.invulnerable = False
        self.invulnerable_time = 0
        
        # Animation
        self.animation_controller = AnimationController()
        self.setup_animations(asset_manager)
        
        # Input
        self.input_manager = input_manager
        
        # Collision
        self.points = [
            [-16, -32], [16, -32],  # Bottom
            [16, 32], [-16, 32]     # Top
        ]
        
    def setup_animations(self, asset_manager):
        """Setup character animations"""
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
        
        # Update animation state
        self.update_animation_state()
        self.animation_controller.update(delta_time)
        
        # Update texture
        texture = self.animation_controller.get_current_texture()
        if texture:
            self.texture = texture
            if not self.facing_right:
                self.texture = self.texture.texture.flipped_horizontally
                
        # Update combat
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time
            
        if self.invulnerable_time > 0:
            self.invulnerable_time -= delta_time
            if self.invulnerable_time <= 0:
                self.invulnerable = False
                
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
            
            if attack_type == 1:
                self.animation_controller.change_state(AnimationState.ATTACK_1, force=True)
            else:
                self.animation_controller.change_state(AnimationState.ATTACK_2, force=True)
                
            self.animation_controller.lock_state()
            
    def take_damage(self, damage: int):
        """Take damage"""
        if not self.invulnerable:
            self.health -= damage
            self.invulnerable = True
            self.invulnerable_time = 1.0
            
            if self.health <= 0:
                self.animation_controller.change_state(AnimationState.DEATH, force=True)
            else:
                self.animation_controller.change_state(AnimationState.HURT, force=True)
                
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