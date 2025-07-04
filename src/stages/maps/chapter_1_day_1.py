# src/stages/maps/chapter_1_day_1.py
"""
Chapter 1 Day 1 - City Under Siege stage implementation
"""

import arcade
from src.stages.stage_loader import StageBase
from src.entities.enemy import CancerEnemy

class Chapter1Day1Stage(StageBase):
    """Chapter 1 Day 1 - City Under Siege"""
    
    def __init__(self):
        super().__init__()
        self.stage_id = "chapter_1_day_1"
        
    def setup(self, stage_data: dict):
        """Setup the stage"""
        super().setup(stage_data)
        
        # Create city environment
        self.create_city_platforms()
        
        # Add destructible objects
        self.create_destructibles()
        
        # Set background
        self.background_color = (50, 50, 70)  # Dusky city color
        
    def create_city_platforms(self):
        """Create city platform layout"""
        # Ground level
        for x in range(0, 2400, 200):
            platform = arcade.SpriteSolidColor(200, 20, arcade.color.DARK_GRAY)
            platform.center_x = x + 100
            platform.center_y = 50
            self.platforms.append(platform)
            
        # Building platforms
        building_configs = [
            # (x, y, width, height)
            (300, 150, 200, 20),
            (600, 250, 150, 20),
            (900, 200, 200, 20),
            (1200, 300, 180, 20),
            (1500, 150, 200, 20),
            (1800, 350, 150, 20),
            (2100, 250, 200, 20),
            
            # Vertical walls
            (500, 100, 20, 100),
            (1100, 150, 20, 100),
            (1700, 200, 20, 150),
        ]
        
        for x, y, w, h in building_configs:
            platform = arcade.SpriteSolidColor(w, h, arcade.color.DARK_GRAY)
            platform.center_x = x
            platform.center_y = y
            self.platforms.append(platform)
            
    def create_destructibles(self):
        """Create destructible objects in the city"""
        # Cars, crates, etc.
        destructible_positions = [
            (400, 80),
            (800, 80),
            (1300, 80),
            (1900, 80),
        ]
        
        for x, y in destructible_positions:
            # Simple destructible sprite (placeholder)
            crate = arcade.SpriteSolidColor(40, 40, arcade.color.BROWN)
            crate.center_x = x
            crate.center_y = y
            crate.health = 20
            self.destructibles.append(crate)
            
    def spawn_wave(self, wave_data: dict):
        """Spawn a wave of enemies"""
        for enemy_group in wave_data.get('enemies', []):
            enemy_type = enemy_group['type']
            position = enemy_group['position']
            count = enemy_group.get('count', 1)
            
            for i in range(count):
                enemy = CancerEnemy(
                    enemy_type=enemy_type.replace('cancer_', ''),
                    size=enemy_type.split('_')[1] if '_' in enemy_type else 'small'
                )
                enemy.center_x = position[0] + i * 50
                enemy.center_y = position[1]
                self.enemies.append(enemy)
                
    def update(self, delta_time: float):
        """Update stage-specific logic"""
        super().update(delta_time)
        
        # Check for destructible damage
        for destructible in self.destructibles:
            if hasattr(destructible, 'health') and destructible.health <= 0:
                # Create destruction effect
                self.create_destruction_effect(destructible.center_x, destructible.center_y)
                destructible.remove_from_sprite_lists()
                
    def create_destruction_effect(self, x: float, y: float):
        """Create destruction particle effect"""
        # This would create particle effects
        # For now, just a placeholder
        pass