"""
Continue menu for multiplayer session rejoining
"""

import arcade
from src.menu.menu_state import MenuState, MenuItem
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.input.input_manager import InputAction

class ContinueMenu(MenuState):
    """Menu for continuing multiplayer sessions"""
    
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Continue Session"
        self.scene_name = "continue_menu"
        
        # Get multiplayer session data
        self.session_data = None
        self.reconnected_players = []
        self.waiting_for_players = []
        
    def on_enter(self):
        """Setup continue menu"""
        super().on_enter()
        
        # Get session data from game instance
        game_instance = self.director.get_system('game_instance')
        if game_instance and game_instance.multiplayer_session_data:
            self.session_data = game_instance.multiplayer_session_data
            self.setup_from_session()
        else:
            # No session data, fall back to squad select
            self.director.change_scene('squad_select')
            return
            
        # Setup continue-specific controls
        self.input_manager.clear_scene_callbacks(self.scene_name)
        
        self.input_manager.register_action_callback(
            InputAction.SELECT, self.start_session, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.BACK, self.cancel_continue, self.scene_name
        )
        
    def setup_from_session(self):
        """Setup continue menu from session data"""
        if not self.session_data:
            return
            
        # Show previous players and wait for reconnection
        previous_players = self.session_data.get('player_list', [])
        
        # For demo purposes, simulate some players reconnecting
        self.reconnected_players = [
            {
                'id': 'host',
                'name': 'Host (You)',
                'character': self.session_data.get('selected_character', 'Ruka'),
                'squad': self.session_data.get('selected_squad', '31A'),
                'status': 'Connected'
            }
        ]
        
        # Simulate other players
        if len(previous_players) > 1:
            for i, player in enumerate(previous_players[1:3]):  # Show up to 2 other players
                self.reconnected_players.append({
                    'id': f'player_{i+2}',
                    'name': player.get('name', f'Player {i+2}'),
                    'character': player.get('character', 'Yuki'),
                    'squad': player.get('squad', '31A'),
                    'status': 'Reconnecting...' if i % 2 == 0 else 'Connected'
                })
                
        # Setup menu items
        menu_y = 200
        self.menu_items = [
            MenuItem(
                "Continue with Current Players",
                self.start_session,
                SCREEN_WIDTH // 2,
                menu_y
            ),
            MenuItem(
                "Change Character",
                self.change_character,
                SCREEN_WIDTH // 2,
                menu_y - 60
            ),
            MenuItem(
                "Start New Session",
                self.new_session,
                SCREEN_WIDTH // 2,
                menu_y - 120
            ),
            MenuItem(
                "Back to Main Menu",
                self.cancel_continue,
                SCREEN_WIDTH // 2,
                menu_y - 180
            )
        ]
        
        if self.menu_items:
            self.menu_items[0].is_selected = True
            
    def start_session(self):
        """Start the session with current players"""
        # Set multiplayer mode
        self.director.systems['is_multiplayer'] = True
        
        # Save session state
        game_instance = self.director.get_system('game_instance')
        if game_instance and self.session_data:
            lobby_data = {
                'lobby_code': self.session_data.get('lobby_code', 'CONTINUE'),
                'players': self.reconnected_players,
                'host_id': 'host'
            }
            game_instance.save_multiplayer_session(lobby_data)
            
        # Go to gameplay
        self.director.change_scene('gameplay')
        
    def change_character(self):
        """Allow character change before continuing"""
        # Go to squad select but maintain continue mode
        self.director.push_scene('squad_select')
        
    def new_session(self):
        """Start a completely new session"""
        game_instance = self.director.get_system('game_instance')
        if game_instance:
            game_instance.start_new_game()
            
    def cancel_continue(self):
        """Cancel continue and return to main menu"""
        self.director.change_scene('main_menu')
        
    def draw(self):
        """Draw continue menu"""
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
        
        # Session info
        if self.session_data:
            lobby_code = self.session_data.get('lobby_code', 'UNKNOWN')
            arcade.draw_text(
                f"Previous Session: {lobby_code}",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT - 120,
                arcade.color.YELLOW,
                20,
                anchor_x="center"
            )
            
        # Player reconnection status
        player_y = SCREEN_HEIGHT - 180
        arcade.draw_text(
            "Player Status:",
            SCREEN_WIDTH // 2,
            player_y,
            arcade.color.WHITE,
            18,
            anchor_x="center"
        )
        
        # Show reconnected players
        for i, player in enumerate(self.reconnected_players):
            y_pos = player_y - 40 - i * 30
            
            # Player info
            status_color = arcade.color.GREEN if player['status'] == 'Connected' else arcade.color.ORANGE
            
            arcade.draw_text(
                f"{player['name']} ({player['character']}) - {player['status']}",
                SCREEN_WIDTH // 2,
                y_pos,
                status_color,
                14,
                anchor_x="center"
            )
            
        # Draw menu items
        for item in self.menu_items:
            item.draw()
            
        # Instructions
        arcade.draw_text(
            "Use Arrow Keys to navigate, Enter to select",
            SCREEN_WIDTH // 2,
            40,
            arcade.color.WHITE,
            12,
            anchor_x="center"
        )