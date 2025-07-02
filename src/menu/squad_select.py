"""
Squad selection menu
"""

import arcade
from src.menu.menu_state import MenuState
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.input.input_manager import InputAction
from src.data.squad_data import get_all_squads

class SquadCard:
    """Visual representation of a squad"""
    
    def __init__(self, squad_data: dict, x: float, y: float, index: int):
        self.data = squad_data
        self.x = x
        self.y = y
        self.index = index
        self.width = 200
        self.height = 280
        self.is_selected = False
        self.is_hovered = False
        
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is within card bounds"""
        half_width = self.width / 2
        half_height = self.height / 2
        return (self.x - half_width <= x <= self.x + half_width and
                self.y - half_height <= y <= self.y + half_height)
                
    def draw(self):
        """Draw the squad card"""
        # Card background
        if self.is_selected:
            color = arcade.color.CRIMSON
            border_width = 4
        elif self.is_hovered:
            color = arcade.color.DARK_RED
            border_width = 2
        else:
            color = arcade.color.DARK_GRAY
            border_width = 1
            
        # Draw card
        arcade.draw_rectangle_filled(
            self.x, self.y, self.width, self.height, color
        )
        arcade.draw_rectangle_outline(
            self.x, self.y, self.width, self.height,
            arcade.color.WHITE, border_width
        )
        
        # Draw squad name
        arcade.draw_text(
            self.data['name'],
            self.x, self.y + 100,
            arcade.color.WHITE,
            20,
            anchor_x="center"
        )
        
        # Draw character icons (3x2 grid)
        icon_size = 40
        spacing = 5
        start_x = self.x - icon_size - spacing/2
        start_y = self.y + 20
        
        members = self.data.get('members', [])
        for i, member in enumerate(members[:6]):  # Show up to 6 members
            row = i // 2
            col = i % 2
            icon_x = start_x + col * (icon_size + spacing)
            icon_y = start_y - row * (icon_size + spacing)
            
            # Character icon background
            char_color = member.get('color', (100, 100, 100))
            arcade.draw_rectangle_filled(
                icon_x, icon_y, icon_size, icon_size, char_color
            )
            arcade.draw_rectangle_outline(
                icon_x, icon_y, icon_size, icon_size,
                arcade.color.WHITE, 1
            )
            
            # Character name initial
            char_name = member.get('name', f'M{i+1}')
            arcade.draw_text(
                char_name[0],
                icon_x, icon_y,
                arcade.color.WHITE,
                16,
                anchor_x="center",
                anchor_y="center"
            )
            
        # Draw squad description
        description = self.data.get('description', 'Squad description')
        if len(description) > 35:
            description = description[:32] + "..."
            
        arcade.draw_text(
            description,
            self.x, self.y - 100,
            arcade.color.LIGHT_GRAY,
            12,
            anchor_x="center"
        )

class CharacterInfo:
    """Character information panel"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 300
        self.height = 500
        self.character = None
        
    def set_character(self, character_data: dict):
        """Set the character to display"""
        self.character = character_data
        
    def draw(self):
        """Draw character information"""
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
            arcade.draw_text(
                "Select a squad",
                self.x, self.y,
                arcade.color.WHITE,
                16,
                anchor_x="center",
                anchor_y="center"
            )
            return
            
        # Character portrait (placeholder)
        portrait_size = 100
        char_color = self.character.get('color', (100, 100, 100))
        arcade.draw_rectangle_filled(
            self.x, self.y + 150, portrait_size, portrait_size, char_color
        )
        arcade.draw_rectangle_outline(
            self.x, self.y + 150, portrait_size, portrait_size,
            arcade.color.WHITE, 2
        )
        
        # Character initial
        char_name = self.character.get('name', 'Character')
        arcade.draw_text(
            char_name[0],
            self.x, self.y + 150,
            arcade.color.WHITE,
            48,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Character name and title
        arcade.draw_text(
            char_name,
            self.x, self.y + 80,
            arcade.color.WHITE,
            20,
            anchor_x="center"
        )
        
        title = self.character.get('title', 'Fighter')
        arcade.draw_text(
            title,
            self.x, self.y + 50,
            arcade.color.YELLOW,
            14,
            anchor_x="center"
        )
        
        # Stats
        stat_y = self.y
        stats = [
            f"Health: {self.character.get('health', 100)}",
            f"Speed: {self.character.get('speed', 5)}",
            f"Jump: {self.character.get('jump_power', 15)}",
            f"Attack: {self.character.get('attack', 8)}",
            f"Defense: {self.character.get('defense', 6)}"
        ]
        
        for i, stat in enumerate(stats):
            arcade.draw_text(
                stat,
                self.x - 100, stat_y - i * 25,
                arcade.color.WHITE,
                12
            )
            
        # Abilities
        ability_y = stat_y - 150
        arcade.draw_text(
            "Abilities:",
            self.x - 100, ability_y,
            arcade.color.YELLOW,
            14
        )
        
        abilities = self.character.get('abilities', [])
        for i, ability in enumerate(abilities[:3]):
            arcade.draw_text(
                f"• {ability}",
                self.x - 90, ability_y - 25 - i * 20,
                arcade.color.WHITE,
                10
            )

class SquadSelectMenu(MenuState):
    """Squad selection menu"""
    
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Select Your Squad"
        self.scene_name = "squad_select"
        
        # Load squad data
        self.squads = get_all_squads()
        self.squad_cards = []
        self.selected_squad_index = 0
        
        # Character info panel
        self.character_info = CharacterInfo(150, 360)
        
        # Create squad cards
        self.create_squad_cards()
        
    def create_squad_cards(self):
        """Create squad card visuals"""
        if not self.squads:
            return
            
        card_spacing = 250
        start_x = SCREEN_WIDTH // 2 - (len(self.squads) - 1) * card_spacing // 2
        
        for i, squad in enumerate(self.squads):
            card = SquadCard(
                squad,
                start_x + i * card_spacing,
                400,
                i
            )
            if i == 0:
                card.is_selected = True
                # Show first character of first squad
                if squad.get('members'):
                    self.character_info.set_character(squad['members'][0])
            self.squad_cards.append(card)
            
    def on_enter(self):
        """Setup squad-specific controls"""
        super().on_enter()
        
        # Clear and re-register specific controls
        self.input_manager.clear_scene_callbacks(self.scene_name)
        
        self.input_manager.register_action_callback(
            InputAction.MENU_LEFT, self.select_previous_squad, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_RIGHT, self.select_next_squad, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.SELECT, self.select_squad, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.BACK, self.go_back, self.scene_name
        )
        
    def select_previous_squad(self):
        """Select previous squad"""
        if self.squad_cards:
            self.squad_cards[self.selected_squad_index].is_selected = False
            self.selected_squad_index = (self.selected_squad_index - 1) % len(self.squad_cards)
            self.squad_cards[self.selected_squad_index].is_selected = True
            
            # Update character info
            squad = self.squads[self.selected_squad_index]
            if squad.get('members'):
                self.character_info.set_character(squad['members'][0])
                
    def select_next_squad(self):
        """Select next squad"""
        if self.squad_cards:
            self.squad_cards[self.selected_squad_index].is_selected = False
            self.selected_squad_index = (self.selected_squad_index + 1) % len(self.squad_cards)
            self.squad_cards[self.selected_squad_index].is_selected = True
            
            # Update character info
            squad = self.squads[self.selected_squad_index]
            if squad.get('members'):
                self.character_info.set_character(squad['members'][0])
                
    def select_squad(self):
        """Select current squad and go to character selection"""
        squad = self.squads[self.selected_squad_index]
        
        # Create and register character select menu
        from src.menu.character_select import CharacterSelectMenu
        char_select = CharacterSelectMenu(self.director, self.input_manager, squad)
        self.director.register_scene("character_select", char_select)
        self.director.push_scene("character_select")
        
    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse hover"""
        for card in self.squad_cards:
            card.is_hovered = card.contains_point(x, y)
            
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse click"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            for i, card in enumerate(self.squad_cards):
                if card.contains_point(x, y):
                    # Select this squad
                    if self.selected_squad_index != i:
                        self.squad_cards[self.selected_squad_index].is_selected = False
                        self.selected_squad_index = i
                        card.is_selected = True
                        
                        # Update character info
                        squad = self.squads[self.selected_squad_index]
                        if squad.get('members'):
                            self.character_info.set_character(squad['members'][0])
                    else:
                        # If already selected, proceed
                        self.select_squad()
                    break
                    
    def draw(self):
        """Draw squad selection screen"""
        # Draw background
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            (20, 20, 20)
        )
        
        # Draw title
        arcade.draw_text(
            self.title,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 80,
            arcade.color.CRIMSON,
            36,
            anchor_x="center"
        )
        
        # Draw squad cards
        for card in self.squad_cards:
            card.draw()
            
        # Draw character info panel
        self.character_info.draw()
        
        # Draw instructions
        arcade.draw_text(
            "Use LEFT/RIGHT to select squad, ENTER to confirm, ESC to go back",
            SCREEN_WIDTH // 2,
            50,
            arcade.color.WHITE,
            14,
            anchor_x="center"
        )