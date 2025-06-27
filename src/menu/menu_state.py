# src/menu/menu_state.py
"""
Fixed menu state that works with Arcade 3.0.0
"""
import arcade
from src.core.director import Scene
from src.input.input_manager import InputManager, InputAction
from typing import List, Callable

class MenuItem:
    """Individual menu item with sprite-based rendering"""
    def __init__(self, text: str, action: Callable, x: float, y: float):
        self.text = text
        self.action = action
        self.x = x
        self.y = y
        self.width = 300
        self.height = 50
        self.is_hovered = False
        self.is_selected = False
        
        # Create sprites for background
        self.bg_sprite = None
        self.text_display = None
        self._create_background()
        
    def _create_background(self):
        """Create background sprite"""
        try:
            self.bg_sprite = arcade.SpriteSolidColor(
                int(self.width), int(self.height), arcade.color.DARK_GRAY
            )
            self.bg_sprite.center_x = self.x
            self.bg_sprite.center_y = self.y
        except Exception as e:
            print(f"Error creating menu item background: {e}")
        
    def draw(self):
        """Draw the menu item using sprites"""
        # Update background color based on state
        if self.bg_sprite:
            if self.is_selected:
                color = arcade.color.CRIMSON
            elif self.is_hovered:
                color = arcade.color.DARK_RED
            else:
                color = arcade.color.DARK_GRAY
            
            # Recreate sprite with new color
            try:
                self.bg_sprite = arcade.SpriteSolidColor(
                    int(self.width), int(self.height), color
                )
                self.bg_sprite.center_x = self.x
                self.bg_sprite.center_y = self.y
                self.bg_sprite.draw()
            except Exception as e:
                print(f"Menu item draw error: {e}")
        
        # Draw border using thin sprites
        try:
            border_width = 3 if self.is_selected else 1
            border_color = arcade.color.WHITE
            
            # Top border
            top_border = arcade.SpriteSolidColor(int(self.width), border_width, border_color)
            top_border.center_x = self.x
            top_border.center_y = self.y + self.height/2 - border_width/2
            top_border.draw()
            
            # Bottom border
            bottom_border = arcade.SpriteSolidColor(int(self.width), border_width, border_color)
            bottom_border.center_x = self.x
            bottom_border.center_y = self.y - self.height/2 + border_width/2
            bottom_border.draw()
            
            # Left border
            left_border = arcade.SpriteSolidColor(border_width, int(self.height), border_color)
            left_border.center_x = self.x - self.width/2 + border_width/2
            left_border.center_y = self.y
            left_border.draw()
            
            # Right border
            right_border = arcade.SpriteSolidColor(border_width, int(self.height), border_color)
            right_border.center_x = self.x + self.width/2 - border_width/2
            right_border.center_y = self.y
            right_border.draw()
            
        except Exception as e:
            print(f"Menu border draw error: {e}")
        
        # Draw text - try multiple methods
        self._draw_text_safe()
        
    def _draw_text_safe(self):
        """Draw text with fallback methods"""
        try:
            # Method 1: Try standard arcade.draw_text
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
            return
        except:
            pass
        
        try:
            # Method 2: Try minimal parameters
            arcade.draw_text(self.text, self.x, self.y, arcade.color.WHITE, 24)
            return
        except:
            pass
        
        try:
            # Method 3: Try Text class if available
            if hasattr(arcade, 'Text'):
                text_obj = arcade.Text(
                    self.text, self.x, self.y, arcade.color.WHITE, 24,
                    anchor_x="center", anchor_y="center"
                )
                text_obj.draw()
                return
        except:
            pass
        
        # Fallback: print text info
        print(f"Text: '{self.text}' at ({self.x}, {self.y})")
        
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
        
        # Background sprite
        self.background_sprite = None
        self._create_background()
        
    def _create_background(self):
        """Create background sprite"""
        try:
            self.background_sprite = arcade.SpriteSolidColor(
                1280, 720, (20, 20, 20)
            )
            self.background_sprite.center_x = 640
            self.background_sprite.center_y = 360
        except Exception as e:
            print(f"Error creating menu background: {e}")
        
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
            self.menu_items[self.selected_index].action()
            
    def go_back(self):
        """Go back to previous menu"""
        if not self.input_handled:
            self.input_handled = True
            self.director.pop_scene()
        
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
                    item.action()
                    break
                    
    def update(self, delta_time: float):
        """Update menu state"""
        # Reset input handled flag each frame
        self.input_handled = False
                    
    def draw(self):
        """Draw the menu using sprites"""
        # Draw background
        if self.background_sprite:
            self.background_sprite.draw()
        
        # Draw title using safe text method
        self._draw_title()
        
        # Draw menu items
        for item in self.menu_items:
            item.draw()
            
    def _draw_title(self):
        """Draw title with fallback methods"""
        try:
            # Method 1: Try full parameters
            arcade.draw_text(
                self.title,
                640, 600,
                arcade.color.CRIMSON,
                48,
                anchor_x="center",
                font_name="Arial",
                bold=True
            )
            return
        except:
            pass
        
        try:
            # Method 2: Try minimal parameters
            arcade.draw_text(self.title, 640, 600, arcade.color.CRIMSON, 48)
            return
        except:
            pass
        
        try:
            # Method 3: Try Text class
            if hasattr(arcade, 'Text'):
                text_obj = arcade.Text(
                    self.title, 640, 600, arcade.color.CRIMSON, 48,
                    anchor_x="center"
                )
                text_obj.draw()
                return
        except:
            pass
        
        # Fallback
        print(f"Title: '{self.title}'")