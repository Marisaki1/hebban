# src/combat/ability_system.py
"""
Character ability system for special moves
"""

import arcade
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from src.core.sound_manager import sound_manager
from src.effects.particle_system import particle_manager

class AbilityType(Enum):
    """Types of abilities"""
    INSTANT = "instant"
    PROJECTILE = "projectile"
    BUFF = "buff"
    AREA = "area"
    MOVEMENT = "movement"

@dataclass
class AbilityData:
    """Data for a character ability"""
    name: str
    type: AbilityType
    cooldown: float
    cost: float = 0  # Energy/MP cost
    damage: float = 0
    duration: float = 0
    range: float = 0
    description: str = ""
    icon: Optional[str] = None
    sound: Optional[str] = None
    particle_effect: Optional[str] = None

class Ability:
    """Individual ability instance"""
    def __init__(self, data: AbilityData, execute_func: Callable):
        self.data = data
        self.execute = execute_func
        self.current_cooldown = 0.0
        self.is_active = False
        self.active_duration = 0.0
        
    def can_use(self) -> bool:
        """Check if ability can be used"""
        return self.current_cooldown <= 0 and not self.is_active
        
    def use(self, caster, target=None) -> bool:
        """Use the ability"""
        if not self.can_use():
            return False
            
        # Execute ability
        self.execute(caster, target)
        
        # Set cooldown
        self.current_cooldown = self.data.cooldown
        
        # Set active duration for duration-based abilities
        if self.data.duration > 0:
            self.is_active = True
            self.active_duration = self.data.duration
            
        # Play sound
        if self.data.sound:
            sound_manager.play_sfx(self.data.sound)
            
        # Create particle effect
        if self.data.particle_effect:
            particle_manager.create_effect(
                self.data.particle_effect,
                caster.center_x,
                caster.center_y
            )
            
        return True
        
    def update(self, delta_time: float):
        """Update ability cooldowns and duration"""
        if self.current_cooldown > 0:
            self.current_cooldown -= delta_time
            
        if self.is_active:
            self.active_duration -= delta_time
            if self.active_duration <= 0:
                self.is_active = False

class AbilityManager:
    """Manages character abilities"""
    
    def __init__(self):
        self.ability_definitions = self._load_ability_definitions()
        
    def _load_ability_definitions(self) -> Dict[str, AbilityData]:
        """Load all ability definitions"""
        abilities = {
            # Ruka abilities
            "double_jump": AbilityData(
                name="Double Jump",
                type=AbilityType.MOVEMENT,
                cooldown=0,
                description="Jump again in mid-air"
            ),
            "dash_attack": AbilityData(
                name="Dash Attack",
                type=AbilityType.INSTANT,
                cooldown=3.0,
                damage=20,
                range=100,
                description="Quick forward dash that damages enemies",
                sound="dash_attack",
                particle_effect="impact"
            ),
            "leadership_boost": AbilityData(
                name="Leadership Boost",
                type=AbilityType.BUFF,
                cooldown=10.0,
                duration=5.0,
                description="Boost nearby allies' attack power",
                sound="buff_activate",
                particle_effect="sparkle"
            ),
            
            # Yuki abilities
            "air_dash": AbilityData(
                name="Air Dash",
                type=AbilityType.MOVEMENT,
                cooldown=2.0,
                description="Dash horizontally in mid-air",
                sound="air_dash"
            ),
            "quick_strike": AbilityData(
                name="Quick Strike",
                type=AbilityType.INSTANT,
                cooldown=4.0,
                damage=30,
                description="Fast multi-hit combo attack",
                sound="quick_strike",
                particle_effect="impact"
            ),
            "enhanced_vision": AbilityData(
                name="Enhanced Vision",
                type=AbilityType.BUFF,
                cooldown=8.0,
                duration=10.0,
                description="Reveal hidden items and enemy weak points",
                sound="vision_activate",
                particle_effect="sparkle"
            ),
            
            # Tama abilities
            "shadow_strike": AbilityData(
                name="Shadow Strike",
                type=AbilityType.INSTANT,
                cooldown=5.0,
                damage=25,
                description="Teleport behind enemy and strike",
                sound="shadow_strike",
                particle_effect="impact"
            ),
            "decoy": AbilityData(
                name="Decoy",
                type=AbilityType.INSTANT,
                cooldown=8.0,
                duration=5.0,
                description="Create a decoy to distract enemies",
                sound="decoy_create"
            ),
            "smoke_bomb": AbilityData(
                name="Smoke Bomb",
                type=AbilityType.AREA,
                cooldown=6.0,
                range=150,
                duration=3.0,
                description="Create smoke cloud for concealment",
                sound="smoke_bomb",
                particle_effect="dust"
            ),
            
            # Add more abilities for other characters...
        }
        
        return abilities
        
    def create_ability(self, ability_name: str) -> Optional[Ability]:
        """Create an ability instance"""
        if ability_name not in self.ability_definitions:
            print(f"Warning: Unknown ability '{ability_name}'")
            return None
            
        data = self.ability_definitions[ability_name]
        
        # Create execution function based on ability type
        if ability_name == "dash_attack":
            execute_func = self._execute_dash_attack
        elif ability_name == "leadership_boost":
            execute_func = self._execute_leadership_boost
        elif ability_name == "air_dash":
            execute_func = self._execute_air_dash
        elif ability_name == "quick_strike":
            execute_func = self._execute_quick_strike
        elif ability_name == "shadow_strike":
            execute_func = self._execute_shadow_strike
        else:
            # Default execution
            execute_func = lambda caster, target: None
            
        return Ability(data, execute_func)
        
    def _execute_dash_attack(self, caster, target):
        """Execute dash attack ability"""
        # Move forward quickly
        dash_distance = 100
        direction = 1 if caster.facing_right else -1
        caster.center_x += dash_distance * direction
        
        # Damage enemies in path
        # This would check for enemies in the dash path
        
        # Create dash effect
        for i in range(5):
            x = caster.center_x - (i * 20 * direction)
            particle_manager.create_effect('impact', x, caster.center_y)
            
    def _execute_leadership_boost(self, caster, target):
        """Execute leadership boost ability"""
        # Apply buff to caster
        caster.attack_boost = 1.5  # 50% damage boost
        
        # Create aura effect
        emitter = particle_manager.create_effect('sparkle', caster.center_x, caster.center_y)
        emitter.emission_rate = 30
        emitter.particle_lifetime = 0.5
        emitter.spread_angle = 360
        
    def _execute_air_dash(self, caster, target):
        """Execute air dash ability"""
        # Dash horizontally in air
        dash_speed = 200
        direction = 1 if caster.facing_right else -1
        caster.velocity[0] = dash_speed * direction
        
        # Reset vertical velocity for horizontal dash
        if caster.velocity[1] < 0:
            caster.velocity[1] = 0
            
    def _execute_quick_strike(self, caster, target):
        """Execute quick strike ability"""
        # Perform multiple hits
        caster.attack_combo = 3
        caster.is_attacking = True
        
        # Create strike effects
        for i in range(3):
            arcade.schedule(
                lambda dt: particle_manager.create_effect(
                    'impact',
                    caster.center_x + (i * 10),
                    caster.center_y
                ),
                i * 0.1
            )
            
    def _execute_shadow_strike(self, caster, target):
        """Execute shadow strike ability"""
        if target:
            # Teleport behind target
            offset = 50
            caster.center_x = target.center_x - offset if target.facing_right else target.center_x + offset
            caster.center_y = target.center_y
            
            # Face target
            caster.facing_right = target.center_x > caster.center_x
            
            # Auto-attack
            caster.is_attacking = True
            
            # Create shadow effect
            particle_manager.create_effect('dust', caster.center_x, caster.center_y)

# Global ability manager
ability_manager = AbilityManager()