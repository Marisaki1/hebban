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
        
        # Draw text - Updated for Arcade 3.0
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
        self.callbacks_registered = False
        
    def on_enter(self):
        """Setup input callbacks when entering menu"""
        print(f"Entering menu: {self.title}")
        self.clear_input_callbacks()
        self.register_input_callbacks()
        
    def on_exit(self):
        """Clean up when exiting menu"""
        print(f"Exiting menu: {self.title}")
        self.clear_input_callbacks()
        
    def on_pause(self):
        """Called when scene is paused"""
        print(f"Pausing menu: {self.title}")
        
    def on_resume(self):
        """Called when scene is resumed"""
        print(f"Resuming menu: {self.title}")
        self.clear_input_callbacks()
        self.register_input_callbacks()
        
    def clear_input_callbacks(self):
        """Clear input callbacks to prevent conflicts"""
        if self.callbacks_registered:
            self.input_manager.clear_callbacks_for_action(InputAction.MENU_UP)
            self.input_manager.clear_callbacks_for_action(InputAction.MENU_DOWN)
            self.input_manager.clear_callbacks_for_action(InputAction.MENU_LEFT)
            self.input_manager.clear_callbacks_for_action(InputAction.MENU_RIGHT)
            self.input_manager.clear_callbacks_for_action(InputAction.SELECT)
            self.input_manager.clear_callbacks_for_action(InputAction.BACK)
            self.callbacks_registered = False
        
    def register_input_callbacks(self):
        """Register input callbacks"""
        if not self.callbacks_registered:
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
            self.callbacks_registered = True
        
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
            try:
                self.menu_items[self.selected_index].action()
            except Exception as e:
                print(f"Error executing menu action: {e}")
            
    def go_back(self):
        """Go back to previous menu"""
        print(f"Going back from {self.title}")
        # Check if there's a previous scene to go back to
        if len(self.director.scene_stack) > 1:
            self.director.pop_scene()
        else:
            # If this is the main menu or only scene, don't pop
            print("Cannot go back - this is the root scene")
            
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
                    try:
                        item.action()
                    except Exception as e:
                        print(f"Error executing menu action: {e}")
                    break
                    
    def draw(self):
        """Draw the menu"""
        arcade.start_render()
        
        # Draw background
        arcade.draw_rectangle_filled(
            640, 360, 1280, 720, (20, 20, 20)
        )
        
        # Draw title - Updated for Arcade 3.0
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