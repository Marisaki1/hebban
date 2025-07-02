# src/menu/lobby_menu.py - Fixed for Arcade 3.0
"""
Multiplayer lobby for hosting/joining games - Fixed for Arcade 3.0
"""
from typing import List
import arcade

from src.core.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from src.menu.menu_state import MenuItem, MenuState

class LobbyMenu(MenuState):
    """Multiplayer lobby for hosting/joining games"""
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Multiplayer Lobby"
        self.is_host = False
        self.lobby_code = None
        self.connected_players = []
        self.max_players = 8
        self.ready_states = {}
        
    def create_lobby(self):
        """Create a new lobby as host"""
        self.is_host = True
        self.lobby_code = self._generate_lobby_code()
        self.connected_players = [
            {
                'id': 'host',
                'name': 'Host Player',
                'squad': 'Squad Alpha',
                'character': 'Ruka',
                'ready': False
            }
        ]
        
    def _generate_lobby_code(self) -> str:
        """Generate random lobby code"""
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
    def draw(self):
        """Draw lobby screen using Arcade 3.0 functions"""
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
            anchor_x="center",
            font_name="Arial",
            bold=True
        )
        
        if self.lobby_code:
            # Show lobby code
            arcade.draw_text(
                f"Lobby Code: {self.lobby_code}",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT - 120,
                arcade.color.YELLOW,
                24,
                anchor_x="center"
            )
            
            # Player list
            player_y = SCREEN_HEIGHT - 200
            
            arcade.draw_text(
                f"Players ({len(self.connected_players)}/{self.max_players})",
                200,
                player_y,
                arcade.color.WHITE,
                20,
                font_name="Arial",
                bold=True
            )
            
            player_y -= 40
            
            for i, player in enumerate(self.connected_players):
                # Player slot background
                bg_color = arcade.color.DARK_GREEN if player['ready'] else arcade.color.DARK_GRAY
                arcade.draw_rectangle_filled(
                    SCREEN_WIDTH // 2, player_y - i * 60,
                    800, 50,
                    bg_color
                )
                
                # Player info
                info_text = f"{player['name']} - {player['squad']} - {player['character']}"
                arcade.draw_text(
                    info_text,
                    250, player_y - i * 60,
                    arcade.color.WHITE,
                    16,
                    anchor_y="center"
                )
                
                # Ready status
                status_text = "READY" if player['ready'] else "NOT READY"
                status_color = arcade.color.GREEN if player['ready'] else arcade.color.RED
                arcade.draw_text(
                    status_text,
                    SCREEN_WIDTH - 250, player_y - i * 60,
                    status_color,
                    16,
                    anchor_y="center"
                )
                
            # Start button (host only)
            if self.is_host:
                all_ready = all(p['ready'] for p in self.connected_players)
                button_color = arcade.color.GREEN if all_ready else arcade.color.DARK_GRAY
                arcade.draw_rectangle_filled(
                    SCREEN_WIDTH // 2, 100,
                    200, 50,
                    button_color
                )
                arcade.draw_text(
                    "START GAME",
                    SCREEN_WIDTH // 2, 100,
                    arcade.color.WHITE,
                    20,
                    anchor_x="center",
                    anchor_y="center",
                    font_name="Arial",
                    bold=True
                )
        else:
            # Show create/join options
            self.menu_items = [
                MenuItem("Create Lobby", self.create_lobby, SCREEN_WIDTH // 2, 400),
                MenuItem("Join Lobby", self.join_lobby, SCREEN_WIDTH // 2, 320),
                MenuItem("Back", self.go_back, SCREEN_WIDTH // 2, 240)
            ]
            
            for item in self.menu_items:
                item.draw()
                
    def join_lobby(self):
        """Join existing lobby"""
        # This would open input dialog for lobby code
        pass