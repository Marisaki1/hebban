# src/menu/character_select.py - Fixed with mouse support
"""
Fixed character selection menu with proper save persistence and mouse support
"""

import arcade
from src.menu.menu_state import MenuState
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.input.input_manager import InputAction

class CharacterGrid:
    """3x2 character selection grid with mouse support"""
    
    def __init__(self, x: float, y: float, characters: list):
        self.x = x
        self.y = y
        self.characters = characters
        self.selected_index = 0
        self.cell_width = 120
        self.cell_height = 150
        self.spacing = 20
        self.grid_cells = []
        self._create_grid()
        
    def _create_grid(self):
        """Create grid cells for characters"""
        for i, char in enumerate(self.characters[:6]):  # Max 6 characters
            row = i // 3
            col = i % 3
            
            cell_x = self.x + col * (self.cell_width + self.spacing)
            cell_y = self.y - row * (self.cell_height + self.spacing)
            
            self.grid_cells.append({
                'character': char,
                'x': cell_x,
                'y': cell_y,
                'index': i,
                'selected': i == 0,
                'hovered': False
            })
            
    def move_selection(self, direction: str):
        """Move selection in grid"""
        old_index = self.selected_index
        
        if direction == 'up' and self.selected_index >= 3:
            self.selected_index -= 3
        elif direction == 'down' and self.selected_index < 3:
            if self.selected_index + 3 < len(self.characters):
                self.selected_index += 3
        elif direction == 'left' and self.selected_index % 3 > 0:
            self.selected_index -= 1
        elif direction == 'right' and self.selected_index % 3 < 2:
            if self.selected_index + 1 < len(self.characters):
                self.selected_index += 1
                
        # Update selection state
        if old_index != self.selected_index:
            self.grid_cells[old_index]['selected'] = False
            self.grid_cells[self.selected_index]['selected'] = True
            
            # Clear all hovers when using keyboard
            for cell in self.grid_cells:
                cell['hovered'] = False
                
    def get_cell_at_position(self, x: float, y: float) -> int:
        """Get cell index at mouse position"""
        for cell in self.grid_cells:
            half_width = self.cell_width / 2
            half_height = self.cell_height / 2
            if (cell['x'] - half_width <= x <= cell['x'] + half_width and
                cell['y'] - half_height <= y <= cell['y'] + half_height):
                return cell['index']
        return -1
        
    def set_hover(self, x: float, y: float):
        """Set hover state based on mouse position"""
        hovered_index = self.get_cell_at_position(x, y)
        
        for i, cell in enumerate(self.grid_cells):
            cell['hovered'] = (i == hovered_index)
            
        # Update selection if hovering
        if hovered_index >= 0 and hovered_index != self.selected_index:
            self.grid_cells[self.selected_index]['selected'] = False
            self.selected_index = hovered_index
            self.grid_cells[self.selected_index]['selected'] = True
            
    def get_selected_character(self) -> dict:
        """Get currently selected character"""
        return self.characters[self.selected_index]
        
    def draw(self):
        """Draw the character grid"""
        for cell in self.grid_cells:
            # Determine colors
            if cell['selected']:
                bg_color = arcade.color.CRIMSON
                border_width = 3
            elif cell['hovered']:
                bg_color = arcade.color.DARK_RED
                border_width = 2
            else:
                bg_color = arcade.color.DARK_GRAY
                border_width = 1
                
            # Draw cell background
            arcade.draw_rectangle_filled(
                cell['x'], cell['y'],
                self.cell_width, self.cell_height,
                bg_color
            )
            
            # Draw border
            arcade.draw_rectangle_outline(
                cell['x'], cell['y'],
                self.cell_width, self.cell_height,
                arcade.color.WHITE, border_width
            )
            
            # Draw character portrait (placeholder)
            portrait_size = 60
            char_color = cell['character'].get('color', (100, 100, 100))
            arcade.draw_rectangle_filled(
                cell['x'], cell['y'] + 20,
                portrait_size, portrait_size,
                char_color
            )
            arcade.draw_rectangle_outline(
                cell['x'], cell['y'] + 20,
                portrait_size, portrait_size,
                arcade.color.WHITE, 1
            )
            
            # Character initial
            char_name = cell['character'].get('name', 'Character')
            arcade.draw_text(
                char_name[0],
                cell['x'], cell['y'] + 20,
                arcade.color.WHITE,
                24,
                anchor_x="center",
                anchor_y="center"
            )
            
            # Character name
            arcade.draw_text(
                char_name.split()[0],  # First name only
                cell['x'], cell['y'] - 40,
                arcade.color.WHITE,
                12,
                anchor_x="center"
            )

class DetailedCharacterInfo:
    """Detailed character information panel"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 350
        self.height = 600
        self.character = None
        
    def set_character(self, character_data: dict):
        """Set the character to display"""
        self.character = character_data
        
    def draw(self):
        """Draw detailed character information"""
        # Background panel
        arcade.draw_rectangle_filled(
            self.x, self.y, self.width, self.height,
            arcade.color.DARK_BLUE_GRAY
        )
        arcade.draw_rectangle_outline(
            self.x, self.y, self.width, self.height,
            arcade.color.WHITE, 2
        )
        
        if not self.character:
            return
            
        # Large character portrait
        portrait_size = 150
        char_color = self.character.get('color', (100, 100, 100))
        arcade.draw_rectangle_filled(
            self.x, self.y + 200, portrait_size, portrait_size, char_color
        )
        arcade.draw_rectangle_outline(
            self.x, self.y + 200, portrait_size, portrait_size,
            arcade.color.WHITE, 3
        )
        
        # Character initial
        char_name = self.character.get('name', 'Character')
        arcade.draw_text(
            char_name[0],
            self.x, self.y + 200,
            arcade.color.WHITE,
            64,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Character name and title
        arcade.draw_text(
            char_name,
            self.x, self.y + 100,
            arcade.color.WHITE,
            24,
            anchor_x="center"
        )
        
        title = self.character.get('title', 'Fighter')
        arcade.draw_text(
            title,
            self.x, self.y + 70,
            arcade.color.YELLOW,
            16,
            anchor_x="center"
        )
        
        # Bio
        bio = self.character.get('bio', 'No description available')
        # Split long bio into multiple lines
        words = bio.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line + word) < 35:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
            
        bio_y = self.y + 30
        for i, line in enumerate(lines[:3]):  # Max 3 lines
            arcade.draw_text(
                line,
                self.x, bio_y - i * 20,
                arcade.color.LIGHT_GRAY,
                12,
                anchor_x="center"
            )
            
        # Stats with bars
        stat_y = self.y - 50
        stat_spacing = 40
        max_stat = 15  # For scaling bars
        
        stats = [
            ('Health', self.character.get('health', 100), 150),  # Different scale
            ('Speed', self.character.get('speed', 5), max_stat),
            ('Jump', self.character.get('jump_power', 15), max_stat),
            ('Attack', self.character.get('attack', 8), max_stat),
            ('Defense', self.character.get('defense', 6), max_stat)
        ]
        
        for i, (stat_name, value, scale) in enumerate(stats):
            y_pos = stat_y - i * stat_spacing
            
            # Stat name
            arcade.draw_text(
                f"{stat_name}:",
                self.x - 150, y_pos,
                arcade.color.WHITE,
                14
            )
            
            # Stat value
            display_value = value if stat_name != 'Health' else value
            arcade.draw_text(
                str(display_value),
                self.x + 120, y_pos,
                arcade.color.WHITE,
                14
            )
            
            # Stat bar
            bar_width = 100
            bar_height = 8
            fill_percentage = min(value / scale, 1.0)
            fill_width = bar_width * fill_percentage
            
            # Bar background
            arcade.draw_rectangle_filled(
                self.x + 20, y_pos,
                bar_width, bar_height,
                arcade.color.DARK_GRAY
            )
            
            # Bar fill
            if fill_width > 0:
                # Color based on stat level
                if fill_percentage > 0.7:
                    bar_color = arcade.color.GREEN
                elif fill_percentage > 0.4:
                    bar_color = arcade.color.YELLOW
                else:
                    bar_color = arcade.color.RED
                    
                arcade.draw_rectangle_filled(
                    self.x + 20 - bar_width/2 + fill_width/2, y_pos,
                    fill_width, bar_height,
                    bar_color
                )
                
        # Abilities
        ability_y = stat_y - 250
        arcade.draw_text(
            "Special Abilities:",
            self.x, ability_y,
            arcade.color.YELLOW,
            16,
            anchor_x="center"
        )
        
        abilities = self.character.get('abilities', [])
        for i, ability in enumerate(abilities[:4]):  # Show up to 4 abilities
            arcade.draw_text(
                f"• {ability}",
                self.x - 150, ability_y - 30 - i * 25,
                arcade.color.WHITE,
                12
            )

class CharacterSelectMenu(MenuState):
    """Character selection within a squad - FIXED save persistence and mouse support"""

    def __init__(self, director, input_manager, squad_data: dict):
        super().__init__(director, input_manager)
        self.squad_data = squad_data
        self.title = f"Select Character - {squad_data['name']}"
        self.scene_name = "character_select"
        
        # Flag for returning to lobby instead of gameplay
        self.return_to_lobby = False
        
        # Character grid
        self.character_grid = CharacterGrid(
            SCREEN_WIDTH // 2 + 100,
            SCREEN_HEIGHT // 2 + 100,
            squad_data['members']
        )
        
        # Detailed character info
        self.character_info = DetailedCharacterInfo(200, SCREEN_HEIGHT // 2)
        self.character_info.set_character(squad_data['members'][0])
        
    def on_enter(self):
        """Setup character select controls"""
        super().on_enter()
        
        # Clear default menu navigation
        self.input_manager.clear_scene_callbacks(self.scene_name)
        
        # Add grid navigation
        self.input_manager.register_action_callback(
            InputAction.MENU_UP, lambda: self.navigate_grid('up'), self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_DOWN, lambda: self.navigate_grid('down'), self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_LEFT, lambda: self.navigate_grid('left'), self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_RIGHT, lambda: self.navigate_grid('right'), self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.SELECT, self.select_character, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.BACK, self.go_back, self.scene_name
        )
        
    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse motion"""
        # Update grid hover
        self.character_grid.set_hover(x, y)
        
        # Update character info based on hover
        selected_char = self.character_grid.get_selected_character()
        self.character_info.set_character(selected_char)
        
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse click"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Check if clicking on a character cell
            clicked_index = self.character_grid.get_cell_at_position(x, y)
            if clicked_index >= 0:
                # If clicking on already selected character, confirm selection
                if clicked_index == self.character_grid.selected_index:
                    self.select_character()
                # Otherwise just select it (already done by hover)
                    
    def navigate_grid(self, direction: str):
        """Navigate character grid"""
        self.character_grid.move_selection(direction)
        selected_char = self.character_grid.get_selected_character()
        self.character_info.set_character(selected_char)
        
    def select_character(self):
        """Confirm character selection - FIXED to go to chapter select"""
        selected_char = self.character_grid.get_selected_character()
        
        # FIXED: Ensure proper saving to save manager
        save_manager = self.director.get_system('save_manager')
        if save_manager and save_manager.current_save:
            # Save both squad and character data correctly
            save_manager.current_save.game_data['selected_squad'] = self.squad_data['id']
            save_manager.current_save.game_data['selected_character'] = selected_char['id']
            
            print(f"✓ Character selected: {selected_char['name']} ({selected_char['id']})")
            print(f"✓ Squad selected: {self.squad_data['name']} ({self.squad_data['id']})")
            
            # Force save to ensure persistence
            save_manager.save_game(1)
        else:
            print("ERROR: No save manager or save data available!")
            
        # Check where to go next
        if self.return_to_lobby:
            # Return to lobby with updated character
            self.director.pop_scene()  # Go back to lobby
        else:
            # Check for pending lobby join (Join Game flow)
            game_instance = self.director.get_system('game_instance')
            if game_instance and game_instance.pending_lobby_join:
                # Complete join game flow
                game_instance.complete_join_game_flow()
            else:
                # FIXED: Go to chapter selection instead of game mode
                self.director.change_scene('chapter_select')
            
    def draw(self):
        """Draw character selection screen"""
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
            28,
            anchor_x="center"
        )
        
        # Draw character grid
        self.character_grid.draw()
        
        # Draw character info
        self.character_info.draw()
        
        # Instructions
        instruction_text = "Use Arrow Keys or Mouse to select, ENTER/Click to confirm, ESC to go back"
        if self.return_to_lobby:
            instruction_text = "Select character for lobby, ENTER/Click to confirm, ESC to return"
            
        arcade.draw_text(
            instruction_text,
            SCREEN_WIDTH // 2,
            40,
            arcade.color.WHITE,
            14,
            anchor_x="center"
        )