# src/entities/items.py
"""
Item and powerup system for collectibles
"""

import math
import arcade
import random
from typing import List, Optional, Callable
from enum import Enum
from src.core.sound_manager import sound_manager
from src.effects.particle_system import particle_manager

class ItemType(Enum):
    """Types of items"""
    HEALTH = "health"
    ENERGY = "energy"
    POWERUP = "powerup"
    COIN = "coin"
    KEY = "key"
    WEAPON = "weapon"
    SPECIAL = "special"

class ItemRarity(Enum):
    """Item rarity levels"""
    COMMON = ("common", arcade.color.WHITE)
    RARE = ("rare", arcade.color.BLUE)
    EPIC = ("epic", arcade.color.PURPLE)
    LEGENDARY = ("legendary", arcade.color.GOLD)

class Item(arcade.Sprite):
    """Base class for all items"""
    def __init__(self, item_type: ItemType, x: float, y: float):
        super().__init__()
        
        self.item_type = item_type
        self.rarity = ItemRarity.COMMON
        self.value = 0
        self.duration = 0
        self.collected = False
        
        # Visual properties
        self.bob_speed = 2.0
        self.bob_height = 5
        self.bob_timer = random.uniform(0, 6.28)  # Random start phase
        self.glow_timer = 0
        self.base_y = y
        
        # Set position
        self.center_x = x
        self.center_y = y
        
        # Particle emitter for glow effect
        self.glow_emitter = None
        
    def update(self, delta_time: float):
        """Update item animation"""
        if self.collected:
            return
            
        # Bobbing animation
        self.bob_timer += delta_time * self.bob_speed
        self.center_y = self.base_y + math.sin(self.bob_timer) * self.bob_height
        
        # Rotation for visual interest
        self.angle += delta_time * 30  # Slow rotation
        
        # Update glow
        self.glow_timer += delta_time
        
    def collect(self, player):
        """Called when item is collected"""
        if self.collected:
            return
            
        self.collected = True
        self.apply_effect(player)
        
        # Play collection sound
        sound_manager.play_sfx(f"collect_{self.item_type.value}")
        
        # Create collection effect
        particle_manager.create_effect('sparkle', self.center_x, self.center_y)
        
        # Remove from sprite lists
        self.remove_from_sprite_lists()
        
    def apply_effect(self, player):
        """Apply item effect to player - override in subclasses"""
        pass
        
    def draw(self):
        """Draw item with glow effect"""
        # Draw glow based on rarity
        if self.rarity != ItemRarity.COMMON:
            glow_color = list(self.rarity.value[1])
            glow_alpha = int(128 + 64 * math.sin(self.glow_timer * 3))
            glow_color.append(glow_alpha)
            
            arcade.draw_circle_filled(
                self.center_x, self.center_y,
                self.width * 0.8,
                glow_color
            )
            
        # Draw the item sprite
        super().draw()

class HealthItem(Item):
    """Health restoration item"""
    def __init__(self, x: float, y: float, heal_amount: int = 20):
        super().__init__(ItemType.HEALTH, x, y)
        self.heal_amount = heal_amount
        
        # Create texture
        self.texture = arcade.make_soft_circle_texture(
            32, arcade.color.RED, outer_alpha=255
        )
        
        # Set rarity based on heal amount
        if heal_amount >= 50:
            self.rarity = ItemRarity.RARE
        elif heal_amount >= 100:
            self.rarity = ItemRarity.EPIC
            
    def apply_effect(self, player):
        """Heal the player"""
        old_health = player.health
        player.health = min(player.health + self.heal_amount, player.max_health)
        actual_heal = player.health - old_health
        
        # Create healing effect
        particle_manager.create_effect('healing', player.center_x, player.center_y)
        
        # Show heal amount
        if hasattr(player, 'hud'):
            player.hud.add_score(0)  # Trigger score popup
            player.hud.score_popup_value = f"+{actual_heal} HP"

class CoinItem(Item):
    """Collectible coin for score"""
    def __init__(self, x: float, y: float, value: int = 10):
        super().__init__(ItemType.COIN, x, y)
        self.value = value
        
        # Create texture based on value
        if value >= 50:
            color = arcade.color.GOLD
            self.rarity = ItemRarity.RARE
            size = 24
        elif value >= 100:
            color = arcade.color.PLATINUM
            self.rarity = ItemRarity.EPIC
            size = 28
        else:
            color = arcade.color.BRONZE
            size = 20
            
        self.texture = arcade.make_soft_circle_texture(
            size, color, outer_alpha=255
        )
        
    def apply_effect(self, player):
        """Add to player's score"""
        if hasattr(player, 'score'):
            player.score += self.value
        if hasattr(player, 'hud'):
            player.hud.add_score(self.value)

class PowerupItem(Item):
    """Temporary power boost item"""
    def __init__(self, x: float, y: float, powerup_type: str = "speed"):
        super().__init__(ItemType.POWERUP, x, y)
        self.powerup_type = powerup_type
        self.duration = 10.0  # 10 seconds
        
        # Set properties based on type
        powerup_configs = {
            "speed": {
                "color": arcade.color.YELLOW,
                "boost": 1.5,
                "rarity": ItemRarity.COMMON
            },
            "damage": {
                "color": arcade.color.RED,
                "boost": 2.0,
                "rarity": ItemRarity.RARE
            },
            "defense": {
                "color": arcade.color.BLUE,
                "boost": 0.5,
                "rarity": ItemRarity.RARE
            },
            "invincibility": {
                "color": arcade.color.PURPLE,
                "duration": 5.0,
                "rarity": ItemRarity.LEGENDARY
            }
        }
        
        config = powerup_configs.get(powerup_type, powerup_configs["speed"])
        self.boost_amount = config.get("boost", 1.0)
        self.rarity = config.get("rarity", ItemRarity.COMMON)
        self.duration = config.get("duration", self.duration)
        
        # Create star-shaped texture
        self.texture = arcade.make_soft_square_texture(
            32, config["color"], outer_alpha=255
        )
        
    def apply_effect(self, player):
        """Apply powerup effect"""
        if self.powerup_type == "speed":
            player.move_speed *= self.boost_amount
        elif self.powerup_type == "damage":
            if hasattr(player, 'attack_boost'):
                player.attack_boost = self.boost_amount
        elif self.powerup_type == "defense":
            if hasattr(player, 'defense_boost'):
                player.defense_boost = self.boost_amount
        elif self.powerup_type == "invincibility":
            player.invulnerable = True
            player.invulnerable_time = self.duration
            
        # Add visual effect to player
        if hasattr(player, 'active_powerups'):
            player.active_powerups.append({
                'type': self.powerup_type,
                'duration': self.duration,
                'boost': self.boost_amount
            })

class ItemSpawner:
    """Manages item spawning in levels"""
    def __init__(self):
        self.spawn_chance = 0.3  # 30% chance to spawn item on enemy death
        self.item_weights = {
            ItemType.HEALTH: 40,
            ItemType.COIN: 40,
            ItemType.POWERUP: 20
        }
        
    def spawn_from_enemy(self, enemy_x: float, enemy_y: float, enemy_type: str) -> Optional[Item]:
        """Spawn item from defeated enemy"""
        if random.random() > self.spawn_chance:
            return None
            
        # Choose item type based on weights
        total_weight = sum(self.item_weights.values())
        choice = random.uniform(0, total_weight)
        
        current_weight = 0
        chosen_type = ItemType.HEALTH
        
        for item_type, weight in self.item_weights.items():
            current_weight += weight
            if choice <= current_weight:
                chosen_type = item_type
                break
                
        # Create item
        if chosen_type == ItemType.HEALTH:
            heal_amount = random.choice([20, 30, 50])
            return HealthItem(enemy_x, enemy_y, heal_amount)
        elif chosen_type == ItemType.COIN:
            value = random.choice([10, 20, 50, 100])
            return CoinItem(enemy_x, enemy_y, value)
        elif chosen_type == ItemType.POWERUP:
            powerup_type = random.choice(["speed", "damage", "defense"])
            if enemy_type == "boss":
                powerup_type = "invincibility"
            return PowerupItem(enemy_x, enemy_y, powerup_type)
            
        return None
        
    def create_level_items(self, platforms: arcade.SpriteList) -> List[Item]:
        """Create items placed in the level"""
        items = []
        
        # Place items on some platforms
        for platform in platforms[::3]:  # Every third platform
            if random.random() < 0.5:
                item_type = random.choice([ItemType.COIN, ItemType.HEALTH])
                
                if item_type == ItemType.COIN:
                    item = CoinItem(
                        platform.center_x + random.randint(-50, 50),
                        platform.top + 30
                    )
                else:
                    item = HealthItem(
                        platform.center_x,
                        platform.top + 30
                    )
                    
                items.append(item)
                
        return items

# Global item spawner
item_spawner = ItemSpawner()