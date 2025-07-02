"""
Input management system
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
    """Manages all input handling"""
    
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
        
        # State tracking
        self.pressed_keys: Set[int] = set()
        self.action_callbacks: Dict[InputAction, List[Callable]] = {}
        self.scene_callbacks: Dict[str, Dict[InputAction, List[Callable]]] = {}
        self.current_scene: str = None
        
        # Mouse state
        self.mouse_x = 0
        self.mouse_y = 0
        
        # Controller support (basic)
        self.controller = None
        
    def set_current_scene(self, scene_name: str):
        """Set current scene for callback management"""
        self.current_scene = scene_name
        if scene_name not in self.scene_callbacks:
            self.scene_callbacks[scene_name] = {}
            
    def register_action_callback(self, action: InputAction, callback: Callable, scene_name: str = None):
        """Register callback for an action"""
        if scene_name is None:
            scene_name = self.current_scene
            
        # Initialize structures
        if action not in self.action_callbacks:
            self.action_callbacks[action] = []
            
        if scene_name not in self.scene_callbacks:
            self.scene_callbacks[scene_name] = {}
            
        if action not in self.scene_callbacks[scene_name]:
            self.scene_callbacks[scene_name][action] = []
            
        # Add callback
        self.action_callbacks[action].append(callback)
        self.scene_callbacks[scene_name][action].append(callback)
        
    def clear_scene_callbacks(self, scene_name: str):
        """Clear callbacks for a scene"""
        if scene_name in self.scene_callbacks:
            # Remove from global callbacks
            for action, callbacks in self.scene_callbacks[scene_name].items():
                if action in self.action_callbacks:
                    for callback in callbacks:
                        if callback in self.action_callbacks[action]:
                            self.action_callbacks[action].remove(callback)
            
            # Clear scene callbacks
            self.scene_callbacks[scene_name].clear()
            
    def is_action_pressed(self, action: InputAction) -> bool:
        """Check if action is currently pressed"""
        if action in self.input_mappings:
            for key in self.input_mappings[action]:
                if key in self.pressed_keys:
                    return True
        return False
        
    def on_key_press(self, key, modifiers):
        """Handle key press"""
        self.pressed_keys.add(key)
        
        # Trigger action callbacks
        for action, keys in self.input_mappings.items():
            if key in keys and action in self.action_callbacks:
                for callback in self.action_callbacks[action]:
                    try:
                        callback()
                    except Exception as e:
                        print(f"Error in input callback: {e}")
                        
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