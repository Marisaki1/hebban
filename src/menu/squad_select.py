# src/menu/squad_select.py - Fixed for Arcade 3.0
import arcade
import json
from src.menu.menu_state import MenuState
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.input.input_manager import InputAction

class SquadCard:
    """Visual representation of a squad with mouse support - Arcade 3.0 compatible"""
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
        """Draw the squad card using Arcade 3.0 functions"""
        try:
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
                font_name="Arial"
            )
            
            # Draw squad preview (3x2 grid of character icons)
            icon_size = 50
            spacing = 5
            start_x = self.x - icon_size - spacing/2
            start_y = self.y - 20
            
            members = self.data.get('members', [])
            for i, member in enumerate(members[:6]):  # Show up to 6 members
                row = i // 2
                col = i % 2
                icon_x = start_x + col * (icon_size + spacing)
                icon_y = start_y - row * (icon_size + spacing)
                
                # Draw character icon placeholder
                arcade.draw_rectangle_filled(
                    icon_x, icon_y, icon_size, icon_size,
                    arcade.color.DARK_BLUE_GRAY
                )
                arcade.draw_rectangle_outline(
                    icon_x, icon_y, icon_size, icon_size,
                    arcade.color.LIGHT_GRAY, 1
                )
                
                # Draw character name abbreviation
                char_name = member.get('name', f'M{i+1}')
                arcade.draw_text(
                    char_name[:3],
                    icon_x, icon_y,
                    arcade.color.WHITE,
                    10,
                    anchor_x="center",
                    anchor_y="center"
                )
                
            # Draw squad description
            description = self.data.get('description', 'Squad description')
            # Wrap long descriptions
            if len(description) > 30:
                description = description[:27] + "..."
                
            arcade.draw_text(
                description,
                self.x, self.y - 110,
                arcade.color.LIGHT_GRAY,
                12,
                anchor_x="center"
            )
            
        except Exception as e:
            print(f"Error drawing squad card: {e}")
            # Fallback simple card
            arcade.draw_rectangle_filled(
                self.x, self.y, self.width, self.height, arcade.color.DARK_GRAY
            )
            arcade.draw_text(
                self.data.get('name', 'Squad'),
                self.x, self.y,
                arcade.color.WHITE,
                16,
                anchor_x="center",
                anchor_y="center"
            )

class CharacterInfo:
    """Character information panel - Arcade 3.0 compatible"""
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
        """Draw character information using Arcade 3.0 functions"""
        try:
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
                
            # Character portrait placeholder
            portrait_size = 128
            arcade.draw_rectangle_filled(
                self.x, self.y + 200, portrait_size, portrait_size,
                arcade.color.DARK_GRAY
            )
            arcade.draw_rectangle_outline(
                self.x, self.y + 200, portrait_size, portrait_size,
                arcade.color.LIGHT_GRAY, 1
            )
            
            # Character initial
            char_name = self.character.get('name', 'Character')
            arcade.draw_text(
                char_name[0],
                self.x, self.y + 200,
                arcade.color.WHITE,
                48,
                anchor_x="center",
                anchor_y="center"
            )
            
            # Character name
            arcade.draw_text(
                char_name,
                self.x, self.y + 100,
                arcade.color.WHITE,
                24,
                anchor_x="center"
            )
            
            # Character title/role
            title = self.character.get('title', 'Fighter')
            arcade.draw_text(
                title,
                self.x, self.y + 70,
                arcade.color.YELLOW,
                16,
                anchor_x="center"
            )
            
            # Stats
            stat_y = self.y
            stat_spacing = 30
            
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
                    self.x - 100, stat_y - i * stat_spacing,
                    arcade.color.WHITE,
                    14
                )
                
            # Abilities
            ability_y = stat_y - 180
            arcade.draw_text(
                "Abilities:",
                self.x - 100, ability_y,
                arcade.color.YELLOW,
                16
            )
            
            abilities = self.character.get('abilities', [])
            for i, ability in enumerate(abilities[:3]):  # Show up to 3 abilities
                ability_text = ability if isinstance(ability, str) else str(ability)
                arcade.draw_text(
                    f"• {ability_text}",
                    self.x - 90, ability_y - 25 - i * 20,
                    arcade.color.WHITE,
                    12
                )
                
        except Exception as e:
            print(f"Error drawing character info: {e}")

class SquadSelectMenu(MenuState):
    """Squad selection menu with character grid and proper navigation - Arcade 3.0 compatible"""
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Select Your Squad"
        self.scene_name = "squad_select"
        
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
        
        # Track input state
        self.input_cooldown = 0
        
    def load_squads(self):
        """Load squad data from configuration"""
        try:
            from src.data.squad_data import get_all_squads
            squads = get_all_squads()
            
            # Preload sprites for all squads
            try:
                from src.core.sprite_manager import sprite_manager
                for squad in squads:
                    member_ids = [member['id'] for member in squad['members']]
                    sprite_manager.preload_squad_sprites(member_ids)
            except Exception as e:
                print(f"Error preloading sprites: {e}")
            
            return squads
        except Exception as e:
            print(f"Error loading squads: {e}")
            # Return default squads
            return self._get_default_squads()
        
    def _get_default_squads(self):
        """Get default squads if loading fails"""
        return [
            {
                'id': '31A',
                'name': '31A Squad',
                'description': 'Elite combat unit',
                'members': [
                    {'id': 'ruka', 'name': 'Ruka', 'health': 100, 'speed': 6, 'jump_power': 15, 'attack': 8, 'defense': 6, 'abilities': ['Double Jump', 'Dash Attack']},
                    {'id': 'yuki', 'name': 'Yuki', 'health': 80, 'speed': 8, 'jump_power': 18, 'attack': 6, 'defense': 4, 'abilities': ['Air Dash', 'Quick Strike']},
                ]
            }
        ]
        
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
        """Override to setup squad-specific controls"""
        # Call parent to set up basic navigation
        super().on_enter()
        
        # Clear and re-register our specific controls
        self.input_manager.clear_scene_callbacks(self.scene_name)
        
        # Navigation callbacks
        self.input_manager.register_action_callback(
            InputAction.MENU_LEFT, self.select_previous_squad, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_RIGHT, self.select_next_squad, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.SELECT, self.select_item, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.BACK, self.go_back, self.scene_name
        )
        
    def update(self, delta_time: float):
        """Update squad select state"""
        super().update(delta_time)
        if self.input_cooldown > 0:
            self.input_cooldown -= delta_time
        
    def select_previous_squad(self):
        """Select previous squad"""
        if not self.showing_character_select and self.input_cooldown <= 0 and self.squad_cards:
            self.input_cooldown = 0.2  # Prevent rapid switching
            self.squad_cards[self.selected_squad_index].is_selected = False
            self.selected_squad_index = (self.selected_squad_index - 1) % len(self.squad_cards)
            self.squad_cards[self.selected_squad_index].is_selected = True
            
            # Update character info to show first character of new squad
            squad = self.squads[self.selected_squad_index]
            if squad.get('members'):
                self.character_info.set_character(squad['members'][0])
            
    def select_next_squad(self):
        """Select next squad"""
        if not self.showing_character_select and self.input_cooldown <= 0 and self.squad_cards:
            self.input_cooldown = 0.2  # Prevent rapid switching
            self.squad_cards[self.selected_squad_index].is_selected = False
            self.selected_squad_index = (self.selected_squad_index + 1) % len(self.squad_cards)
            self.squad_cards[self.selected_squad_index].is_selected = True
            
            # Update character info to show first character of new squad
            squad = self.squads[self.selected_squad_index]
            if squad.get('members'):
                self.character_info.set_character(squad['members'][0])
            
    def select_item(self):
        """Override to handle squad selection"""
        if self.input_cooldown <= 0:
            self.input_cooldown = 0.2
            if not self.showing_character_select:
                # Go to character selection
                try:
                    from src.menu.character_select import CharacterSelectMenu
                    squad = self.squads[self.selected_squad_index]
                    char_select = CharacterSelectMenu(
                        self.director, 
                        self.input_manager,
                        squad
                    )
                    self.director.register_scene("character_select", char_select)
                    self.director.push_scene("character_select")
                except Exception as e:
                    print(f"Error creating character select: {e}")
                    # Fallback - go directly to gameplay
                    try:
                        # Save selected squad
                        save_manager = self.director.get_system('save_manager')
                        if save_manager and save_manager.current_save:
                            squad = self.squads[self.selected_squad_index]
                            save_manager.current_save.game_data['selected_squad'] = squad['id']
                            if squad.get('members'):
                                save_manager.current_save.game_data['selected_character'] = squad['members'][0]['id']
                        
                        self.director.change_scene('gameplay')
                    except Exception as e2:
                        print(f"Fallback failed: {e2}")
                
    def go_back(self):
        """Override to handle going back properly"""
        if self.input_cooldown <= 0:
            self.input_cooldown = 0.2
            if self.showing_character_select:
                self.showing_character_select = False
            else:
                self.director.pop_scene()
                
    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse hover over squad cards"""
        for card in self.squad_cards:
            card.is_hovered = card.contains_point(x, y)
            
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse click on squad cards"""
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
                        # If already selected, proceed to character selection
                        self.select_item()
                    break
            
    def draw(self):
        """Draw squad selection screen - Arcade 3.0 Compatible"""
        try:
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
                16,
                anchor_x="center"
            )
            
        except Exception as e:
            print(f"Error drawing squad select: {e}")
            # Fallback drawing
            arcade.draw_text(
                "Squad Selection (Error in drawing)",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                arcade.color.WHITE,
                24,
                anchor_x="center",
                anchor_y="center"
            )