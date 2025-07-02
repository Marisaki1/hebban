# src/menu/menu_state.py
"""
Fixed menu state that works with Arcade 3.0.0 - Uses updated drawing functions
"""
import arcade
from src.core.director import Scene
from src.core.arcade_compat import safe_draw_rectangle_filled, safe_draw_rectangle_outline, safe_draw_text
from src.input.input_manager import InputManager, InputAction
from typing import List, Callable

class MenuItem:
    """Individual menu item with Arcade 3.0.0 compatible drawing"""
    def __init__(self, text: str, action: Callable, x: float, y: float):
        self.text = text
        self.action = action
        self.x = x
        self.y = y
        self.width = 300
        self.height = 50
        self.is_hovered = False
        self.is_selected = False
        
    def draw(self):
        """Draw the menu item using Arcade 3.0.0 compatible functions"""
        # Determine colors based on state
        if self.is_selected:
            bg_color = arcade.color.CRIMSON
            border_width = 3
        elif self.is_hovered:
            bg_color = arcade.color.DARK_RED
            border_width = 2
        else:
            bg_color = arcade.color.DARK_GRAY
            border_width = 1
        
        # Draw background
        safe_draw_rectangle_filled(
            self.x, self.y, self.width, self.height, bg_color
        )
        
        # Draw border
        safe_draw_rectangle_outline(
            self.x, self.y, self.width, self.height, 
            arcade.color.WHITE, border_width
        )
        
        # Draw text
        safe_draw_text(
            self.text,
            self.x, self.y,
            arcade.color.WHITE,
            24,
            anchor_x="center",
            anchor_y="center"
        )
        
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is within menu item bounds"""
        half_width = self.width / 2
        half_height = self.height / 2
        return (self.x - half_width <= x <= self.x + half_width and
                self.y - half_height <= y <= self.y + half_height)

class MenuState(Scene):
    """Base class for all menu states - Fixed for Arcade 3.0.0"""
    def __init__(self, director, input_manager: InputManager):
        super().__init__(director)
        self.input_manager = input_manager
        self.menu_items: List[MenuItem] = []
        self.selected_index = 0
        self.title = "Menu"
        self.scene_name = self.__class__.__name__
        
        # Track if we're already handling input to prevent double-triggers
        self.input_handled = False
        
    def on_enter(self):
        """Setup input callbacks when entering menu"""
        # Set current scene in input manager
        self.input_manager.set_current_scene(self.scene_name)
        
        # Clear any existing callbacks for this scene
        self.input_manager.clear_scene_callbacks(self.scene_name)
        
        # Register fresh callbacks
        self.input_manager.register_action_callback(
            InputAction.MENU_UP, self.navigate_up, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_DOWN, self.navigate_down, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.SELECT, self.select_item, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.BACK, self.go_back, self.scene_name
        )
        
        # Ensure first item is selected if we have items
        if self.menu_items and not any(item.is_selected for item in self.menu_items):
            self.menu_items[0].is_selected = True
            self.selected_index = 0
            
    def on_exit(self):
        """Cleanup when leaving menu"""
        # Clear this scene's callbacks
        self.input_manager.clear_scene_callbacks(self.scene_name)
        
    def on_pause(self):
        """Called when scene is paused"""
        # Clear callbacks when paused
        self.input_manager.clear_scene_callbacks(self.scene_name)
        
    def on_resume(self):
        """Called when scene is resumed"""
        # Re-register callbacks when resumed
        self.on_enter()
        
    def navigate_up(self):
        """Navigate to previous menu item"""
        if self.menu_items and not self.input_handled:
            self.input_handled = True
            self.menu_items[self.selected_index].is_selected = False
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
            self.menu_items[self.selected_index].is_selected = True
            # Clear all hover states
            for item in self.menu_items:
                item.is_hovered = False
            
    def navigate_down(self):
        """Navigate to next menu item"""
        if self.menu_items and not self.input_handled:
            self.input_handled = True
            self.menu_items[self.selected_index].is_selected = False
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
            self.menu_items[self.selected_index].is_selected = True
            # Clear all hover states
            for item in self.menu_items:
                item.is_hovered = False
            
    def select_item(self):
        """Select current menu item"""
        if self.menu_items and 0 <= self.selected_index < len(self.menu_items) and not self.input_handled:
            self.input_handled = True
            try:
                self.menu_items[self.selected_index].action()
            except Exception as e:
                print(f"Error executing menu action: {e}")
            
    def go_back(self):
        """Go back to previous menu"""
        if not self.input_handled:
            self.input_handled = True
            try:
                self.director.pop_scene()
            except Exception as e:
                print(f"Error going back: {e}")
        
    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse hover with improved selection"""
        mouse_over_item = False
        
        for i, item in enumerate(self.menu_items):
            if item.contains_point(x, y):
                mouse_over_item = True
                item.is_hovered = True
                
                # Update selection if mouse is over a different item
                if self.selected_index != i:
                    # Deselect previous item
                    if 0 <= self.selected_index < len(self.menu_items):
                        self.menu_items[self.selected_index].is_selected = False
                    
                    # Select new item
                    self.selected_index = i
                    item.is_selected = True
            else:
                item.is_hovered = False
                
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse click"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            for i, item in enumerate(self.menu_items):
                if item.contains_point(x, y):
                    # Update selection first
                    if self.selected_index != i:
                        if 0 <= self.selected_index < len(self.menu_items):
                            self.menu_items[self.selected_index].is_selected = False
                        self.selected_index = i
                        item.is_selected = True
                    
                    # Then execute action
                    try:
                        item.action()
                    except Exception as e:
                        print(f"Error executing menu action: {e}")
                    break
                    
    def update(self, delta_time: float):
        """Update menu state"""
        # Reset input handled flag each frame
        self.input_handled = False
                    
    def draw(self):
        """Draw the menu using Arcade 3.0.0 compatible functions"""
        # Draw background
        safe_draw_rectangle_filled(
            640, 360, 1280, 720, (20, 20, 20)
        )
        
        # Draw title
        safe_draw_text(
            self.title,
            640, 600,
            arcade.color.CRIMSON,
            48,
            anchor_x="center"
        )
        
        # Draw menu items
        for item in self.menu_items:
            try:
                item.draw()
            except Exception as e:
                print(f"Error drawing menu item '{item.text}': {e}")
                # Draw fallback text
                safe_draw_text(
                    item.text,
                    item.x, item.y,
                    arcade.color.WHITE,
                    20,
                    anchor_x="center",
                    anchor_y="center"
                )