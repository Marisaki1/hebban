"""
Gravity system for different zones
"""

from enum import Enum
from src.core.constants import GRAVITY_NORMAL, GRAVITY_LOW, GRAVITY_REVERSE, GRAVITY_ZERO, GRAVITY_WATER

class GravityMode(Enum):
    """Different gravity modes"""
    NORMAL = "normal"
    LOW = "low"
    REVERSE = "reverse"
    ZERO = "zero"
    WATER = "water"

class GravityManager:
    """Manages gravity for different zones"""
    
    def __init__(self):
        self.gravity_values = {
            GravityMode.NORMAL: GRAVITY_NORMAL,
            GravityMode.LOW: GRAVITY_LOW,
            GravityMode.REVERSE: GRAVITY_REVERSE,
            GravityMode.ZERO: GRAVITY_ZERO,
            GravityMode.WATER: GRAVITY_WATER
        }
        
        self.current_mode = GravityMode.NORMAL
        self.zone_gravity = {}  # Map zones to gravity modes
        
    def set_mode(self, mode: GravityMode):
        """Set global gravity mode"""
        self.current_mode = mode
        
    def set_zone_gravity(self, zone_id: str, mode: GravityMode):
        """Set gravity for specific zone"""
        self.zone_gravity[zone_id] = mode
        
    def get_gravity(self, zone_id: str = None) -> tuple:
        """Get gravity vector for zone or global"""
        if zone_id and zone_id in self.zone_gravity:
            mode = self.zone_gravity[zone_id]
        else:
            mode = self.current_mode
            
        return self.gravity_values[mode]
        
    def apply_gravity(self, velocity: list, zone_id: str = None, delta_time: float = 1/60):
        """Apply gravity to velocity vector"""
        gx, gy = self.get_gravity(zone_id)
        
        velocity[0] += gx * delta_time * 60
        velocity[1] += gy * delta_time * 60
        
        # Apply drag for water physics
        if zone_id and self.zone_gravity.get(zone_id) == GravityMode.WATER:
            velocity[0] *= 0.95
            velocity[1] *= 0.95
            
        return velocity