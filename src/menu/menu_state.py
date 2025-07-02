"""
Base menu system for Arcade 3.0.0
"""

import arcade
from src.core.director import Scene
from src.input.input_manager import InputManager, InputAction
from typing import List, Callable

class MenuItem:
    """Individual menu item"""
    
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
        """Draw the menu item"""
        # Determine colors
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
        arcade.draw_rectangle_filled(
            self.x, self.y, self.width, self.height, bg_color
        )
        
        # Draw border
        arcade.draw_rectangle_outline(
            self.x, self.y, self.width, self.height,
            arcade.color.WHITE, border_width
        )
        
        # Draw text
        arcade.draw_text(
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
    """Base class for all menu states"""
    
    def __init__(self, director, input_manager: InputManager):
        super().__init__(director)
        self.input_manager = input_manager
        self.menu_items: List[MenuItem] = []
        self.selected_index = 0
        self.title = "Menu"
        self.scene_name = self.__class__.__name__
        
    def on_enter(self):
        """Setup input callbacks when entering menu"""
        self.input_manager.set_current_scene(self.scene_name)
        self.input_manager.clear_scene_callbacks(self.scene_name)
        
        # Register navigation callbacks
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
        
        # Ensure first item is selected
        if self.menu_items and not any(item.is_selected for item in self.menu_items):
            self.menu_items[0].is_selected = True
            self.selected_index = 0
            
    def on_exit(self):
        """Cleanup when leaving menu"""
        self.input_manager.clear_scene_callbacks(self.scene_name)
        
    def navigate_up(self):
        """Navigate to previous menu item"""
        if self.menu_items:
            self.menu_items[self.selected_index].is_selected = False
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
            self.menu_items[self.selected_index].is_selected = True
            
            # Clear hover states
            for item in self.menu_items:
                item.is_hovered = False
                
    def navigate_down(self):
        """Navigate to next menu item"""
        if self.menu_items:
            self.menu_items[self.selected_index].is_selected = False
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
            self.menu_items[self.selected_index].is_selected = True
            
            # Clear hover states
            for item in self.menu_items:
                item.is_hovered = False
                
    def select_item(self):
        """Select current menu item"""
        if self.menu_items and 0 <= self.selected_index < len(self.menu_items):
            try:
                self.menu_items[self.selected_index].action()
            except Exception as e:
                print(f"Error executing menu action: {e}")
                
    def go_back(self):
        """Go back to previous menu"""
        try:
            self.director.pop_scene()
        except Exception as e:
            print(f"Error going back: {e}")
            
    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse hover"""
        for i, item in enumerate(self.menu_items):
            if item.contains_point(x, y):
                item.is_hovered = True
                
                # Update selection if different
                if self.selected_index != i:
                    if 0 <= self.selected_index < len(self.menu_items):
                        self.menu_items[self.selected_index].is_selected = False
                    self.selected_index = i
                    item.is_selected = True
            else:
                item.is_hovered = False
                
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse click"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            for i, item in enumerate(self.menu_items):
                if item.contains_point(x, y):
                    # Update selection
                    if self.selected_index != i:
                        if 0 <= self.selected_index < len(self.menu_items):
                            self.menu_items[self.selected_index].is_selected = False
                        self.selected_index = i
                        item.is_selected = True
                        
                    # Execute action
                    try:
                        item.action()
                    except Exception as e:
                        print(f"Error executing menu action: {e}")
                    break
                    
    def draw(self):
        """Draw the menu"""
        from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
        
        # Draw background
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            (20, 20, 20)
        )
        
        # Draw title
        arcade.draw_text(
            self.title,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
            arcade.color.CRIMSON,
            48,
            anchor_x="center"
        )
        
        # Draw menu items
        for item in self.menu_items:
            item.draw()