# ============================================================================
# FILE: src/menu/character_select.py
# ============================================================================
class CharacterGrid:
    """3x2 character selection grid"""
    def __init__(self, x: float, y: float, characters: List[dict]):
        self.x = x
        self.y = y
        self.characters = characters
        self.selected_index = 0
        self.cell_width = 150
        self.cell_height = 180
        self.spacing = 20
        self.grid_cells = []
        self._create_grid()
        
    def _create_grid(self):
        """Create grid cells for characters"""
        for i, char in enumerate(self.characters[:6]):
            row = i // 3
            col = i % 3
            
            cell_x = self.x + col * (self.cell_width + self.spacing)
            cell_y = self.y - row * (self.cell_height + self.spacing)
            
            self.grid_cells.append({
                'character': char,
                'x': cell_x,
                'y': cell_y,
                'index': i,
                'selected': i == 0
            })
            
    def move_selection(self, direction: str):
        """Move selection in grid"""
        old_index = self.selected_index
        
        if direction == 'up' and self.selected_index >= 3:
            self.selected_index -= 3
        elif direction == 'down' and self.selected_index < 3:
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
            
    def get_selected_character(self) -> dict:
        """Get currently selected character"""
        return self.characters[self.selected_index]
        
    def draw(self):
        """Draw the character grid"""
        for cell in self.grid_cells:
            # Draw cell background
            color = arcade.color.CRIMSON if cell['selected'] else arcade.color.DARK_GRAY
            arcade.draw_rectangle_filled(
                cell['x'], cell['y'], 
                self.cell_width, self.cell_height, 
                color
            )
            
            # Draw border
            border_color = arcade.color.WHITE if cell['selected'] else arcade.color.GRAY
            border_width = 3 if cell['selected'] else 1
            arcade.draw_rectangle_outline(
                cell['x'], cell['y'],
                self.cell_width, self.cell_height,
                border_color, border_width
            )
            
            # Draw character portrait placeholder
            portrait_size = 80
            arcade.draw_rectangle_filled(
                cell['x'], cell['y'] + 20,
                portrait_size, portrait_size,
                arcade.color.DARK_BLUE_GRAY
            )
            
            # Draw character name
            arcade.draw_text(
                cell['character']['name'],
                cell['x'], cell['y'] - 60,
                arcade.color.WHITE,
                14,
                anchor_x="center",
                font_name="Arial"
            )

class CharacterSelectMenu(MenuState):
    """Detailed character selection within a squad"""
    def __init__(self, director, input_manager, squad_data: dict):
        super().__init__(director, input_manager)
        self.squad_data = squad_data
        self.title = f"Select Character - {squad_data['name']}"
        
        # Character grid
        self.character_grid = CharacterGrid(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 2 + 50,
            squad_data['members']
        )
        
        # Character info panel
        self.character_info = CharacterInfo(150, SCREEN_HEIGHT // 2)
        self.character_info.set_character(squad_data['members'][0])
        
        # Confirmation state
        self.character_confirmed = False
        
    def on_enter(self):
        """Setup character select specific controls"""
        super().on_enter()
        
        # Remove default menu navigation
        self.input_manager.action_callbacks[InputAction.MENU_UP].clear()
        self.input_manager.action_callbacks[InputAction.MENU_DOWN].clear()
        
        # Add grid navigation
        self.input_manager.register_action_callback(
            InputAction.MENU_UP, lambda: self.navigate_grid('up')
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_DOWN, lambda: self.navigate_grid('down')
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_LEFT, lambda: self.navigate_grid('left')
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_RIGHT, lambda: self.navigate_grid('right')
        )
        
    def navigate_grid(self, direction: str):
        """Navigate character grid"""
        self.character_grid.move_selection(direction)
        selected_char = self.character_grid.get_selected_character()
        self.character_info.set_character(selected_char)
        
    def select_item(self):
        """Confirm character selection"""
        if not self.character_confirmed:
            self.character_confirmed = True
            selected_char = self.character_grid.get_selected_character()
            
            # Save selection
            save_manager = self.director.get_system('save_manager')
            if save_manager.current_save:
                save_manager.current_save.game_data['selected_squad'] = self.squad_data['id']
                save_manager.current_save.game_data['selected_character'] = selected_char['id']
                
            # Proceed to lobby or game
            if self.director.get_system('is_multiplayer'):
                self.director.change_scene('lobby_menu')
            else:
                self.director.change_scene('gameplay')
                
    def draw(self):
        """Draw character selection screen"""
        arcade.start_render()
        
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
            anchor_x="center",
            font_name="Arial",
            bold=True
        )
        
        # Draw character grid
        self.character_grid.draw()
        
        # Draw character info
        self.character_info.draw()
        
        # Instructions
        instruction_text = "Press ENTER to confirm" if not self.character_confirmed else "Character confirmed!"
        arcade.draw_text(
            instruction_text,
            SCREEN_WIDTH // 2,
            40,
            arcade.color.WHITE,
            16,
            anchor_x="center"
        )
