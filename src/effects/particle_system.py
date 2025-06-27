# src/effects/particle_system.py
"""
Particle system for visual effects
"""

import arcade
import random
import math
from typing import List, Dict, Optional, Tuple
from enum import Enum

class ParticleType(Enum):
    """Types of particle effects"""
    IMPACT = "impact"
    FLAME = "flame"
    SPARKLE = "sparkle"
    HEALING = "healing"
    DUST = "dust"
    EXPLOSION = "explosion"
    SMOKE = "smoke"
    ELECTRICITY = "electricity"

class Particle:
    """Individual particle"""
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 color: Tuple[int, int, int, int], size: float, lifetime: float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_lifetime = lifetime
        self.lifetime = lifetime
        self.gravity = 0
        self.fade_rate = 1.0
        
    def update(self, delta_time: float) -> bool:
        """Update particle, returns False if particle should be removed"""
        # Update position
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        
        # Apply gravity
        self.vy -= self.gravity * delta_time
        
        # Apply air resistance
        self.vx *= 0.99
        self.vy *= 0.99
        
        # Update lifetime
        self.lifetime -= delta_time
        
        # Fade out over time
        alpha_factor = self.lifetime / self.max_lifetime
        self.color = (*self.color[:3], int(self.color[3] * alpha_factor * self.fade_rate))
        
        return self.lifetime > 0
        
    def draw(self):
        """Draw the particle"""
        if self.color[3] > 0:  # Only draw if visible
            arcade.draw_circle_filled(self.x, self.y, self.size, self.color)

class ParticleEmitter:
    """Particle emitter that generates particles"""
    def __init__(self, x: float, y: float, particle_type: ParticleType):
        self.x = x
        self.y = y
        self.particle_type = particle_type
        self.particles: List[Particle] = []
        
        # Emitter properties
        self.emission_rate = 10  # particles per second
        self.emission_timer = 0
        self.active = True
        self.duration = 1.0  # How long the emitter stays active
        self.age = 0
        
        # Particle properties
        self.particle_lifetime = 1.0
        self.spread_angle = 90  # degrees
        self.speed_range = (50, 100)
        self.size_range = (2, 5)
        self.color_range = [(255, 255, 255, 255)]
        self.gravity = 50
        
        # Configure based on particle type
        self._configure_for_type()
        
    def _configure_for_type(self):
        """Configure emitter based on particle type"""
        if self.particle_type == ParticleType.IMPACT:
            self.emission_rate = 20
            self.duration = 0.2
            self.particle_lifetime = 0.5
            self.spread_angle = 180
            self.speed_range = (80, 150)
            self.size_range = (3, 8)
            self.color_range = [
                (255, 255, 100, 255),
                (255, 200, 50, 255),
                (200, 150, 100, 255)
            ]
            self.gravity = 200
            
        elif self.particle_type == ParticleType.FLAME:
            self.emission_rate = 15
            self.duration = 2.0
            self.particle_lifetime = 1.5
            self.spread_angle = 45
            self.speed_range = (30, 80)
            self.size_range = (4, 10)
            self.color_range = [
                (255, 100, 0, 255),
                (255, 150, 0, 255),
                (255, 200, 50, 255),
                (200, 50, 0, 255)
            ]
            self.gravity = -50  # Flames rise
            
        elif self.particle_type == ParticleType.SPARKLE:
            self.emission_rate = 25
            self.duration = 1.0
            self.particle_lifetime = 2.0
            self.spread_angle = 360
            self.speed_range = (20, 60)
            self.size_range = (1, 4)
            self.color_range = [
                (255, 255, 100, 255),
                (100, 255, 255, 255),
                (255, 100, 255, 255),
                (255, 255, 255, 255)
            ]
            self.gravity = 30
            
        elif self.particle_type == ParticleType.HEALING:
            self.emission_rate = 12
            self.duration = 1.5
            self.particle_lifetime = 2.5
            self.spread_angle = 30
            self.speed_range = (20, 50)
            self.size_range = (3, 7)
            self.color_range = [
                (100, 255, 100, 255),
                (150, 255, 150, 255),
                (200, 255, 200, 255)
            ]
            self.gravity = -80  # Healing particles float up
            
        elif self.particle_type == ParticleType.DUST:
            self.emission_rate = 8
            self.duration = 0.5
            self.particle_lifetime = 3.0
            self.spread_angle = 180
            self.speed_range = (10, 40)
            self.size_range = (2, 6)
            self.color_range = [
                (150, 120, 80, 200),
                (120, 100, 70, 200),
                (100, 80, 60, 200)
            ]
            self.gravity = 20
            
        elif self.particle_type == ParticleType.EXPLOSION:
            self.emission_rate = 50
            self.duration = 0.3
            self.particle_lifetime = 1.0
            self.spread_angle = 360
            self.speed_range = (100, 200)
            self.size_range = (5, 12)
            self.color_range = [
                (255, 150, 0, 255),
                (255, 100, 0, 255),
                (200, 80, 0, 255),
                (255, 200, 100, 255)
            ]
            self.gravity = 150
            
    def update(self, delta_time: float):
        """Update emitter and all particles"""
        self.age += delta_time
        
        # Generate new particles if still active
        if self.active and self.age < self.duration:
            self.emission_timer += delta_time
            particles_to_emit = int(self.emission_timer * self.emission_rate)
            self.emission_timer -= particles_to_emit / self.emission_rate
            
            for _ in range(particles_to_emit):
                self._emit_particle()
        else:
            self.active = False
            
        # Update existing particles
        self.particles = [p for p in self.particles if p.update(delta_time)]
        
    def _emit_particle(self):
        """Emit a single particle"""
        # Random angle within spread
        angle = random.uniform(-self.spread_angle/2, self.spread_angle/2)
        angle_rad = math.radians(angle)
        
        # Random speed
        speed = random.uniform(*self.speed_range)
        vx = math.cos(angle_rad) * speed
        vy = math.sin(angle_rad) * speed
        
        # Random size
        size = random.uniform(*self.size_range)
        
        # Random color from range
        color = random.choice(self.color_range)
        
        # Random lifetime variation
        lifetime = self.particle_lifetime * random.uniform(0.8, 1.2)
        
        # Small random offset from emitter position
        x = self.x + random.uniform(-5, 5)
        y = self.y + random.uniform(-5, 5)
        
        # Create particle
        particle = Particle(x, y, vx, vy, color, size, lifetime)
        particle.gravity = self.gravity
        
        self.particles.append(particle)
        
    def draw(self):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw()
            
    def is_finished(self) -> bool:
        """Check if emitter is finished and has no particles left"""
        return not self.active and len(self.particles) == 0

class ParticleManager:
    """Manages all particle emitters"""
    def __init__(self):
        self.emitters: List[ParticleEmitter] = []
        
    def create_effect(self, effect_type: str, x: float, y: float) -> Optional[ParticleEmitter]:
        """Create a particle effect at the given position"""
        try:
            particle_type = ParticleType(effect_type)
        except ValueError:
            print(f"Unknown particle effect type: {effect_type}")
            return None
            
        emitter = ParticleEmitter(x, y, particle_type)
        self.emitters.append(emitter)
        return emitter
        
    def create_burst(self, effect_type: str, x: float, y: float, count: int = 1):
        """Create multiple bursts of the same effect"""
        for _ in range(count):
            offset_x = random.uniform(-10, 10)
            offset_y = random.uniform(-10, 10)
            self.create_effect(effect_type, x + offset_x, y + offset_y)
            
    def update(self, delta_time: float):
        """Update all emitters"""
        # Update all emitters
        for emitter in self.emitters:
            emitter.update(delta_time)
            
        # Remove finished emitters
        self.emitters = [e for e in self.emitters if not e.is_finished()]
        
    def draw(self):
        """Draw all particle effects"""
        for emitter in self.emitters:
            emitter.draw()
            
    def clear(self):
        """Clear all particle effects"""
        self.emitters.clear()
        
    def get_particle_count(self) -> int:
        """Get total number of active particles"""
        return sum(len(emitter.particles) for emitter in self.emitters)

# Global particle manager instance
particle_manager = ParticleManager()