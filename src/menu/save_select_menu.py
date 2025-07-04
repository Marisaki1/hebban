"""
Save slot selection menu for Continue option
"""

import arcade
from datetime import datetime
from src.menu.menu_state import MenuState, MenuItem
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.input.input_manager import InputAction

class SaveSlot:
    """Visual representation of a save slot"""
    
    def __init__(self, slot_data: dict, x: float, y: float):
        self.slot_data = slot_data
        self.x = x
        self.y = y
        self.width = 600
        self.height = 120
        self.is_selected = False
        self.is_hovered = False
        
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is within slot bounds"""
        half_width = self.width / 2
        half_height = self.height / 2
        return (self.x - half_width <= x <= self.x + half_width and
                self.y - half_height <= y <= self.y + half_height)
                
    def draw(self):
        """Draw the save slot"""
        # Slot background
        if self.is_selected:
            color = arcade.color.CRIMSON
            border_width = 4
        elif self.is_hovered:
            color = arcade.color.DARK_RED
            border_width = 2
        elif self.slot_data['exists']:
            color = arcade.color.DARK_BLUE_GRAY
            border_width = 1
        else:
            color = arcade.color.DARK_GRAY
            border_width = 1
            
        # Draw slot
        arcade.draw_rectangle_filled(
            self.x, self.y, self.width, self.height, color
        )
        arcade.draw_rectangle_outline(
            self.x, self.y, self.width, self.height,
            arcade.color.WHITE, border_width
        )
        
        # Slot number
        arcade.draw_text(
            f"Save Slot {self.slot_data['slot']}",
            self.x - 280, self.y + 35,
            arcade.color.WHITE,
            20
        )
        
        if self.slot_data['exists']:
            # Save data exists
            data = self.slot_data['data']
            game_data = data.get('game_data', {})
            
            # Character info
            char_name = game_data.get('selected_character', 'Unknown')
            squad_name = game_data.get('selected_squad', 'Unknown')
            
            arcade.draw_text(
                f"Character: {char_name.title()} ({squad_name})",
                self.x - 280, self.y,
                arcade.color.WHITE,
                14
            )
            
            # Progress info
            progress = game_data.get('progress', {})
            total_score = progress.get('total_score', 0)
            current_level = progress.get('current_level', 1)
            
            arcade.draw_text(
                f"Level: {current_level} | Score: {total_score:,}",
                self.x - 280, self.y - 20,
                arcade.color.LIGHT_GRAY,
                12
            )
            
            # Timestamp
            timestamp_str = data.get('timestamp', '')
            if timestamp_str:
                try:
                    # Parse ISO timestamp
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    formatted_time = timestamp.strftime("%Y-%m-%d %H:%M")
                except:
                    formatted_time = "Unknown time"
            else:
                formatted_time = "Unknown time"
                
            arcade.draw_text(
                f"Saved: {formatted_time}",
                self.x + 200, self.y,
                arcade.color.YELLOW,
                12,
                anchor_x="right"
            )
            
            # Multiplayer indicator
            if game_data.get('was_multiplayer', False):
                arcade.draw_text(
                    "🌐 Multiplayer",
                    self.x + 200, self.y - 25,
                    arcade.color.CYAN,
                    12,
                    anchor_x="right"
                )
        else:
            # Empty slot
            arcade.draw_text(
                "Empty Slot",
                self.x, self.y,
                arcade.color.GRAY,
                16,
                anchor_x="center",
                anchor_y="center"
            )

class SaveSelectMenu(MenuState):
    """Save slot selection menu"""
    
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Select Save to Continue"
        self.scene_name = "save_select"
        
        # Load save slots
        save_manager = self.director.get_system('save_manager')
        self.save_slots_data = save_manager.get_save_files()
        self.save_slots = []
        self.selected_slot_index = 0
        
        # Create save slot visuals
        self.create_save_slots()
        
        # Menu items for actions
        self.menu_items = [
            MenuItem(
                "Load Selected Save",
                self.load_selected_save,
                SCREEN_WIDTH // 2,
                150
            ),
            MenuItem(
                "Delete Selected Save",
                self.delete_selected_save,
                SCREEN_WIDTH // 2,
                100
            ),
            MenuItem(
                "Back to Main Menu",
                self.go_back,
                SCREEN_WIDTH // 2,
                50
            )
        ]
        
        if self.menu_items:
            self.menu_items[0].is_selected = True
            
    def create_save_slots(self):
        """Create save slot visuals"""
        start_y = SCREEN_HEIGHT - 200
        spacing = 140
        
        for i, slot_data in enumerate(self.save_slots_data):
            slot = SaveSlot(
                slot_data,
                SCREEN_WIDTH // 2,
                start_y - i * spacing
            )
            if i == 0:
                slot.is_selected = True
            self.save_slots.append(slot)
            
    def on_enter(self):
        """Setup save select controls"""
        super().on_enter()
        
        # Clear and add specific controls
        self.input_manager.clear_scene_callbacks(self.scene_name)
        
        # Slot navigation
        self.input_manager.register_action_callback(
            InputAction.MENU_UP, self.select_previous_slot, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_DOWN, self.select_next_slot, self.scene_name
        )
        
        # Actions
        self.input_manager.register_action_callback(
            InputAction.SELECT, self.load_selected_save, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.BACK, self.go_back, self.scene_name
        )
        
    def select_previous_slot(self):
        """Select previous save slot"""
        if self.save_slots:
            self.save_slots[self.selected_slot_index].is_selected = False
            self.selected_slot_index = (self.selected_slot_index - 1) % len(self.save_slots)
            self.save_slots[self.selected_slot_index].is_selected = True
            
    def select_next_slot(self):
        """Select next save slot"""
        if self.save_slots:
            self.save_slots[self.selected_slot_index].is_selected = False
            self.selected_slot_index = (self.selected_slot_index + 1) % len(self.save_slots)
            self.save_slots[self.selected_slot_index].is_selected = True
            
    def load_selected_save(self):
        """Load the selected save slot"""
        if self.save_slots and 0 <= self.selected_slot_index < len(self.save_slots):
            slot_data = self.save_slots_data[self.selected_slot_index]
            
            if slot_data['exists']:
                game_instance = self.director.get_system('game_instance')
                if game_instance:
                    success = game_instance.continue_from_save(slot_data['slot'])
                    if not success:
                        print(f"Failed to load save slot {slot_data['slot']}")
            else:
                print("Cannot load empty save slot")
                
    def delete_selected_save(self):
        """Delete the selected save slot"""
        if self.save_slots and 0 <= self.selected_slot_index < len(self.save_slots):
            slot_data = self.save_slots_data[self.selected_slot_index]
            
            if slot_data['exists']:
                save_manager = self.director.get_system('save_manager')
                if save_manager:
                    success = save_manager.delete_save(slot_data['slot'])
                    if success:
                        # Refresh save slots
                        self.save_slots_data = save_manager.get_save_files()
                        self.save_slots.clear()
                        self.create_save_slots()
                        print(f"Deleted save slot {slot_data['slot']}")
            else:
                print("Cannot delete empty save slot")
                
    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse hover"""
        for i, slot in enumerate(self.save_slots):
            if slot.contains_point(x, y):
                slot.is_hovered = True
                # Update selection
                if self.selected_slot_index != i:
                    self.save_slots[self.selected_slot_index].is_selected = False
                    self.selected_slot_index = i
                    slot.is_selected = True
            else:
                slot.is_hovered = False
                
        # Handle menu item hover
        super().on_mouse_motion(x, y, dx, dy)
                
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse click"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Check save slot clicks
            for i, slot in enumerate(self.save_slots):
                if slot.contains_point(x, y):
                    if self.selected_slot_index != i:
                        self.save_slots[self.selected_slot_index].is_selected = False
                        self.selected_slot_index = i
                        slot.is_selected = True
                    else:
                        # Double-click to load
                        self.load_selected_save()
                    return
                    
        # Handle menu item clicks
        super().on_mouse_press(x, y, button, modifiers)
                    
    def draw(self):
        """Draw save selection screen"""
        # Background
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            (20, 20, 20)
        )
        
        # Title
        arcade.draw_text(
            self.title,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 60,
            arcade.color.CRIMSON,
            36,
            anchor_x="center"
        )
        
        # Draw save slots
        for slot in self.save_slots:
            slot.draw()
            
        # Draw menu items
        for item in self.menu_items:
            item.draw()
            
        # Instructions
        arcade.draw_text(
            "Use UP/DOWN to select, ENTER to load, ESC to go back",
            SCREEN_WIDTH // 2,
            20,
            arcade.color.WHITE,
            14,
            anchor_x="center"
        )