"""
Multiplayer lobby menu
"""

import arcade
import random
import string
from src.menu.menu_state import MenuState, MenuItem
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class LobbyMenu(MenuState):
    """Multiplayer lobby for hosting/joining games"""
    
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Multiplayer Lobby"
        self.scene_name = "lobby"
        
        # Lobby state
        self.is_host = False
        self.lobby_code = None
        self.connected_players = []
        self.max_players = 8
        self.ready_states = {}
        self.game_started = False
        
        # Menu items for lobby browser
        self.setup_menu_items()
        
    def setup_menu_items(self):
        """Setup initial menu items"""
        menu_y_start = 400
        menu_spacing = 70
        
        self.menu_items = [
            MenuItem(
                "Create Lobby",
                self.create_lobby,
                SCREEN_WIDTH // 2,
                menu_y_start
            ),
            MenuItem(
                "Join Lobby",
                self.join_lobby,
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
            
    def create_lobby(self):
        """Create a new lobby as host"""
        self.is_host = True
        self.lobby_code = self._generate_lobby_code()
        
        # Add host as first player
        host_player = {
            'id': 'host',
            'name': 'Host Player',
            'squad': '31A',
            'character': 'Ruka',
            'ready': False
        }
        
        self.connected_players = [host_player]
        self.ready_states = {'host': False}
        
        # Clear menu items when in lobby
        self.menu_items = []
        
    def join_lobby(self):
        """Join existing lobby (placeholder)"""
        # In a real implementation, this would open a code input dialog
        # For now, simulate joining a lobby
        self.is_host = False
        self.lobby_code = "DEMO123"
        
        # Simulate some players already in lobby
        demo_players = [
            {'id': 'host', 'name': 'HostPlayer', 'squad': '31A', 'character': 'Ruka', 'ready': True},
            {'id': 'player2', 'name': 'YukiFan', 'squad': '31A', 'character': 'Yuki', 'ready': False},
            {'id': 'player3', 'name': 'KarenMain', 'squad': '31A', 'character': 'Karen', 'ready': True},
        ]
        
        # Add current player
        current_player = {
            'id': 'current',
            'name': 'NewPlayer',
            'squad': '31A',
            'character': 'Tsukasa',
            'ready': False
        }
        
        self.connected_players = demo_players + [current_player]
        self.menu_items = []
        
    def quick_match(self):
        """Find and join a random lobby (placeholder)"""
        # Simulate finding a match
        self.join_lobby()
        
    def _generate_lobby_code(self) -> str:
        """Generate random 6-character lobby code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
    def toggle_ready(self):
        """Toggle ready state for current player"""
        if self.connected_players:
            current_player = self.connected_players[-1]  # Assume last is current player
            current_player['ready'] = not current_player['ready']
            
    def start_game(self):
        """Start the game (host only)"""
        if self.is_host and self.can_start_game():
            self.game_started = True
            # In real implementation, would start networked game
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
        self.setup_menu_items()
        
    def on_key_press(self, key, modifiers):
        """Handle key press in lobby"""
        super().on_key_press(key, modifiers)
        
        if self.lobby_code:  # In lobby
            if key == arcade.key.R:
                self.toggle_ready()
            elif key == arcade.key.ENTER and self.is_host:
                self.start_game()
            elif key == arcade.key.ESCAPE:
                self.leave_lobby()
                
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
        
        if self.lobby_code:
            self.draw_lobby_view()
        else:
            self.draw_menu_view()
            
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
                
        # Empty slots
        for i in range(len(self.connected_players), self.max_players):
            y_pos = slot_y - i * 70
            
            arcade.draw_rectangle_outline(
                SCREEN_WIDTH // 2, y_pos,
                800, 60,
                arcade.color.DARK_GRAY, 1
            )
            
            arcade.draw_text(
                "--- Waiting for player ---",
                SCREEN_WIDTH // 2, y_pos,
                arcade.color.DARK_GRAY,
                16,
                anchor_x="center",
                anchor_y="center"
            )
            
        # Control instructions
        instructions_y = 120
        
        arcade.draw_text(
            "R: Toggle Ready",
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
        
    def draw_menu_view(self):
        """Draw the lobby browser menu"""
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