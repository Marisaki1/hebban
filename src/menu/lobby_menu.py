"""
Fixed multiplayer lobby menu with proper join functionality
"""

import arcade
import random
import string
from src.menu.menu_state import MenuState, MenuItem
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.input.input_manager import InputAction

class LobbyCodeInput:
    """Lobby code input widget"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 300
        self.height = 50
        self.code = ""
        self.max_length = 6
        self.active = False
        self.cursor_timer = 0
        
    def is_valid_code(self) -> bool:
        """Check if code is valid format"""
        return len(self.code) == self.max_length and self.code.isalnum()
        
    def add_character(self, char: str):
        """Add character to code"""
        if len(self.code) < self.max_length and char.isalnum():
            self.code += char.upper()
            
    def remove_character(self):
        """Remove last character"""
        if self.code:
            self.code = self.code[:-1]
            
    def clear(self):
        """Clear the code"""
        self.code = ""
        
    def update(self, delta_time: float):
        """Update cursor animation"""
        self.cursor_timer += delta_time
        
    def draw(self):
        """Draw the input field"""
        # Background
        bg_color = arcade.color.DARK_BLUE_GRAY if self.active else arcade.color.DARK_GRAY
        arcade.draw_rectangle_filled(
            self.x, self.y, self.width, self.height, bg_color
        )
        
        # Border
        border_color = arcade.color.CRIMSON if self.active else arcade.color.WHITE
        border_width = 3 if self.active else 1
        arcade.draw_rectangle_outline(
            self.x, self.y, self.width, self.height, border_color, border_width
        )
        
        # Text
        display_text = self.code
        if self.active and self.cursor_timer % 1.0 < 0.5:
            display_text += "_"
            
        arcade.draw_text(
            display_text or "Enter Code",
            self.x, self.y,
            arcade.color.WHITE if self.code else arcade.color.GRAY,
            24,
            anchor_x="center",
            anchor_y="center"
        )

class LobbyMenu(MenuState):
    """Fixed multiplayer lobby menu"""
    
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Multiplayer Lobby"
        self.scene_name = "lobby"
        
        # Lobby state
        self.mode = "browser"  # "browser", "host", "join", "in_lobby"
        self.is_host = False
        self.lobby_code = None
        self.connected_players = []
        self.max_players = 8
        self.ready_states = {}
        self.game_started = False
        
        # UI elements
        self.lobby_code_input = LobbyCodeInput(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Setup initial state
        self.setup_browser_menu()
        
    def set_join_mode(self):
        """Set lobby to join mode"""
        self.mode = "join"
        self.setup_join_mode()
        
    def setup_browser_menu(self):
        """Setup initial lobby browser menu"""
        self.mode = "browser"
        menu_y_start = 400
        menu_spacing = 70
        
        self.menu_items = [
            MenuItem(
                "Host Lobby",
                self.host_lobby,
                SCREEN_WIDTH // 2,
                menu_y_start
            ),
            MenuItem(
                "Join with Code",
                self.show_join_input,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing
            ),
            MenuItem(
                "Quick Match",
                self.quick_match,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing * 2
            ),
            MenuItem(
                "Back",
                self.go_back,
                SCREEN_WIDTH // 2,
                menu_y_start - menu_spacing * 3
            )
        ]
        
        if self.menu_items:
            self.menu_items[0].is_selected = True
            
    def setup_join_mode(self):
        """Setup join mode with code input"""
        self.mode = "join"
        self.lobby_code_input.active = True
        self.lobby_code_input.clear()
        
        # Clear menu items during code input
        self.menu_items = []
        
    def host_lobby(self):
        """Create a new lobby as host"""
        self.is_host = True
        self.lobby_code = self._generate_lobby_code()
        self.mode = "in_lobby"
        
        # Get current player info from save data
        save_manager = self.director.get_system('save_manager')
        player_name = "Host Player"
        selected_squad = "31A"
        selected_character = "Ruka"
        
        if save_manager and save_manager.current_save:
            game_data = save_manager.current_save.game_data
            selected_squad = game_data.get('selected_squad', '31A')
            selected_character = game_data.get('selected_character', 'ruka')
            
        # Add host as first player
        host_player = {
            'id': 'host',
            'name': player_name,
            'squad': selected_squad,
            'character': selected_character,
            'ready': False
        }
        
        self.connected_players = [host_player]
        self.ready_states = {'host': False}
        
        # Clear menu items when in lobby
        self.menu_items = []
        
        print(f"✓ Created lobby with code: {self.lobby_code}")
        
    def show_join_input(self):
        """Show lobby code input"""
        self.setup_join_mode()
        
    def join_lobby_with_code(self, code: str):
        """Join lobby with provided code"""
        if not code or len(code) != 6:
            print("Invalid lobby code")
            return False
            
        # In a real implementation, this would connect to the actual lobby
        # For demo, simulate joining
        self.is_host = False
        self.lobby_code = code
        self.mode = "in_lobby"
        
        # Simulate existing players in the lobby
        demo_players = [
            {'id': 'host', 'name': 'HostPlayer', 'squad': '31A', 'character': 'Ruka', 'ready': True},
            {'id': 'player2', 'name': 'YukiFan', 'squad': '31A', 'character': 'Yuki', 'ready': False},
        ]
        
        # Add current player
        save_manager = self.director.get_system('save_manager')
        selected_squad = "31A"
        selected_character = "ruka"
        
        if save_manager and save_manager.current_save:
            game_data = save_manager.current_save.game_data
            selected_squad = game_data.get('selected_squad', '31A')
            selected_character = game_data.get('selected_character', 'ruka')
            
        current_player = {
            'id': 'current',
            'name': 'NewPlayer',
            'squad': selected_squad,
            'character': selected_character,
            'ready': False
        }
        
        self.connected_players = demo_players + [current_player]
        self.menu_items = []
        
        print(f"✓ Joined lobby: {code}")
        return True
        
    def quick_match(self):
        """Find and join a random lobby"""
        # Generate a random lobby code and join
        random_code = self._generate_lobby_code()
        self.join_lobby_with_code(random_code)
        
    def _generate_lobby_code(self) -> str:
        """Generate random 6-character lobby code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
    def toggle_ready(self):
        """Toggle ready state for current player"""
        if self.connected_players:
            # Find current player (last in list if not host)
            current_player = None
            if self.is_host:
                current_player = self.connected_players[0]
            else:
                current_player = self.connected_players[-1]
                
            if current_player:
                current_player['ready'] = not current_player['ready']
                
    def change_character(self):
        """Change character in lobby"""
        # Go to character select but return to lobby after
        from src.menu.character_select import CharacterSelectMenu
        from src.data.squad_data import get_squad_data
        
        # Get current squad
        save_manager = self.director.get_system('save_manager')
        if save_manager and save_manager.current_save:
            squad_id = save_manager.current_save.game_data.get('selected_squad', '31A')
            squad_data = get_squad_data(squad_id)
            if squad_data:
                char_select = CharacterSelectMenu(self.director, self.input_manager, squad_data)
                char_select.return_to_lobby = True  # Flag to return to lobby
                self.director.register_scene("character_select", char_select)
                self.director.push_scene("character_select")
                
    def start_game(self):
        """Start the game (host only)"""
        if self.is_host and self.can_start_game():
            self.game_started = True
            
            # Save multiplayer session
            game_instance = self.director.get_system('game_instance')
            if game_instance:
                lobby_data = {
                    'lobby_code': self.lobby_code,
                    'players': self.connected_players,
                    'host_id': 'host'
                }
                game_instance.save_multiplayer_session(lobby_data)
                
            # Start networked game
            self.director.change_scene('gameplay')
            
    def can_start_game(self) -> bool:
        """Check if game can be started"""
        if not self.is_host or len(self.connected_players) < 1:
            return False
        return all(player['ready'] for player in self.connected_players)
        
    def leave_lobby(self):
        """Leave current lobby"""
        self.lobby_code = None
        self.connected_players = []
        self.is_host = False
        self.game_started = False
        self.setup_browser_menu()
        
    def on_enter(self):
        """Setup lobby-specific controls"""
        super().on_enter()
        
        self.input_manager.clear_scene_callbacks(self.scene_name)
        
        # Always register basic navigation
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
            InputAction.BACK, self.handle_back, self.scene_name
        )
        
    def handle_back(self):
        """Handle back button based on current mode"""
        if self.mode == "join":
            # Cancel join mode
            self.setup_browser_menu()
        elif self.mode == "in_lobby":
            # Leave lobby
            self.leave_lobby()
        else:
            # Go back to previous menu
            self.go_back()
            
    def on_key_press(self, key, modifiers):
        """Handle key press"""
        if self.mode == "join" and self.lobby_code_input.active:
            # Handle lobby code input
            if key == arcade.key.ENTER:
                if self.lobby_code_input.is_valid_code():
                    self.join_lobby_with_code(self.lobby_code_input.code)
                    return
            elif key == arcade.key.BACKSPACE:
                self.lobby_code_input.remove_character()
                return
            elif key == arcade.key.ESCAPE:
                self.setup_browser_menu()
                return
            else:
                # Add character if it's alphanumeric
                char = arcade.key.symbol_string(key)
                if len(char) == 1 and char.isalnum():
                    self.lobby_code_input.add_character(char)
                    return
                    
        elif self.mode == "in_lobby":
            # Handle lobby controls
            if key == arcade.key.R:
                self.toggle_ready()
            elif key == arcade.key.C:
                self.change_character()
            elif key == arcade.key.ENTER and self.is_host:
                self.start_game()
            elif key == arcade.key.ESCAPE:
                self.leave_lobby()
            return
            
        # Default key handling for menu navigation
        super().on_key_press(key, modifiers)
        
    def update(self, delta_time: float):
        """Update lobby"""
        super().update(delta_time)
        self.lobby_code_input.update(delta_time)
        
    def draw(self):
        """Draw lobby screen"""
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
        
        if self.mode == "browser":
            self.draw_browser_view()
        elif self.mode == "join":
            self.draw_join_view()
        elif self.mode == "in_lobby":
            self.draw_lobby_view()
            
    def draw_browser_view(self):
        """Draw the lobby browser"""
        # Draw menu items
        for item in self.menu_items:
            item.draw()
            
        # Instructions
        arcade.draw_text(
            "Select an option to join multiplayer",
            SCREEN_WIDTH // 2,
            200,
            arcade.color.WHITE,
            16,
            anchor_x="center"
        )
        
    def draw_join_view(self):
        """Draw the join lobby view"""
        # Instructions
        arcade.draw_text(
            "Enter Lobby Code:",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 80,
            arcade.color.WHITE,
            24,
            anchor_x="center"
        )
        
        # Code input
        self.lobby_code_input.draw()
        
        # Instructions
        instructions_y = SCREEN_HEIGHT // 2 - 80
        arcade.draw_text(
            "Enter 6-character lobby code",
            SCREEN_WIDTH // 2,
            instructions_y,
            arcade.color.WHITE,
            16,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "ENTER: Join Lobby  •  ESC: Back",
            SCREEN_WIDTH // 2,
            instructions_y - 40,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center"
        )
        
    def draw_lobby_view(self):
        """Draw the active lobby view"""
        # Lobby code
        arcade.draw_text(
            f"Lobby Code: {self.lobby_code}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 120,
            arcade.color.YELLOW,
            24,
            anchor_x="center"
        )
        
        # Host indicator
        host_text = "You are the HOST" if self.is_host else "Connected to lobby"
        arcade.draw_text(
            host_text,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 160,
            arcade.color.GREEN if self.is_host else arcade.color.WHITE,
            16,
            anchor_x="center"
        )
        
        # Player list header
        player_y = SCREEN_HEIGHT - 220
        arcade.draw_text(
            f"Players ({len(self.connected_players)}/{self.max_players})",
            200,
            player_y,
            arcade.color.WHITE,
            20
        )
        
        # Player slots
        slot_y = player_y - 60
        for i, player in enumerate(self.connected_players):
            y_pos = slot_y - i * 70
            
            # Player slot background
            bg_color = arcade.color.DARK_GREEN if player['ready'] else arcade.color.DARK_GRAY
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH // 2, y_pos,
                800, 60,
                bg_color
            )
            arcade.draw_rectangle_outline(
                SCREEN_WIDTH // 2, y_pos,
                800, 60,
                arcade.color.WHITE, 2
            )
            
            # Player info
            info_text = f"{player['name']} - {player['squad']} Squad - {player['character']}"
            arcade.draw_text(
                info_text,
                250, y_pos,
                arcade.color.WHITE,
                16,
                anchor_y="center"
            )
            
            # Ready status
            status_text = "READY" if player['ready'] else "NOT READY"
            status_color = arcade.color.GREEN if player['ready'] else arcade.color.RED
            arcade.draw_text(
                status_text,
                SCREEN_WIDTH - 200, y_pos,
                status_color,
                16,
                anchor_y="center"
            )
            
            # Host crown
            if player['id'] == 'host':
                arcade.draw_text(
                    "👑",
                    200, y_pos,
                    arcade.color.GOLD,
                    20,
                    anchor_y="center"
                )
                
        # Control instructions
        instructions_y = 120
        
        arcade.draw_text(
            "R: Toggle Ready  •  C: Change Character",
            SCREEN_WIDTH // 2,
            instructions_y,
            arcade.color.WHITE,
            14,
            anchor_x="center"
        )
        
        if self.is_host:
            start_color = arcade.color.GREEN if self.can_start_game() else arcade.color.GRAY
            arcade.draw_text(
                "ENTER: Start Game" if self.can_start_game() else "Waiting for all players to be ready",
                SCREEN_WIDTH // 2,
                instructions_y - 30,
                start_color,
                14,
                anchor_x="center"
            )
            
        arcade.draw_text(
            "ESC: Leave Lobby",
            SCREEN_WIDTH // 2,
            instructions_y - 60,
            arcade.color.WHITE,
            14,
            anchor_x="center"
        )