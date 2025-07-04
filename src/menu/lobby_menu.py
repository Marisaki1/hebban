# src/menu/lobby_menu.py
"""
Fixed multiplayer lobby menu with proper state management
"""

import arcade
import random
import string
from src.menu.menu_state import MenuState, MenuItem
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.input.input_manager import InputAction
from src.networking.network_manager import NetworkManager

class LobbyCodeInput:
    """Lobby code input widget - NUMERIC ONLY"""
    
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
        """Check if code is valid format - 6 digits"""
        return len(self.code) == self.max_length and self.code.isdigit()
        
    def add_character(self, char: str):
        """Add character to code - NUMBERS ONLY"""
        if len(self.code) < self.max_length and char.isdigit():
            self.code += char
            
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
            display_text or "Enter 6-Digit Code",
            self.x, self.y,
            arcade.color.WHITE if self.code else arcade.color.GRAY,
            24,
            anchor_x="center",
            anchor_y="center"
        )

class LobbyMenu(MenuState):
    """Fixed multiplayer lobby menu with proper state management"""
    
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Multiplayer Lobby"
        self.scene_name = "lobby_menu"
        
        # Network manager
        self.network_manager = None
        
        # Connection settings
        self.server_host = "192.168.100.5"  # Your default server
        self.server_port = 8080
        
        # Lobby state
        self.mode = "browser"  # "browser", "host", "join", "in_lobby", "connecting", "server_input"
        self.is_host = False
        self.lobby_code = None
        self.connected_players = []
        self.max_players = 6
        self.ready_states = {}
        self.game_started = False
        self.connection_status = "Not connected"
        
        # UI elements
        self.lobby_code_input = LobbyCodeInput(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Server input for internet play
        self.server_input_active = False
        self.server_input = f"{self.server_host}:{self.server_port}"
        
        # Connection check callback reference
        self.connection_check_callback = None
        
        # Initialize menu
        self.setup_browser_menu()
        
    def on_enter(self):
        """Setup lobby when entering scene"""
        super().on_enter()
        print(f"Entering lobby menu - current mode: {self.mode}")
        
        # Set player name from save data
        save_manager = self.director.get_system('save_manager')
        if save_manager and save_manager.current_save:
            game_data = save_manager.current_save.game_data
            player_name = game_data.get('player_name', 'Player')
        else:
            player_name = 'Player'
            
        # Initialize network manager if needed
        if not self.network_manager:
            self.network_manager = NetworkManager()
            self.network_manager.player_name = player_name
            self._setup_network_callbacks()
            
            # Store in director for other scenes
            self.director.systems['network_manager'] = self.network_manager
            
        # Connect to server if not connected
        if not self.network_manager.is_connected:
            self.start_connection()
            
    def start_connection(self):
        """Start connection to server"""
        self.mode = "connecting"
        self.connection_status = f"Connecting to {self.server_host}:{self.server_port}..."
        
        # Clear any existing connection check
        if self.connection_check_callback:
            arcade.unschedule(self.connection_check_callback)
            
        # Start connection
        self.network_manager.start(self.server_host, self.server_port)
        
        # Schedule connection check
        self.connection_check_callback = self._check_connection
        arcade.schedule(self.connection_check_callback, 0.5)
        
    def _check_connection(self, dt):
        """Check if connected to server"""
        if self.network_manager.is_connected:
            self.connection_status = "Connected to server"
            arcade.unschedule(self.connection_check_callback)
            self.connection_check_callback = None
            
            # Switch to browser mode
            self.mode = "browser"
            self.setup_browser_menu()
            
            print("✓ Connected to server - menu enabled")
        else:
            # Still trying to connect
            self.connection_status = f"Connecting to {self.server_host}:{self.server_port}..."
            
    def _setup_network_callbacks(self):
        """Setup network event callbacks"""
        self.network_manager.set_lobby_update_callback(self._on_lobby_update)
        self.network_manager.set_game_start_callback(self._on_game_start)
        self.network_manager.set_disconnect_callback(self._on_disconnect)
        self.network_manager.set_host_change_callback(self._on_host_change)
        
    def _on_lobby_update(self, data: dict):
        """Handle lobby update from server"""
        print(f"Lobby update received: {data}")
        
        if 'error' in data:
            self.connection_status = f"Error: {data['error']}"
            print(f"Lobby error: {data['error']}")
            self.mode = "browser"
            self.setup_browser_menu()
            return
            
        # Update lobby info
        self.lobby_code = data.get('code', self.lobby_code)
        self.connected_players = data.get('players', [])
        self.is_host = (data.get('host_id') == self.network_manager.player_id)
        
        # Update ready states
        self.ready_states = {}
        for player in self.connected_players:
            self.ready_states[player['id']] = player.get('ready', False)
            
        # Ensure we're in lobby mode
        if self.mode != "in_lobby":
            self.mode = "in_lobby"
            self.menu_items = []  # Clear menu items when in lobby
            
        print(f"✓ In lobby {self.lobby_code} with {len(self.connected_players)} players")
            
    def _on_game_start(self, data: dict):
        """Handle game start from server"""
        if 'error' in data:
            self.connection_status = f"Error: {data['error']}"
            return
            
        self.game_started = True
        
        # Save multiplayer session
        game_instance = self.director.get_system('game_instance')
        if game_instance:
            lobby_data = {
                'lobby_code': self.lobby_code,
                'players': self.connected_players,
                'host_id': self.network_manager.player_id if self.is_host else None
            }
            game_instance.save_multiplayer_session(lobby_data)
            
        # Set multiplayer flag
        self.director.systems['is_multiplayer'] = True
        
        # Start networked gameplay
        print("Starting networked gameplay...")
        self.director.change_scene('gameplay')
        
    def _on_disconnect(self, data: dict):
        """Handle disconnection from server"""
        self.connection_status = "Disconnected from server"
        self.mode = "browser"
        self.network_manager.is_connected = False
        self.setup_browser_menu()
        
    def _on_host_change(self, data: dict):
        """Handle host change"""
        new_host_id = data.get('new_host_id')
        if new_host_id == self.network_manager.player_id:
            self.is_host = True
            self.connection_status = "You are now the host!"
            
    def on_exit(self):
        """Cleanup when leaving lobby"""
        print("Exiting lobby menu")
        
        # Unschedule connection check if active
        if self.connection_check_callback:
            arcade.unschedule(self.connection_check_callback)
            self.connection_check_callback = None
            
        # Leave lobby if in one
        if self.lobby_code and self.network_manager:
            self.network_manager.leave_lobby()
            self.lobby_code = None
            
        # Reset state
        self.mode = "browser"
        
    def setup_browser_menu(self):
        """Setup initial lobby browser menu"""
        print(f"Setting up browser menu - connected: {self.network_manager.is_connected if self.network_manager else False}")
        
        self.mode = "browser"
        menu_y_start = 400
        menu_spacing = 70
        
        self.menu_items = []
        
        # Host Lobby button
        host_item = MenuItem(
            "Host Lobby",
            self.host_lobby if self.network_manager and self.network_manager.is_connected else lambda: None,
            SCREEN_WIDTH // 2,
            menu_y_start
        )
        # Gray out if not connected
        if not (self.network_manager and self.network_manager.is_connected):
            host_item.text = "Host Lobby (Not Connected)"
        self.menu_items.append(host_item)
        
        # Join with Code button
        join_item = MenuItem(
            "Join with Code",
            self.show_join_input if self.network_manager and self.network_manager.is_connected else lambda: None,
            SCREEN_WIDTH // 2,
            menu_y_start - menu_spacing
        )
        # Gray out if not connected
        if not (self.network_manager and self.network_manager.is_connected):
            join_item.text = "Join with Code (Not Connected)"
        self.menu_items.append(join_item)
        
        # Change Server button
        self.menu_items.append(MenuItem(
            "Change Server",
            self.show_server_input,
            SCREEN_WIDTH // 2,
            menu_y_start - menu_spacing * 2
        ))
        
        # Back button
        self.menu_items.append(MenuItem(
            "Back",
            self.go_back,
            SCREEN_WIDTH // 2,
            menu_y_start - menu_spacing * 3
        ))
        
        # Select first item
        if self.menu_items:
            self.menu_items[0].is_selected = True
            self.selected_index = 0
            
    def host_lobby(self):
        """Create a new lobby as host"""
        if not self.network_manager or not self.network_manager.is_connected:
            self.connection_status = "Not connected to server"
            return
            
        print("Creating lobby...")
        
        self.is_host = True
        self.lobby_code = self._generate_lobby_code()
        self.mode = "in_lobby"
        
        # Get current character data
        character_data = self._get_character_data()
        
        # Create lobby on server
        self.network_manager.create_lobby(self.lobby_code)
        
        # Clear menu items when in lobby
        self.menu_items = []
        
        print(f"Creating lobby with code: {self.lobby_code}")
        
    def show_join_input(self):
        """Show lobby code input"""
        if not self.network_manager or not self.network_manager.is_connected:
            self.connection_status = "Not connected to server"
            return
            
        print("Showing join input...")
        self.mode = "join"
        self.lobby_code_input.active = True
        self.lobby_code_input.clear()
        
        # Clear menu items during code input
        self.menu_items = []
        
    def show_server_input(self):
        """Show server input"""
        print("Showing server input...")
        self.server_input_active = True
        self.mode = "server_input"
        self.menu_items = []
        
    def join_lobby_with_code(self, code: str):
        """Join lobby with provided code"""
        if not self.network_manager or not self.network_manager.is_connected:
            self.connection_status = "Not connected to server"
            return False
            
        if not code or len(code) != 6 or not code.isdigit():
            self.connection_status = "Invalid lobby code (must be 6 digits)"
            return False
            
        print(f"Joining lobby with code: {code}")
        
        self.is_host = False
        self.lobby_code = code
        self.mode = "in_lobby"
        
        # Get character data
        character_data = self._get_character_data()
        
        # Join lobby on server
        self.network_manager.join_lobby(code, character_data)
        
        self.menu_items = []
        
        return True
        
    def _get_character_data(self) -> dict:
        """Get current character data"""
        save_manager = self.director.get_system('save_manager')
        if save_manager and save_manager.current_save:
            game_data = save_manager.current_save.game_data
            return {
                'squad': game_data.get('selected_squad', '31A'),
                'character': game_data.get('selected_character', 'ruka')
            }
        return {'squad': '31A', 'character': 'ruka'}
        
    def _generate_lobby_code(self) -> str:
        """Generate random 6-digit lobby code"""
        return ''.join(random.choices('0123456789', k=6))
        
    def toggle_ready(self):
        """Toggle ready state for current player"""
        if self.connected_players and self.network_manager:
            # Find current player
            current_player = None
            for player in self.connected_players:
                if player['id'] == self.network_manager.player_id:
                    current_player = player
                    break
                    
            if current_player:
                new_ready = not current_player.get('ready', False)
                self.network_manager.set_ready(new_ready)
                print(f"Set ready state to: {new_ready}")
                
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
            print("Starting game...")
            self.network_manager.start_game()
            
    def can_start_game(self) -> bool:
        """Check if game can be started"""
        if not self.is_host or len(self.connected_players) < 1:
            return False
        return all(player['ready'] for player in self.connected_players)
        
    def leave_lobby(self):
        """Leave current lobby"""
        print("Leaving lobby...")
        if self.network_manager:
            self.network_manager.leave_lobby()
        self.lobby_code = None
        self.connected_players = []
        self.is_host = False
        self.game_started = False
        self.mode = "browser"
        self.setup_browser_menu()
        
    def on_key_press(self, key, modifiers):
        """Handle key press"""
        # Handle different modes
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
                self.mode = "browser"
                self.setup_browser_menu()
                return
            else:
                # Handle numeric input only
                if 48 <= key <= 57:  # 0-9
                    char = chr(key)
                    self.lobby_code_input.add_character(char)
                return
                
        elif self.mode == "server_input" and self.server_input_active:
            # Handle server input
            if key == arcade.key.ENTER:
                # Parse server input
                parts = self.server_input.split(':')
                if len(parts) == 2:
                    try:
                        self.server_host = parts[0]
                        self.server_port = int(parts[1])
                        
                        # Disconnect and reconnect
                        if self.network_manager:
                            self.network_manager.disconnect()
                            
                        # Reinitialize network manager
                        self.network_manager = NetworkManager()
                        self.network_manager.player_name = self._get_player_name()
                        self._setup_network_callbacks()
                        self.director.systems['network_manager'] = self.network_manager
                        
                        # Start connection
                        self.start_connection()
                        
                        # Return to browser
                        self.server_input_active = False
                        
                    except ValueError:
                        self.connection_status = "Invalid port number"
                else:
                    self.connection_status = "Invalid format (use host:port)"
                return
                
            elif key == arcade.key.BACKSPACE:
                if self.server_input:
                    self.server_input = self.server_input[:-1]
                return
            elif key == arcade.key.ESCAPE:
                self.server_input_active = False
                self.mode = "browser"
                self.setup_browser_menu()
                return
            else:
                # Add character to server input
                if 32 <= key <= 126:  # Printable characters
                    self.server_input += chr(key)
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
            # CTRL+C to copy lobby code
            elif key == arcade.key.C and modifiers & arcade.key.MOD_CTRL:
                self.copy_lobby_code()
            return
            
        elif self.mode == "browser":
            # Default menu navigation
            super().on_key_press(key, modifiers)
            
    def _get_player_name(self) -> str:
        """Get player name from save data"""
        save_manager = self.director.get_system('save_manager')
        if save_manager and save_manager.current_save:
            return save_manager.current_save.game_data.get('player_name', 'Player')
        return 'Player'
        
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
        
        # Connection status
        status_color = arcade.color.GREEN if self.network_manager and self.network_manager.is_connected else arcade.color.RED
        arcade.draw_text(
            self.connection_status,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            status_color,
            14,
            anchor_x="center"
        )
        
        # Draw based on current mode
        if self.mode == "browser":
            self.draw_browser_view()
        elif self.mode == "join":
            self.draw_join_view()
        elif self.mode == "in_lobby":
            self.draw_lobby_view()
        elif self.mode == "connecting":
            self.draw_connecting_view()
        elif self.mode == "server_input":
            self.draw_server_input()
            
    def draw_connecting_view(self):
        """Draw connecting screen"""
        arcade.draw_text(
            "Connecting to server...",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            arcade.color.WHITE,
            24,
            anchor_x="center"
        )
        
        arcade.draw_text(
            f"{self.server_host}:{self.server_port}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 40,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center"
        )
        
        # Animated dots
        dots = "." * (int(self.lobby_code_input.cursor_timer) % 4)
        arcade.draw_text(
            dots,
            SCREEN_WIDTH // 2 + 100,
            SCREEN_HEIGHT // 2,
            arcade.color.WHITE,
            24
        )
        
    def draw_server_input(self):
        """Draw server input screen"""
        arcade.draw_text(
            "Enter Server Address:",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 80,
            arcade.color.WHITE,
            24,
            anchor_x="center"
        )
        
        # Input field
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            400, 50,
            arcade.color.DARK_GRAY
        )
        arcade.draw_rectangle_outline(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            400, 50,
            arcade.color.WHITE, 2
        )
        
        # Server text with cursor
        cursor = "_" if self.lobby_code_input.cursor_timer % 1.0 < 0.5 else ""
        arcade.draw_text(
            self.server_input + cursor,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            arcade.color.WHITE,
            20,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Instructions
        arcade.draw_text(
            "Format: hostname:port (e.g., 192.168.1.100:8080)",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 60,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "ENTER: Connect  •  ESC: Cancel",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 100,
            arcade.color.WHITE,
            14,
            anchor_x="center"
        )
        
    def draw_browser_view(self):
        """Draw the lobby browser"""
        # Draw menu items
        for item in self.menu_items:
            item.draw()
            
        # Instructions
        instructions_text = "Select an option to join multiplayer"
        if not (self.network_manager and self.network_manager.is_connected):
            instructions_text = "Not connected to server - Select 'Change Server' to connect"
            
        arcade.draw_text(
            instructions_text,
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
            "Enter 6-Digit Lobby Code:",
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
            "Enter the 6-digit code to join a lobby",
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
        
    def copy_lobby_code(self):
        """Copy lobby code to clipboard"""
        if self.lobby_code:
            try:
                import pyperclip
                pyperclip.copy(self.lobby_code)
                self.connection_status = f"Lobby code {self.lobby_code} copied to clipboard!"
                print(f"Lobby code {self.lobby_code} copied to clipboard!")
            except ImportError:
                print("Pyperclip not available - cannot copy to clipboard")
            except Exception as e:
                print(f"Error copying to clipboard: {e}")
                
    def draw_lobby_view(self):
        """Draw the active lobby view"""
        # Large lobby code display
        lobby_code_y = SCREEN_HEIGHT - 140
        arcade.draw_text(
            f"Lobby Code: {self.lobby_code}",
            SCREEN_WIDTH // 2,
            lobby_code_y,
            arcade.color.YELLOW,
            32,
            anchor_x="center"
        )
        
        # Copy instruction
        arcade.draw_text(
            "(Press CTRL+C to copy lobby code)",
            SCREEN_WIDTH // 2,
            lobby_code_y - 35,
            arcade.color.LIGHT_GRAY,
            12,
            anchor_x="center"
        )
        
        # Host indicator
        host_text = "You are the HOST" if self.is_host else "Connected to lobby"
        host_color = arcade.color.GREEN if self.is_host else arcade.color.WHITE
        arcade.draw_text(
            host_text,
            SCREEN_WIDTH // 2,
            lobby_code_y - 65,
            host_color,
            18,
            anchor_x="center"
        )
        
        # Player list header
        player_y = SCREEN_HEIGHT - 260
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
            
            # Highlight current player
            if player['id'] == self.network_manager.player_id:
                bg_color = arcade.color.DARK_BLUE if not player['ready'] else arcade.color.DARK_GREEN
                
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
            character_data = player.get('character', {})
            squad = character_data.get('squad', '31A')
            character = character_data.get('character', 'ruka')
            
            # Show player name and character
            info_text = f"{player['name']} - {squad} Squad - {character.title()}"
            arcade.draw_text(
                info_text,
                250, y_pos,
                arcade.color.WHITE,
                16,
                anchor_y="center"
            )
            
            # Connection status
            if player.get('connected', True):
                status_text = "READY" if player['ready'] else "NOT READY"
                status_color = arcade.color.GREEN if player['ready'] else arcade.color.RED
            else:
                status_text = "DISCONNECTED"
                status_color = arcade.color.GRAY
                
            arcade.draw_text(
                status_text,
                SCREEN_WIDTH - 200, y_pos,
                status_color,
                16,
                anchor_y="center"
            )
            
            # Host crown
            if player['id'] == self.network_manager.lobby_info.get('host_id'):
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
            "R: Toggle Ready  •  C: Change Character  •  CTRL+C: Copy Code",
            SCREEN_WIDTH // 2,
            instructions_y,
            arcade.color.WHITE,
            14,
            anchor_x="center"
        )
        
        if self.is_host:
            if self.can_start_game():
                start_text = "ENTER: Start Game"
                start_color = arcade.color.GREEN
            else:
                start_text = "Waiting for all players to be ready..."
                start_color = arcade.color.GRAY
                
            arcade.draw_text(
                start_text,
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