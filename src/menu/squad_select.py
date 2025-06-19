# Fixed SquadSelectMenu with proper ESC handling

import arcade
import json
from src.menu.menu_state import MenuState
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.input.input_manager import InputAction

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
            anchor_x="center",
            font_name="Arial",
            bold=True
        )
        
        # Draw squad preview (3x2 grid of character icons)
        icon_size = 50
        spacing = 5
        start_x = self.x - icon_size - spacing/2
        start_y = self.y - 20
        
        for i, member in enumerate(self.data['members'][:6]):
            row = i // 2
            col = i % 2
            icon_x = start_x + col * (icon_size + spacing)
            icon_y = start_y - row * (icon_size + spacing)
            
            # Draw character icon placeholder
            arcade.draw_rectangle_filled(
                icon_x, icon_y, icon_size, icon_size,
                arcade.color.DARK_BLUE_GRAY
            )
            arcade.draw_text(
                member['name'][:3],
                icon_x, icon_y,
                arcade.color.WHITE,
                10,
                anchor_x="center",
                anchor_y="center"
            )

class CharacterInfo:
    """Character information panel"""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 300
        self.height = 600
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
                "Select a character",
                self.x, self.y,
                arcade.color.WHITE,
                16,
                anchor_x="center",
                anchor_y="center"
            )
            return
            
        # Character portrait placeholder
        portrait_size = 128
        arcade.draw_rectangle_filled(
            self.x, self.y + 200, portrait_size, portrait_size,
            arcade.color.DARK_GRAY
        )
        
        # Character name
        arcade.draw_text(
            self.character['name'],
            self.x, self.y + 100,
            arcade.color.WHITE,
            24,
            anchor_x="center",
            font_name="Arial",
            bold=True
        )
        
        # Stats
        stat_y = self.y
        stat_spacing = 40
        
        stats = [
            f"Health: {self.character.get('health', 100)}",
            f"Speed: {self.character.get('speed', 5)}",
            f"Jump: {self.character.get('jump_power', 15)}"
        ]
        
        for i, stat in enumerate(stats):
            arcade.draw_text(
                stat,
                self.x - 100, stat_y - i * stat_spacing,
                arcade.color.WHITE,
                16,
                font_name="Arial"
            )
            
        # Abilities
        ability_y = stat_y - 150
        arcade.draw_text(
            "Abilities:",
            self.x - 100, ability_y,
            arcade.color.YELLOW,
            18,
            font_name="Arial",
            bold=True
        )
        
        for i, ability in enumerate(self.character.get('abilities', [])):
            arcade.draw_text(
                f"• {ability}",
                self.x - 90, ability_y - 30 - i * 25,
                arcade.color.WHITE,
                14,
                font_name="Arial"
            )

class SquadSelectMenu(MenuState):
    """Squad selection menu with character grid"""
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Select Your Squad"
        
        # Load squad data
        self.squads = self.load_squads()
        self.squad_cards = []
        self.selected_squad_index = 0
        self.selected_character_index = 0
        
        # Character info panel
        self.character_info = CharacterInfo(150, 360)
        
        # Character grid for selected squad
        self.character_grid = []
        self.showing_character_select = False
        
        # Create squad cards
        self.create_squad_cards()
        
        # Clear default menu items since we handle our own navigation
        self.menu_items = []
        
    def load_squads(self):
        """Load squad data from configuration"""
        # Default squad data for testing
        return [
            {
                'id': 'squad_alpha',
                'name': 'Squad Alpha',
                'members': [
                    {'name': 'Ruka', 'health': 100, 'speed': 6, 'jump_power': 15,
                     'abilities': ['Double Jump', 'Dash Attack']},
                    {'name': 'Yuki', 'health': 80, 'speed': 8, 'jump_power': 18,
                     'abilities': ['Air Dash', 'Quick Strike']},
                    {'name': 'Karen', 'health': 120, 'speed': 4, 'jump_power': 12,
                     'abilities': ['Shield Bash', 'Ground Pound']},
                    {'name': 'Tsukasa', 'health': 90, 'speed': 7, 'jump_power': 16,
                     'abilities': ['Teleport', 'Energy Blast']},
                    {'name': 'Megumi', 'health': 85, 'speed': 7, 'jump_power': 17,
                     'abilities': ['Healing Aura', 'Light Beam']},
                    {'name': 'Ichigo', 'health': 95, 'speed': 6, 'jump_power': 15,
                     'abilities': ['Fire Ball', 'Flame Dash']}
                ]
            },
            {
                'id': 'squad_bravo',
                'name': 'Squad Bravo',
                'members': [
                    {'name': 'Seika', 'health': 110, 'speed': 5, 'jump_power': 14,
                     'abilities': ['Ice Wall', 'Freeze Ray']},
                    {'name': 'Mion', 'health': 85, 'speed': 9, 'jump_power': 16,
                     'abilities': ['Shadow Step', 'Smoke Bomb']},
                    {'name': 'Aoi', 'health': 100, 'speed': 6, 'jump_power': 15,
                     'abilities': ['Thunder Strike', 'Electric Field']},
                    {'name': 'Sumire', 'health': 90, 'speed': 7, 'jump_power': 17,
                     'abilities': ['Wind Slash', 'Tornado']},
                    {'name': 'Kura', 'health': 95, 'speed': 6, 'jump_power': 15,
                     'abilities': ['Rock Throw', 'Earth Quake']},
                    {'name': 'Maria', 'health': 80, 'speed': 8, 'jump_power': 18,
                     'abilities': ['Time Slow', 'Blink']}
                ]
            }
        ]
        
    def create_squad_cards(self):
        """Create squad card visuals"""
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
            self.squad_cards.append(card)
            
    def register_input_callbacks(self):
        """Override to register squad-specific controls"""
        super().register_input_callbacks()
        
        # Clear default left/right (we'll handle them ourselves)
        self.input_manager.clear_callbacks_for_action(InputAction.MENU_LEFT)
        self.input_manager.clear_callbacks_for_action(InputAction.MENU_RIGHT)
        
        # Register squad navigation
        self.input_manager.register_action_callback(
            InputAction.MENU_LEFT, self.select_previous_squad
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_RIGHT, self.select_next_squad
        )
        
    def select_previous_squad(self):
        """Select previous squad"""
        if not self.showing_character_select:
            self.squad_cards[self.selected_squad_index].is_selected = False
            self.selected_squad_index = (self.selected_squad_index - 1) % len(self.squad_cards)
            self.squad_cards[self.selected_squad_index].is_selected = True
            
    def select_next_squad(self):
        """Select next squad"""
        if not self.showing_character_select:
            self.squad_cards[self.selected_squad_index].is_selected = False
            self.selected_squad_index = (self.selected_squad_index + 1) % len(self.squad_cards)
            self.squad_cards[self.selected_squad_index].is_selected = True
            
    def select_item(self):
        """Override to handle squad selection"""
        if not self.showing_character_select:
            # Enter character selection for this squad
            self.showing_character_select = True
            squad = self.squads[self.selected_squad_index]
            self.character_info.set_character(squad['members'][0])
        else:
            # Character selected, create character select menu
            squad = self.squads[self.selected_squad_index]
            from src.menu.character_select import CharacterSelectMenu
            char_select = CharacterSelectMenu(
                self.director, 
                self.input_manager,
                squad
            )
            self.director.register_scene("character_select", char_select)
            self.director.push_scene("character_select")
            
    def go_back(self):
        """Override to handle custom back behavior"""
        if self.showing_character_select:
            # Exit character selection mode
            self.showing_character_select = False
        else:
            # Go back to main menu
            super().go_back()
            
    def draw(self):
        """Draw squad selection screen"""
        arcade.start_render()
        
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
            anchor_x="center",
            font_name="Arial",
            bold=True
        )
        
        # Draw squad cards
        for card in self.squad_cards:
            card.draw()
            
        # Draw character info panel
        self.character_info.draw()
        
        # Draw instructions
        instruction = "Use LEFT/RIGHT to select squad, ENTER to confirm, ESC to go back"
        if self.showing_character_select:
            instruction = "Character selection mode - ENTER to proceed, ESC to go back"
            
        arcade.draw_text(
            instruction,
            SCREEN_WIDTH // 2,
            50,
            arcade.color.WHITE,
            16,
            anchor_x="center"
        )