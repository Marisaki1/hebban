# src/effects/transitions.py
"""
Screen transition effects for smooth scene changes
"""

import arcade
from typing import Callable, Optional
from enum import Enum

class TransitionType(Enum):
    """Types of screen transitions"""
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    IRIS_IN = "iris_in"
    IRIS_OUT = "iris_out"
    DISSOLVE = "dissolve"

class TransitionManager:
    """Manages screen transitions between scenes"""
    
    def __init__(self, window_width: int, window_height: int):
        self.width = window_width
        self.height = window_height
        self.transition_active = False
        self.transition_progress = 0.0
        self.transition_duration = 0.5
        self.transition_type = TransitionType.FADE
        self.transition_callback: Optional[Callable] = None
        self.is_entering = True
        
        # Transition overlay color
        self.overlay_color = (0, 0, 0)
        
    def start_transition(self, transition_type: TransitionType, 
                        duration: float = 0.5,
                        callback: Optional[Callable] = None,
                        is_entering: bool = True):
        """Start a transition effect"""
        self.transition_active = True
        self.transition_progress = 0.0
        self.transition_duration = duration
        self.transition_type = transition_type
        self.transition_callback = callback
        self.is_entering = is_entering
        
    def update(self, delta_time: float):
        """Update transition progress"""
        if not self.transition_active:
            return
            
        self.transition_progress += delta_time / self.transition_duration
        
        if self.transition_progress >= 1.0:
            self.transition_progress = 1.0
            self.transition_active = False
            
            # Call callback at midpoint for scene change
            if self.transition_callback and not self.is_entering:
                self.transition_callback()
                
    def draw(self):
        """Draw transition effect"""
        if not self.transition_active and self.transition_progress <= 0:
            return
            
        # Calculate alpha based on transition direction
        if self.is_entering:
            alpha = int(255 * (1.0 - self.transition_progress))
        else:
            alpha = int(255 * self.transition_progress)
            
        if self.transition_type == TransitionType.FADE:
            self._draw_fade(alpha)
        elif self.transition_type == TransitionType.SLIDE_LEFT:
            self._draw_slide_horizontal(-1, alpha)
        elif self.transition_type == TransitionType.SLIDE_RIGHT:
            self._draw_slide_horizontal(1, alpha)
        elif self.transition_type == TransitionType.SLIDE_UP:
            self._draw_slide_vertical(1, alpha)
        elif self.transition_type == TransitionType.SLIDE_DOWN:
            self._draw_slide_vertical(-1, alpha)
        elif self.transition_type == TransitionType.IRIS_IN:
            self._draw_iris(True)
        elif self.transition_type == TransitionType.IRIS_OUT:
            self._draw_iris(False)
        elif self.transition_type == TransitionType.DISSOLVE:
            self._draw_dissolve(alpha)
            
    def _draw_fade(self, alpha: int):
        """Draw fade transition"""
        arcade.draw_rectangle_filled(
            self.width // 2, self.height // 2,
            self.width, self.height,
            (*self.overlay_color, alpha)
        )
        
    def _draw_slide_horizontal(self, direction: int, alpha: int):
        """Draw horizontal slide transition"""
        if self.is_entering:
            offset = self.width * (1.0 - self.transition_progress) * direction
        else:
            offset = self.width * self.transition_progress * direction * -1
            
        arcade.draw_rectangle_filled(
            self.width // 2 + offset, self.height // 2,
            self.width, self.height,
            (*self.overlay_color, alpha)
        )
        
    def _draw_slide_vertical(self, direction: int, alpha: int):
        """Draw vertical slide transition"""
        if self.is_entering:
            offset = self.height * (1.0 - self.transition_progress) * direction
        else:
            offset = self.height * self.transition_progress * direction * -1
            
        arcade.draw_rectangle_filled(
            self.width // 2, self.height // 2 + offset,
            self.width, self.height,
            (*self.overlay_color, alpha)
        )
        
    def _draw_iris(self, iris_in: bool):
        """Draw iris transition (circle wipe)"""
        if iris_in:
            radius = max(self.width, self.height) * self.transition_progress
        else:
            radius = max(self.width, self.height) * (1.0 - self.transition_progress)
            
        # Draw black rectangles around circle
        if radius < max(self.width, self.height):
            # This is a simplified version - in a real implementation,
            # you'd use a shader or stencil buffer for a perfect circle
            steps = 32
            for i in range(steps):
                angle = (i / steps) * 2 * 3.14159
                next_angle = ((i + 1) / steps) * 2 * 3.14159
                
                # Draw triangular segments
                arcade.draw_triangle_filled(
                    self.width // 2, self.height // 2,
                    self.width // 2 + radius * math.cos(angle),
                    self.height // 2 + radius * math.sin(angle),
                    self.width // 2 + radius * math.cos(next_angle),
                    self.height // 2 + radius * math.sin(next_angle),
                    (*self.overlay_color, 255)
                )
                
    def _draw_dissolve(self, alpha: int):
        """Draw dissolve transition with dithering effect"""
        # Create a dither pattern
        for x in range(0, self.width, 4):
            for y in range(0, self.height, 4):
                if (x + y) % 8 == 0:
                    arcade.draw_rectangle_filled(
                        x + 2, y + 2, 4, 4,
                        (*self.overlay_color, alpha)
                    )
                    
    def fade_out(self, callback: Callable, duration: float = 0.5):
        """Convenience method for fade out"""
        self.start_transition(TransitionType.FADE, duration, callback, False)
        
    def fade_in(self, duration: float = 0.5):
        """Convenience method for fade in"""
        self.start_transition(TransitionType.FADE, duration, None, True)
        
    def slide_transition(self, direction: str, callback: Callable, duration: float = 0.5):
        """Convenience method for slide transitions"""
        transition_map = {
            'left': TransitionType.SLIDE_LEFT,
            'right': TransitionType.SLIDE_RIGHT,
            'up': TransitionType.SLIDE_UP,
            'down': TransitionType.SLIDE_DOWN
        }
        
        if direction in transition_map:
            self.start_transition(transition_map[direction], duration, callback, False)

# Global transition manager (initialized in main game)
transition_manager = None