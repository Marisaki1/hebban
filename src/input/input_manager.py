"""
Input management system - COMPLETELY FIXED
"""

import arcade
from typing import Dict, List, Callable, Set
from enum import Enum

class InputAction(Enum):
    """Game input actions"""
    MENU_UP = "menu_up"
    MENU_DOWN = "menu_down"
    MENU_LEFT = "menu_left"
    MENU_RIGHT = "menu_right"
    SELECT = "select"
    BACK = "back"
    PAUSE = "pause"
    JUMP = "jump"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    ACTION_1 = "action_1"
    ACTION_2 = "action_2"

class InputManager:
    """Manages all input handling - COMPLETELY FIXED"""
    
    def __init__(self):
        # Key mappings
        self.input_mappings: Dict[InputAction, List[int]] = {
            InputAction.MENU_UP: [arcade.key.UP, arcade.key.W],
            InputAction.MENU_DOWN: [arcade.key.DOWN, arcade.key.S],
            InputAction.MENU_LEFT: [arcade.key.LEFT, arcade.key.A],
            InputAction.MENU_RIGHT: [arcade.key.RIGHT, arcade.key.D],
            InputAction.SELECT: [arcade.key.ENTER, arcade.key.SPACE],
            InputAction.BACK: [arcade.key.ESCAPE, arcade.key.BACKSPACE],
            InputAction.PAUSE: [arcade.key.P, arcade.key.ESCAPE],
            InputAction.JUMP: [arcade.key.SPACE, arcade.key.W],
            InputAction.MOVE_LEFT: [arcade.key.LEFT, arcade.key.A],
            InputAction.MOVE_RIGHT: [arcade.key.RIGHT, arcade.key.D],
            InputAction.ACTION_1: [arcade.key.Z, arcade.key.J],
            InputAction.ACTION_2: [arcade.key.X, arcade.key.K],
        }
        
        # FIXED: Only store callbacks for current active scene
        self.pressed_keys: Set[int] = set()
        self.current_scene_callbacks: Dict[InputAction, List[Callable]] = {}
        self.current_scene: str = None
        
        # Mouse state
        self.mouse_x = 0
        self.mouse_y = 0
        self.controller = None
        
    def set_current_scene(self, scene_name: str):
        """Set current scene and CLEAR ALL previous callbacks"""
        # FIXED: Clear ALL callbacks when switching scenes
        self.clear_all_callbacks()
        self.current_scene = scene_name
        
    def clear_all_callbacks(self):
        """FIXED: Clear ALL callbacks to prevent accumulation"""
        self.current_scene_callbacks.clear()
        
    def register_action_callback(self, action: InputAction, callback: Callable, scene_name: str = None):
        """Register callback for an action - ONLY for current scene"""
        # FIXED: Only register if this is for the current scene
        if scene_name and scene_name != self.current_scene:
            return
            
        if action not in self.current_scene_callbacks:
            self.current_scene_callbacks[action] = []
            
        self.current_scene_callbacks[action].append(callback)
        
    def clear_scene_callbacks(self, scene_name: str):
        """FIXED: This now clears all callbacks regardless of scene name"""
        self.clear_all_callbacks()
        
    def is_action_pressed(self, action: InputAction) -> bool:
        """Check if action is currently pressed"""
        if action in self.input_mappings:
            for key in self.input_mappings[action]:
                if key in self.pressed_keys:
                    return True
        return False
        
    def on_key_press(self, key, modifiers):
        """Handle key press - FIXED to only trigger current scene callbacks"""
        self.pressed_keys.add(key)
        
        # Debug logging
        if key == arcade.key.ESCAPE:
            print(f"ESC pressed - Current scene: {self.current_scene}")
            print(f"Available callbacks: {list(self.current_scene_callbacks.keys())}")
        
        # FIXED: Only trigger callbacks for current scene
        for action, keys in self.input_mappings.items():
            if key in keys and action in self.current_scene_callbacks:
                print(f"Triggering action: {action.value}")
                # Execute all callbacks for this action
                for callback in self.current_scene_callbacks[action]:
                    try:
                        callback()
                    except Exception as e:
                        print(f"Error in input callback for {action.value}: {e}")
                        
    def on_key_release(self, key, modifiers):
        """Handle key release"""
        self.pressed_keys.discard(key)
        
    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse motion"""
        self.mouse_x = x
        self.mouse_y = y
        
    def get_movement_vector(self) -> tuple:
        """Get movement vector for player"""
        x = 0
        
        if self.is_action_pressed(InputAction.MOVE_LEFT):
            x -= 1
        if self.is_action_pressed(InputAction.MOVE_RIGHT):
            x += 1
            
        return x, 0
        
    def update_controller(self):
        """Update controller state (placeholder)"""
        # Controller support can be added here
        pass