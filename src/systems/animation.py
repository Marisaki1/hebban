# ============================================================================
# FILE: src/systems/animation.py
# ============================================================================
from enum import Enum
from typing import Dict, List

class AnimationState(Enum):
    """Character animation states"""
    IDLE = "idle"
    WALK = "walk"
    RUN = "run"
    JUMP = "jump"
    FALL = "fall"
    ATTACK_1 = "attack_1"
    ATTACK_2 = "attack_2"
    HURT = "hurt"
    DEATH = "death"

class Animation:
    """Single animation sequence"""
    def __init__(self, frames: List[arcade.Texture], frame_duration: float = 0.1, loop: bool = True):
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame = 0
        self.elapsed_time = 0
        self.finished = False
        
    def update(self, delta_time: float):
        """Update animation frame"""
        if self.finished and not self.loop:
            return
            
        self.elapsed_time += delta_time
        
        if self.elapsed_time >= self.frame_duration:
            self.elapsed_time = 0
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True
                    
    def get_current_frame(self) -> arcade.Texture:
        """Get current animation frame"""
        return self.frames[self.current_frame]
        
    def reset(self):
        """Reset animation to start"""
        self.current_frame = 0
        self.elapsed_time = 0
        self.finished = False

class AnimationController:
    """Manages character animations with state machine"""
    def __init__(self):
        self.animations: Dict[AnimationState, Animation] = {}
        self.current_state = AnimationState.IDLE
        self.previous_state = AnimationState.IDLE
        self.state_locked = False
        
    def add_animation(self, state: AnimationState, animation: Animation):
        """Add animation for state"""
        self.animations[state] = animation
        
    def change_state(self, new_state: AnimationState, force: bool = False):
        """Change animation state"""
        if self.state_locked and not force:
            return
            
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            
            if new_state in self.animations:
                self.animations[new_state].reset()
                
    def update(self, delta_time: float):
        """Update current animation"""
        if self.current_state in self.animations:
            anim = self.animations[self.current_state]
            anim.update(delta_time)
            
            # Check for non-looping animation completion
            if anim.finished and not anim.loop:
                self.state_locked = False
                # Return to idle or previous state
                self.change_state(AnimationState.IDLE)
                
    def get_current_texture(self) -> arcade.Texture:
        """Get current frame texture"""
        if self.current_state in self.animations:
            return self.animations[self.current_state].get_current_frame()
        return None
        
    def lock_state(self):
        """Lock current state (for attack animations etc)"""
        self.state_locked = True
        
    def unlock_state(self):
        """Unlock state"""
        self.state_locked = False