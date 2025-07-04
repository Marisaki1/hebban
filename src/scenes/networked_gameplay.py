# src/scenes/networked_gameplay.py
"""
Networked gameplay scene that syncs with other players
"""

from src.scenes.gameplay import GameplayScene
from src.entities.player import Player
import arcade

class NetworkedGameplayScene(GameplayScene):
    """Gameplay scene with networking support"""
    
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        
        # Network manager
        self.network_manager = None
        self.is_networked = False
        
        # Other players
        self.other_players = {}  # player_id -> Player sprite
        self.network_update_timer = 0
        self.network_update_rate = 1/30  # 30 updates per second
        
    def on_enter(self):
        """Setup networked gameplay"""
        # Check if this is a networked game
        self.is_networked = self.director.systems.get('is_multiplayer', False)
        
        if self.is_networked:
            # Get network manager
            self.network_manager = self.director.get_system('network_manager')
            if not self.network_manager:
                # Create one if needed
                from src.networking.network_manager import NetworkManager
                self.network_manager = NetworkManager()
                self.director.systems['network_manager'] = self.network_manager
                
            # Setup network callbacks
            self._setup_network_callbacks()
            
        # Call parent setup
        super().on_enter()
        
        # Create other players if networked
        if self.is_networked and self.network_manager and self.network_manager.lobby_info:
            self._create_other_players()
            
    def _setup_network_callbacks(self):
        """Setup network event callbacks"""
        if self.network_manager:
            self.network_manager.set_player_update_callback(self._on_player_update)
            self.network_manager.set_disconnect_callback(self._on_player_disconnect)
            
    def _create_other_players(self):
        """Create sprites for other players in lobby"""
        if not self.network_manager or not self.network_manager.lobby_info:
            return
            
        players = self.network_manager.lobby_info.get('players', [])
        
        for player_data in players:
            player_id = player_data['id']
            
            # Skip self
            if player_id == self.network_manager.player_id:
                continue
                
            # Create player sprite
            character_info = player_data.get('character', {})
            char_data = self._get_character_data_for_player(character_info)
            
            if char_data:
                other_player = Player(char_data, None)  # No input manager for other players
                other_player.center_x = 300 + len(self.other_players) * 100
                other_player.center_y = 200
                
                self.other_players[player_id] = other_player
                self.player_list.append(other_player)
                
                print(f"Created player sprite for {player_data['name']}")
                
    def _get_character_data_for_player(self, character_info: dict) -> dict:
        """Get character data for a player"""
        from src.data.squad_data import get_character_data
        
        squad_id = character_info.get('squad', '31A')
        char_id = character_info.get('character', 'ruka')
        
        char_data = get_character_data(squad_id, char_id)
        if char_data:
            return char_data
            
        # Fallback
        return {
            'id': char_id,
            'name': char_id.title(),
            'health': 100,
            'speed': 6,
            'jump_power': 15,
            'attack': 8,
            'defense': 6,
            'abilities': []
        }
        
    def _on_player_update(self, data: dict):
        """Handle player update from network"""
        player_id = data.get('player_id')
        
        if not player_id or player_id == self.network_manager.player_id:
            return
            
        # Create player if doesn't exist
        if player_id not in self.other_players:
            # Create new player
            # TODO: Get proper character data
            char_data = {
                'id': 'yuki',
                'name': 'Network Player',
                'health': 100,
                'speed': 6,
                'jump_power': 15,
                'attack': 8,
                'defense': 6,
                'abilities': []
            }
            
            other_player = Player(char_data, None)
            self.other_players[player_id] = other_player
            self.player_list.append(other_player)
            
        # Update player position and state
        player = self.other_players[player_id]
        position = data.get('position', (0, 0))
        velocity = data.get('velocity', (0, 0))
        state = data.get('state', 'idle')
        health = data.get('health', 100)
        facing_right = data.get('facing_right', True)
        
        player.center_x = position[0]
        player.center_y = position[1]
        player.velocity = list(velocity)
        player.health = health
        player.facing_right = facing_right
        
        # Update state
        if state == 'attacking':
            player.is_attacking = True
        else:
            player.is_attacking = False
            
    def _on_player_disconnect(self, data: dict):
        """Handle player disconnection"""
        player_id = data.get('player_id')
        
        if player_id and player_id in self.other_players:
            # Remove player sprite
            player = self.other_players[player_id]
            player.remove_from_sprite_lists()
            del self.other_players[player_id]
            
            print(f"Player {player_id} disconnected")
            
    def update(self, delta_time: float):
        """Update with network synchronization"""
        super().update(delta_time)
        
        # Send network updates if networked
        if self.is_networked and self.network_manager and not self.game_over:
            self.network_update_timer += delta_time
            
            if self.network_update_timer >= self.network_update_rate:
                self.network_update_timer = 0
                self._send_player_update()
                
    def _send_player_update(self):
        """Send player state to server"""
        if not self.player or not self.network_manager:
            return
            
        # Determine player state
        state = 'idle'
        if self.player.is_attacking:
            state = 'attacking'
        elif abs(self.player.velocity[0]) > 0.1:
            state = 'moving'
        elif self.player.velocity[1] != 0:
            state = 'jumping'
            
        # Send update
        self.network_manager.send_player_update(
            (self.player.center_x, self.player.center_y),
            tuple(self.player.velocity),
            state,
            self.player.health
        )
        
    def check_combat_collisions(self):
        """Check collisions including networked players"""
        # Call parent for normal enemy collisions
        super().check_combat_collisions()
        
        # In networked games, collisions between players could be handled here
        # For now, we'll keep it PvE
        
    def draw(self):
        """Draw with player names"""
        super().draw()
        
        # Draw player names above networked players
        if self.is_networked:
            self.gui_camera.use()
            
            # Draw names above other players
            for player_id, player in self.other_players.items():
                # Get player name from lobby info
                player_name = "Player"
                if self.network_manager and self.network_manager.lobby_info:
                    players = self.network_manager.lobby_info.get('players', [])
                    for p in players:
                        if p['id'] == player_id:
                            player_name = p.get('name', 'Player')
                            break
                            
                # Convert world position to screen position
                screen_x = player.center_x - self.camera.position[0]
                screen_y = player.center_y - self.camera.position[1] + 40
                
                # Draw name
                arcade.draw_text(
                    player_name,
                    screen_x, screen_y,
                    arcade.color.WHITE,
                    12,
                    anchor_x="center"
                )
                
                # Draw health bar
                bar_width = 40
                bar_height = 4
                health_percent = player.health / player.max_health
                
                arcade.draw_rectangle_filled(
                    screen_x, screen_y - 10,
                    bar_width, bar_height,
                    arcade.color.DARK_RED
                )
                
                if health_percent > 0:
                    arcade.draw_rectangle_filled(
                        screen_x - bar_width/2 + (bar_width * health_percent)/2,
                        screen_y - 10,
                        bar_width * health_percent, bar_height,
                        arcade.color.GREEN
                    )