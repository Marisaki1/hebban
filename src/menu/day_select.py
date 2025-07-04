# src/menu/day_select.py
"""
Day (stage) selection menu within a chapter
"""

import arcade
from src.menu.menu_state import MenuState
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.input.input_manager import InputAction
from src.stages.stage_data import get_unlocked_stages, StageType

class DayCard:
    """Visual representation of a day/stage"""
    
    def __init__(self, day_data: dict, x: float, y: float, index: int, is_unlocked: bool, is_completed: bool):
        self.data = day_data
        self.x = x
        self.y = y
        self.index = index
        self.is_unlocked = is_unlocked
        self.is_completed = is_completed
        self.width = 200
        self.height = 250
        self.is_selected = False
        self.is_hovered = False
        
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is within card bounds"""
        half_width = self.width / 2
        half_height = self.height / 2
        return (self.x - half_width <= x <= self.x + half_width and
                self.y - half_height <= y <= self.y + half_height)
                
    def draw(self):
        """Draw the day card"""
        # Card background
        if not self.is_unlocked:
            bg_color = (40, 40, 40)
            text_color = arcade.color.GRAY
        elif self.is_completed:
            bg_color = arcade.color.DARK_GREEN if not self.is_selected else arcade.color.GREEN
            text_color = arcade.color.WHITE
        elif self.is_selected:
            bg_color = arcade.color.CRIMSON
            text_color = arcade.color.WHITE
        elif self.is_hovered:
            bg_color = arcade.color.DARK_RED
            text_color = arcade.color.WHITE
        else:
            bg_color = arcade.color.DARK_BLUE_GRAY
            text_color = arcade.color.WHITE
            
        # Draw card
        arcade.draw_rectangle_filled(
            self.x, self.y, self.width, self.height, bg_color
        )
        
        # Border
        border_width = 3 if self.is_selected else 1
        if self.is_completed:
            border_color = arcade.color.GOLD
        elif self.is_unlocked:
            border_color = arcade.color.WHITE
        else:
            border_color = arcade.color.DARK_GRAY
            
        arcade.draw_rectangle_outline(
            self.x, self.y, self.width, self.height,
            border_color, border_width
        )
        
        # Stage type icon
        stage_type = self.data.get('type', StageType.COMBAT)
        type_icons = {
            StageType.COMBAT: "⚔️",
            StageType.ESCAPE: "🏃",
            StageType.SURVIVAL: "🛡️",
            StageType.BOSS: "👹",
            StageType.COLLECTION: "💎"
        }
        
        icon = type_icons.get(stage_type, "❓")
        arcade.draw_text(
            icon,
            self.x, self.y + 50,
            arcade.color.WHITE,
            40,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Day name
        arcade.draw_text(
            self.data['name'],
            self.x, self.y,
            text_color,
            16,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Description
        desc = self.data.get('description', '')
        if len(desc) > 30:
            desc = desc[:27] + "..."
            
        arcade.draw_text(
            desc,
            self.x, self.y - 40,
            arcade.color.LIGHT_GRAY if self.is_unlocked else arcade.color.DARK_GRAY,
            10,
            anchor_x="center"
        )
        
        # Status indicators
        if self.is_completed:
            arcade.draw_text(
                "✅ COMPLETE",
                self.x, self.y - 80,
                arcade.color.GREEN,
                12,
                anchor_x="center"
            )
        elif not self.is_unlocked:
            arcade.draw_text(
                "🔒 LOCKED",
                self.x, self.y - 80,
                arcade.color.RED,
                12,
                anchor_x="center"
            )

class DaySelectMenu(MenuState):
    """Day selection menu within a chapter"""
    
    def __init__(self, director, input_manager, chapter_data: dict):
        super().__init__(director, input_manager)
        self.chapter_data = chapter_data
        self.title = f"{chapter_data['name']} - Select Stage"
        self.scene_name = "day_select"
        
        # Get save data
        save_manager = self.director.get_system('save_manager')
        self.save_data = {}
        if save_manager and save_manager.current_save:
            self.save_data = save_manager.current_save.game_data
            
        # Get stages
        self.unlocked_stages = get_unlocked_stages(chapter_data['id'], self.save_data)
        self.all_stages = list(chapter_data.get('days', {}).values())
        
        # Check completion status
        completed_stages = self.save_data.get('progress', {}).get('completed_stages', [])
        for stage in self.all_stages:
            stage_key = f"{chapter_data['id']}_{stage['id']}"
            stage['is_completed'] = stage_key in completed_stages
            stage['is_unlocked'] = any(s['id'] == stage['id'] for s in self.unlocked_stages)
            
        # Create day cards
        self.day_cards = []
        self.selected_index = 0
        self.create_day_cards()
        
    def create_day_cards(self):
        """Create day card visuals"""
        cards_per_row = 4
        card_spacing_x = 250
        card_spacing_y = 300
        start_x = SCREEN_WIDTH // 2 - (min(len(self.all_stages), cards_per_row) - 1) * card_spacing_x // 2
        start_y = SCREEN_HEIGHT // 2 + 50
        
        for i, stage in enumerate(self.all_stages):
            row = i // cards_per_row
            col = i % cards_per_row
            
            x = start_x + col * card_spacing_x
            y = start_y - row * card_spacing_y
            
            card = DayCard(
                stage,
                x, y, i,
                stage['is_unlocked'],
                stage['is_completed']
            )
            
            # Select first unlocked, uncompleted stage
            if stage['is_unlocked'] and not stage['is_completed'] and not any(c.is_selected for c in self.day_cards):
                card.is_selected = True
                self.selected_index = i
            elif i == 0 and not any(c.is_selected for c in self.day_cards):
                card.is_selected = True
                
            self.day_cards.append(card)
            
    def on_enter(self):
        """Setup day select controls"""
        super().on_enter()
        
        self.input_manager.clear_scene_callbacks(self.scene_name)
        
        # Navigation
        self.input_manager.register_action_callback(
            InputAction.MENU_LEFT, self.navigate_left, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_RIGHT, self.navigate_right, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_UP, self.navigate_up, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_DOWN, self.navigate_down, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.SELECT, self.select_day, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.BACK, self.go_back, self.scene_name
        )
        
    def navigate_left(self):
        """Navigate to previous day"""
        if self.selected_index % 4 > 0:  # Not at left edge
            self.update_selection(self.selected_index - 1)
            
    def navigate_right(self):
        """Navigate to next day"""
        if self.selected_index % 4 < 3 and self.selected_index + 1 < len(self.day_cards):
            self.update_selection(self.selected_index + 1)
            
    def navigate_up(self):
        """Navigate up"""
        if self.selected_index >= 4:
            self.update_selection(self.selected_index - 4)
            
    def navigate_down(self):
        """Navigate down"""
        if self.selected_index + 4 < len(self.day_cards):
            self.update_selection(self.selected_index + 4)
            
    def update_selection(self, new_index: int):
        """Update selected day"""
        if 0 <= new_index < len(self.day_cards):
            self.day_cards[self.selected_index].is_selected = False
            self.selected_index = new_index
            self.day_cards[self.selected_index].is_selected = True
            
    def select_day(self):
        """Select current day"""
        selected_card = self.day_cards[self.selected_index]
        
        if not selected_card.is_unlocked:
            # Play error sound
            sound_manager = self.director.get_system('sound_manager')
            if sound_manager:
                sound_manager.play_sfx("menu_back")
            return
            
        # Save selected stage
        save_manager = self.director.get_system('save_manager')
        if save_manager and save_manager.current_save:
            save_manager.current_save.game_data['selected_stage'] = {
                'chapter_id': self.chapter_data['id'],
                'day_id': selected_card.data['id']
            }
            
        # Go to game mode selection
        self.director.change_scene('game_mode_select')
        
    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse hover"""
        for i, card in enumerate(self.day_cards):
            was_hovered = card.is_hovered
            card.is_hovered = card.contains_point(x, y)
            
            # Update selection on hover
            if card.is_hovered and not was_hovered:
                self.update_selection(i)
                
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse click"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            for i, card in enumerate(self.day_cards):
                if card.contains_point(x, y):
                    if self.selected_index == i:
                        # Double click - select
                        self.select_day()
                    else:
                        # Single click - just select
                        self.update_selection(i)
                    break
                    
    def draw(self):
        """Draw day selection screen"""
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
            32,
            anchor_x="center"
        )
        
        # Draw day cards
        for card in self.day_cards:
            card.draw()
            
        # Selected stage info
        if 0 <= self.selected_index < len(self.day_cards):
            selected = self.day_cards[self.selected_index].data
            
            # Primary objective
            primary = selected.get('win_conditions', {}).get('primary', {})
            if primary:
                arcade.draw_text(
                    f"Objective: {primary.get('description', 'Unknown')}",
                    SCREEN_WIDTH // 2,
                    120,
                    arcade.color.YELLOW,
                    16,
                    anchor_x="center"
                )
                
        # Instructions
        arcade.draw_text(
            "Use Arrow Keys or Mouse to select, ENTER/Click to play, ESC to go back",
            SCREEN_WIDTH // 2,
            40,
            arcade.color.WHITE,
            14,
            anchor_x="center"
        )