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
        # Draw background
        if self.is_selected:
            color = arcade.color.CRIMSON
        elif self.is_hovered:
            color = arcade.color.DARK_RED
        else:
            color = arcade.color.DARK_GRAY
            
        arcade.draw_rectangle_filled(
            self.x, self.y, self.width, self.height, color
        )
        
        # Draw text
        arcade.draw_text(
            self.text,
            self.x,
            self.y,
            arcade.color.WHITE,
            24,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial"
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
        
    def on_enter(self):
        """Setup input callbacks when entering menu"""
        self.input_manager.register_action_callback(
            InputAction.MENU_UP, self.navigate_up
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_DOWN, self.navigate_down
        )
        self.input_manager.register_action_callback(
            InputAction.SELECT, self.select_item
        )
        self.input_manager.register_action_callback(
            InputAction.BACK, self.go_back
        )
        
    def navigate_up(self):
        """Navigate to previous menu item"""
        if self.menu_items:
            self.menu_items[self.selected_index].is_selected = False
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
            self.menu_items[self.selected_index].is_selected = True
            
    def navigate_down(self):
        """Navigate to next menu item"""
        if self.menu_items:
            self.menu_items[self.selected_index].is_selected = False
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
            self.menu_items[self.selected_index].is_selected = True
            
    def select_item(self):
        """Select current menu item"""
        if self.menu_items and 0 <= self.selected_index < len(self.menu_items):
            self.menu_items[self.selected_index].action()
            
    def go_back(self):
        """Go back to previous menu"""
        self.director.pop_scene()
        
    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse hover"""
        for i, item in enumerate(self.menu_items):
            if item.contains_point(x, y):
                if self.selected_index != i:
                    self.menu_items[self.selected_index].is_selected = False
                    self.selected_index = i
                    item.is_selected = True
                item.is_hovered = True
            else:
                item.is_hovered = False
                
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse click"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            for item in self.menu_items:
                if item.contains_point(x, y):
                    item.action()
                    break
                    
    def draw(self):
        """Draw the menu"""
        arcade.start_render()
        
        # Draw background
        arcade.draw_rectangle_filled(
            640, 360, 1280, 720, (20, 20, 20)
        )
        
        # Draw title
        arcade.draw_text(
            self.title,
            640,
            600,
            arcade.color.CRIMSON,
            48,
            anchor_x="center",
            font_name="Arial",
            bold=True
        )
        
        # Draw menu items
        for item in self.menu_items:
            item.draw()