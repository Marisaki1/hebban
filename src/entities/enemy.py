"""
Enemy system for Cancer enemies
"""

import arcade
import random
from typing import List, Optional

class CancerEnemy(arcade.Sprite):
    """Cancer enemy with AI and different sizes"""
    
    def __init__(self, enemy_type: str = "basic", size: str = "small"):
        super().__init__()
        
        # Enemy properties
        self.enemy_type = enemy_type
        self.size = size
        
        # Size-based stats
        size_stats = {
            "small": {"scale": 1.0, "health": 20, "damage": 10, "speed": 2.0},
            "medium": {"scale": 1.5, "health": 50, "damage": 20, "speed": 1.5},
            "large": {"scale": 2.0, "health": 100, "damage": 30, "speed": 1.0},
            "boss": {"scale": 3.0, "health": 500, "damage": 50, "speed": 0.5}
        }
        
        stats = size_stats.get(size, size_stats["small"])
        self.scale = stats["scale"]
        self.max_health = stats["health"]
        self.health = self.max_health
        self.damage = stats["damage"]
        self.move_speed = stats["speed"]
        
        # Load texture
        self._load_texture()
        
        # Physics
        self.velocity = [0, 0]
        self.on_ground = False
        
        # AI state
        self.ai_state = "patrol"
        self.target_player = None
        self.patrol_start = 0
        self.patrol_range = 200
        self.patrol_direction = 1
        
        # Combat
        self.attack_range = 50 * self.scale
        self.attack_cooldown = 0
        self.detection_range = 300
        
        # Loot
        self.score_value = int(10 * self.scale)
        
    def _load_texture(self):
        """Load enemy texture"""
        try:
            # Try to get texture from asset manager
            game = arcade.get_window()
            if hasattr(game, 'asset_manager'):
                texture = game.asset_manager.get_texture(f"enemy_{self.size}")
                if texture:
                    self.texture = texture
                    return
        except:
            pass
            
        print(f"No texture found for enemy size {self.size}")
        
    def update(self, delta_time: float, players: List, gravity_manager):
        """Update enemy AI and physics"""
        # Find target player
        self.find_target(players)
        
        # AI behavior
        if self.ai_state == "patrol":
            self.patrol_behavior(delta_time)
        elif self.ai_state == "chase":
            self.chase_behavior(delta_time)
        elif self.ai_state == "attack":
            self.attack_behavior(delta_time)
            
        # Apply gravity
        if gravity_manager:
            gravity_manager.apply_gravity(self.velocity, None, delta_time)
        else:
            # Fallback gravity
            self.velocity[1] -= 0.5 * delta_time * 60
            
        # Apply movement
        self.center_x += self.velocity[0] * delta_time * 60
        self.center_y += self.velocity[1] * delta_time * 60
        
        # Simple ground collision
        if self.center_y <= 100:
            self.center_y = 100
            self.velocity[1] = 0
            self.on_ground = True
        else:
            self.on_ground = False
            
        # Update timers
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time
            
    def find_target(self, players: List):
        """Find nearest player to target"""
        if not players:
            self.target_player = None
            return
            
        nearest_distance = float('inf')
        nearest_player = None
        
        for player in players:
            if hasattr(player, 'center_x') and hasattr(player, 'center_y'):
                distance = abs(self.center_x - player.center_x) + abs(self.center_y - player.center_y)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_player = player
                    
        self.target_player = nearest_player
        
        # Update AI state based on distance
        if nearest_distance < self.attack_range:
            self.ai_state = "attack"
        elif nearest_distance < self.detection_range:
            self.ai_state = "chase"
        else:
            self.ai_state = "patrol"
            
    def patrol_behavior(self, delta_time: float):
        """Simple patrol behavior"""
        if self.patrol_start == 0:
            self.patrol_start = self.center_x
            
        # Move back and forth
        distance_from_start = self.center_x - self.patrol_start
        
        if abs(distance_from_start) > self.patrol_range:
            self.patrol_direction *= -1
            
        self.velocity[0] = self.patrol_direction * self.move_speed
        
    def chase_behavior(self, delta_time: float):
        """Chase target player"""
        if not self.target_player:
            return
            
        # Move towards player
        if self.target_player.center_x > self.center_x:
            self.velocity[0] = self.move_speed * 1.5
        else:
            self.velocity[0] = -self.move_speed * 1.5
            
        # Jump if player is above
        if (self.target_player.center_y > self.center_y + 50 and 
            self.on_ground and 
            abs(self.target_player.center_x - self.center_x) < 100):
            self.velocity[1] = 10
            
    def attack_behavior(self, delta_time: float):
        """Attack nearby player"""
        if not self.target_player or self.attack_cooldown > 0:
            return
            
        # Stop moving to attack
        self.velocity[0] = 0
        
        # Check if player is in range
        distance = abs(self.center_x - self.target_player.center_x)
        if distance < self.attack_range:
            # Deal damage to player
            if hasattr(self.target_player, 'take_damage'):
                self.target_player.take_damage(self.damage)
                
            self.attack_cooldown = 2.0
            
            # Create attack effect
            try:
                game = arcade.get_window()
                if hasattr(game, 'particle_manager'):
                    game.particle_manager.create_effect('impact', self.center_x, self.center_y)
                if hasattr(game, 'sound_manager'):
                    game.sound_manager.play_sfx("enemy_hit")
            except:
                pass
                
    def take_damage(self, damage: int):
        """Take damage from player"""
        self.health -= damage
        
        # Create hit effect
        try:
            game = arcade.get_window()
            if hasattr(game, 'particle_manager'):
                game.particle_manager.create_effect('impact', self.center_x, self.center_y)
        except:
            pass
            
        if self.health <= 0:
            self.die()
            
    def die(self):
        """Handle enemy death"""
        # Create death effect
        try:
            game = arcade.get_window()
            if hasattr(game, 'particle_manager'):
                game.particle_manager.create_effect('explosion', self.center_x, self.center_y)
            if hasattr(game, 'sound_manager'):
                game.sound_manager.play_sfx("enemy_death")
        except:
            pass
            
        # Spawn loot (placeholder)
        self.spawn_loot()
        
        # Remove from sprite lists
        self.remove_from_sprite_lists()
        
    def spawn_loot(self):
        """Spawn loot items (placeholder)"""
        # Random chance to spawn health or coins
        loot_chance = random.random()
        
        if loot_chance < 0.3:  # 30% chance for health
            self.create_health_item()
        elif loot_chance < 0.6:  # 30% chance for coins
            self.create_coin_item()
        # 40% chance for no loot
        
    def create_health_item(self):
        """Create health pickup item (placeholder)"""
        # This would create a health item sprite
        # For now, just add score to player
        if self.target_player and hasattr(self.target_player, 'heal'):
            heal_amount = random.randint(10, 20)
            self.target_player.heal(heal_amount)
            
    def create_coin_item(self):
        """Create coin pickup item (placeholder)"""
        # This would create a coin item sprite
        # For now, just add score to player
        if self.target_player and hasattr(self.target_player, 'add_score'):
            coin_value = random.randint(5, 15) * int(self.scale)
            self.target_player.add_score(coin_value)

class EnemySpawner:
    """Manages enemy spawning in levels"""
    
    def __init__(self):
        self.spawn_points = []
        self.spawn_timer = 0
        self.spawn_interval = 5.0  # Spawn every 5 seconds
        self.max_enemies = 10
        
    def add_spawn_point(self, x: float, y: float, enemy_type: str = "basic", size: str = "small"):
        """Add a spawn point"""
        self.spawn_points.append({
            'x': x,
            'y': y,
            'type': enemy_type,
            'size': size
        })
        
    def update(self, delta_time: float, enemy_list: arcade.SpriteList):
        """Update spawner"""
        if len(enemy_list) >= self.max_enemies:
            return
            
        self.spawn_timer += delta_time
        
        if self.spawn_timer >= self.spawn_interval and self.spawn_points:
            self.spawn_timer = 0
            
            # Choose random spawn point
            spawn_point = random.choice(self.spawn_points)
            
            # Create enemy
            enemy = CancerEnemy(spawn_point['type'], spawn_point['size'])
            enemy.center_x = spawn_point['x']
            enemy.center_y = spawn_point['y']
            
            enemy_list.append(enemy)
            
    def spawn_wave(self, enemy_list: arcade.SpriteList, wave_config: list):
        """Spawn a specific wave of enemies"""
        for config in wave_config:
            enemy = CancerEnemy(
                config.get('type', 'basic'),
                config.get('size', 'small')
            )
            enemy.center_x = config.get('x', 500)
            enemy.center_y = config.get('y', 200)
            enemy_list.append(enemy)