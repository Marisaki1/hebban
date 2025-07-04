# src/menu/chapter_select.py
"""
Chapter selection menu
"""

import arcade
from src.menu.menu_state import MenuState
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.input.input_manager import InputAction
from src.stages.stage_data import get_unlocked_chapters

class ChapterCard:
    """Visual representation of a chapter"""
    
    def __init__(self, chapter_data: dict, x: float, y: float, index: int, is_unlocked: bool):
        self.data = chapter_data
        self.x = x
        self.y = y
        self.index = index
        self.is_unlocked = is_unlocked
        self.width = 300
        self.height = 400
        self.is_selected = False
        self.is_hovered = False
        
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is within card bounds"""
        half_width = self.width / 2
        half_height = self.height / 2
        return (self.x - half_width <= x <= self.x + half_width and
                self.y - half_height <= y <= self.y + half_height)
                
    def draw(self):
        """Draw the chapter card"""
        # Card background
        if not self.is_unlocked:
            bg_color = (40, 40, 40)
            text_color = arcade.color.GRAY
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
        border_color = arcade.color.GOLD if self.is_unlocked else arcade.color.DARK_GRAY
        arcade.draw_rectangle_outline(
            self.x, self.y, self.width, self.height,
            border_color, border_width
        )
        
        # Chapter image placeholder
        image_size = 200
        arcade.draw_rectangle_filled(
            self.x, self.y + 50, image_size, image_size,
            (60, 60, 60) if self.is_unlocked else (30, 30, 30)
        )
        
        # Chapter number
        chapter_num = self.data['id'].replace('chapter_', '')
        arcade.draw_text(
            f"Chapter {chapter_num}",
            self.x, self.y + 50,
            text_color,
            48,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Chapter name
        arcade.draw_text(
            self.data['name'],
            self.x, self.y - 80,
            text_color,
            20,
            anchor_x="center"
        )
        
        # Description
        desc = self.data.get('description', '')
        if len(desc) > 40:
            desc = desc[:37] + "..."
            
        arcade.draw_text(
            desc,
            self.x, self.y - 120,
            arcade.color.LIGHT_GRAY if self.is_unlocked else arcade.color.DARK_GRAY,
            14,
            anchor_x="center"
        )
        
        # Lock indicator
        if not self.is_unlocked:
            arcade.draw_text(
                "🔒 LOCKED",
                self.x, self.y - 160,
                arcade.color.RED,
                16,
                anchor_x="center"
            )

class ChapterSelectMenu(MenuState):
    """Chapter selection menu"""
    
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Select Chapter"
        self.scene_name = "chapter_select"
        
        # Get save data
        save_manager = self.director.get_system('save_manager')
        save_data = {}
        if save_manager and save_manager.current_save:
            save_data = save_manager.current_save.game_data
            
        # Get chapters
        self.chapters = get_unlocked_chapters(save_data)
        self.all_chapters = []  # Include locked chapters for display
        
        # Import here to avoid circular import
        from src.stages.stage_data import CHAPTERS
        for chapter_id, chapter_data in CHAPTERS.items():
            chapter_data['is_unlocked'] = any(c['id'] == chapter_id for c in self.chapters)
            self.all_chapters.append(chapter_data)
            
        # Sort by ID
        self.all_chapters.sort(key=lambda x: x['id'])
        
        # Create chapter cards
        self.chapter_cards = []
        self.selected_index = 0
        self.create_chapter_cards()
        
    def create_chapter_cards(self):
        """Create chapter card visuals"""
        cards_per_row = 3
        card_spacing_x = 350
        card_spacing_y = 450
        start_x = SCREEN_WIDTH // 2 - (min(len(self.all_chapters), cards_per_row) - 1) * card_spacing_x // 2
        start_y = SCREEN_HEIGHT // 2 + 100
        
        for i, chapter in enumerate(self.all_chapters):
            row = i // cards_per_row
            col = i % cards_per_row
            
            x = start_x + col * card_spacing_x
            y = start_y - row * card_spacing_y
            
            card = ChapterCard(
                chapter,
                x, y, i,
                chapter['is_unlocked']
            )
            
            # Select first unlocked chapter
            if i == 0 and chapter['is_unlocked']:
                card.is_selected = True
                
            self.chapter_cards.append(card)
            
    def on_enter(self):
        """Setup chapter select controls"""
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
            InputAction.SELECT, self.select_chapter, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.BACK, self.go_back, self.scene_name
        )
        
    def navigate_left(self):
        """Navigate to previous chapter"""
        if self.selected_index % 3 > 0:  # Not at left edge
            self.update_selection(self.selected_index - 1)
            
    def navigate_right(self):
        """Navigate to next chapter"""
        if self.selected_index % 3 < 2 and self.selected_index + 1 < len(self.chapter_cards):
            self.update_selection(self.selected_index + 1)
            
    def navigate_up(self):
        """Navigate up"""
        if self.selected_index >= 3:
            self.update_selection(self.selected_index - 3)
            
    def navigate_down(self):
        """Navigate down"""
        if self.selected_index + 3 < len(self.chapter_cards):
            self.update_selection(self.selected_index + 3)
            
    def update_selection(self, new_index: int):
        """Update selected chapter"""
        if 0 <= new_index < len(self.chapter_cards):
            self.chapter_cards[self.selected_index].is_selected = False
            self.selected_index = new_index
            self.chapter_cards[self.selected_index].is_selected = True
            
    def select_chapter(self):
        """Select current chapter"""
        selected_card = self.chapter_cards[self.selected_index]
        
        if not selected_card.is_unlocked:
            # Play error sound
            sound_manager = self.director.get_system('sound_manager')
            if sound_manager:
                sound_manager.play_sfx("menu_back")
            return
            
        # Save selected chapter
        save_manager = self.director.get_system('save_manager')
        if save_manager and save_manager.current_save:
            save_manager.current_save.game_data['selected_chapter'] = selected_card.data['id']
            
        # Go to day selection
        from src.menu.day_select import DaySelectMenu
        day_select = DaySelectMenu(self.director, self.input_manager, selected_card.data)
        self.director.register_scene("day_select", day_select)
        self.director.push_scene("day_select")
        
    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse hover"""
        for i, card in enumerate(self.chapter_cards):
            was_hovered = card.is_hovered
            card.is_hovered = card.contains_point(x, y)
            
            # Update selection on hover
            if card.is_hovered and not was_hovered:
                self.update_selection(i)
                
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse click"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            for i, card in enumerate(self.chapter_cards):
                if card.contains_point(x, y):
                    if self.selected_index == i:
                        # Double click - select
                        self.select_chapter()
                    else:
                        # Single click - just select
                        self.update_selection(i)
                    break
                    
    def draw(self):
        """Draw chapter selection screen"""
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
        
        # Draw chapter cards
        for card in self.chapter_cards:
            card.draw()
            
        # Instructions
        arcade.draw_text(
            "Use Arrow Keys or Mouse to select, ENTER/Click to confirm, ESC to go back",
            SCREEN_WIDTH // 2,
            40,
            arcade.color.WHITE,
            14,
            anchor_x="center"
        )
        
        # Progress indicator
        save_manager = self.director.get_system('save_manager')
        if save_manager and save_manager.current_save:
            progress = save_manager.current_save.game_data.get('progress', {})
            completed_stages = len(progress.get('completed_stages', []))
            
            arcade.draw_text(
                f"Progress: {completed_stages} stages completed",
                SCREEN_WIDTH - 20,
                SCREEN_HEIGHT - 40,
                arcade.color.YELLOW,
                14,
                anchor_x="right"
            )