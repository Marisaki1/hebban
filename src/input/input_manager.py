import arcade
from typing import Dict, List, Callable, Any
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

class InputType(Enum):
    """Input device types"""
    KEYBOARD = "keyboard"
    MOUSE = "mouse"
    CONTROLLER = "controller"

class InputManager:
    """Universal input manager for keyboard, mouse, and controller"""
    def __init__(self):
        self.input_mappings: Dict[InputAction, List[Any]] = {
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
        
        self.controller_mappings: Dict[InputAction, List[int]] = {
            # Xbox controller mappings
            InputAction.SELECT: [0],  # A button
            InputAction.BACK: [1],    # B button
            InputAction.JUMP: [0],    # A button
            InputAction.ACTION_1: [2], # X button
            InputAction.ACTION_2: [3], # Y button
        }
        
        self.pressed_keys: set = set()
        self.pressed_buttons: set = set()
        self.action_callbacks: Dict[InputAction, List[Callable]] = {}
        self.last_input_type = InputType.KEYBOARD
        
        # Controller state
        self.controller = None
        self.controller_deadzone = 0.2
        
    def register_action_callback(self, action: InputAction, callback: Callable):
        """Register a callback for an input action"""
        if action not in self.action_callbacks:
            self.action_callbacks[action] = []
        self.action_callbacks[action].append(callback)
        
    def is_action_pressed(self, action: InputAction) -> bool:
        """Check if an action is currently pressed"""
        # Check keyboard
        if action in self.input_mappings:
            for key in self.input_mappings[action]:
                if key in self.pressed_keys:
                    return True
                    
        # Check controller
        if self.controller and action in self.controller_mappings:
            for button in self.controller_mappings[action]:
                if button in self.pressed_buttons:
                    return True
                    
        return False
        
    def on_key_press(self, key, modifiers):
        """Handle key press events"""
        self.pressed_keys.add(key)
        self.last_input_type = InputType.KEYBOARD
        
        # Check for action triggers
        for action, keys in self.input_mappings.items():
            if key in keys and action in self.action_callbacks:
                for callback in self.action_callbacks[action]:
                    callback()
                    
    def on_key_release(self, key, modifiers):
        """Handle key release events"""
        self.pressed_keys.discard(key)
        
    def update_controller(self):
        """Update controller state"""
        # This would interface with arcade's controller support
        # Implementation depends on arcade version
        pass
        
    def get_movement_vector(self) -> tuple:
        """Get normalized movement vector"""
        x = 0
        y = 0
        
        if self.is_action_pressed(InputAction.MOVE_LEFT):
            x -= 1
        if self.is_action_pressed(InputAction.MOVE_RIGHT):
            x += 1
            
        # Normalize diagonal movement
        if x != 0 and y != 0:
            x *= 0.707
            y *= 0.707
            
        return x, y