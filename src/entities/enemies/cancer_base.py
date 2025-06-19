# ============================================================================
# FILE: src/entities/enemies/cancer_base.py
# ============================================================================
from typing import List

import arcade

from src.entities.player import Player


class CancerEnemy(arcade.Sprite):
    """Base class for Cancer enemies"""
    def __init__(self, enemy_type: str, size: str = "small"):
        super().__init__()
        
        # Enemy properties
        self.enemy_type = enemy_type
        self.size = size
        self.sizes = {
            "small": {"scale": 1.0, "health": 20, "damage": 10},
            "medium": {"scale": 2.0, "health": 50, "damage": 20},
            "large": {"scale": 3.0, "health": 100, "damage": 30},
            "boss": {"scale": 5.0, "health": 500, "damage": 50}
        }
        
        # Apply size properties
        size_data = self.sizes[size]
        self.scale = size_data["scale"]
        self.max_health = size_data["health"]
        self.health = self.max_health
        self.damage = size_data["damage"]
        
        # Movement
        self.velocity = [0, 0]
        self.move_speed = 2.0 / self.scale  # Larger enemies move slower
        
        # AI state
        self.ai_state = "patrol"
        self.target_player = None
        self.patrol_start = 0
        self.patrol_range = 200
        
        # Combat
        self.attack_range = 50 * self.scale
        self.attack_cooldown = 0
        
    def update(self, delta_time: float, players: List[Player], gravity_manager):
        """Update enemy AI and physics"""
        # Find nearest player
        self.find_target(players)
        
        # AI behavior
        if self.ai_state == "patrol":
            self.patrol_behavior(delta_time)
        elif self.ai_state == "chase":
            self.chase_behavior(delta_time)
        elif self.ai_state == "attack":
            self.attack_behavior(delta_time)
            
        # Apply gravity
        gravity_manager.apply_gravity(self.velocity, None, delta_time)
        
        # Apply movement
        self.center_x += self.velocity[0] * delta_time * 60
        self.center_y += self.velocity[1] * delta_time * 60
        
        # Simple ground collision
        if self.center_y <= 100:
            self.center_y = 100
            self.velocity[1] = 0
            
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time
            
    def find_target(self, players: List[Player]):
        """Find nearest player to target"""
        if not players:
            self.target_player = None
            return
            
        nearest_distance = float('inf')
        nearest_player = None
        
        for player in players:
            distance = abs(self.center_x - player.center_x) + abs(self.center_y - player.center_y)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_player = player
                
        self.target_player = nearest_player
        
        # Update AI state based on distance
        if nearest_distance < self.attack_range:
            self.ai_state = "attack"
        elif nearest_distance < 300:
            self.ai_state = "chase"
        else:
            self.ai_state = "patrol"
            
    def patrol_behavior(self, delta_time: float):
        """Patrol back and forth"""
        if self.patrol_start == 0:
            self.patrol_start = self.center_x
            
        # Simple back and forth movement
        if abs(self.center_x - self.patrol_start) > self.patrol_range:
            self.velocity[0] = -self.velocity[0]
        elif self.velocity[0] == 0:
            self.velocity[0] = self.move_speed
            
    def chase_behavior(self, delta_time: float):
        """Chase target player"""
        if not self.target_player:
            return
            
        # Move towards player
        direction = 1 if self.target_player.center_x > self.center_x else -1
        self.velocity[0] = direction * self.move_speed * 1.5
        
    def attack_behavior(self, delta_time: float):
        """Attack nearby player"""
        if not self.target_player or self.attack_cooldown > 0:
            return
            
        # Stop and attack
        self.velocity[0] = 0
        
        # Deal damage to player
        distance = abs(self.center_x - self.target_player.center_x)
        if distance < self.attack_range:
            self.target_player.take_damage(self.damage)
            self.attack_cooldown = 2.0
            
    def take_damage(self, damage: int):
        """Take damage from player"""
        self.health -= damage
        if self.health <= 0:
            self.remove_from_sprite_lists()