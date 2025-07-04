# server.py
"""
Heaven Burns Red - Dedicated Game Server
Supports up to 20 concurrent lobbies with 6 players each
"""

import asyncio
import websockets
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Set
import argparse
import logging

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.networking.protocol import NetworkProtocol, MessageType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Player:
    """Connected player"""
    def __init__(self, player_id: str, websocket, player_name: str = "Player"):
        self.id = player_id
        self.websocket = websocket
        self.name = player_name
        self.lobby_code = None
        self.character = None
        self.ready = False
        self.position = (0, 0)
        self.health = 100
        self.connected = True
        self.last_ping = datetime.now()
        
class Lobby:
    """Game lobby"""
    def __init__(self, code: str, host_id: str, max_players: int = 6):
        self.code = code
        self.host_id = host_id
        self.max_players = max_players
        self.players: Dict[str, Player] = {}
        self.game_started = False
        self.created_at = datetime.now()
        self.game_state = {
            'enemies': [],
            'items': [],
            'wave': 1,
            'score': 0
        }
        
    def add_player(self, player: Player):
        """Add player to lobby"""
        self.players[player.id] = player
        player.lobby_code = self.code
        
    def remove_player(self, player_id: str):
        """Remove player from lobby"""
        if player_id in self.players:
            self.players[player_id].lobby_code = None
            del self.players[player_id]
            
            # Select new host if needed
            if self.host_id == player_id and self.players:
                self.host_id = next(iter(self.players.keys()))
                return True  # Host changed
        return False
        
    def get_lobby_info(self):
        """Get lobby information"""
        return {
            'code': self.code,
            'host_id': self.host_id,
            'players': [
                {
                    'id': p.id,
                    'name': p.name,
                    'character': p.character,
                    'ready': p.ready,
                    'connected': p.connected
                }
                for p in self.players.values()
            ],
            'max_players': self.max_players,
            'game_started': self.game_started
        }

class GameServer:
    """Main game server"""
    
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.players: Dict[str, Player] = {}  # All connected players
        self.lobbies: Dict[str, Lobby] = {}  # Active lobbies
        self.max_lobbies = 20
        
        # Statistics
        self.total_connections = 0
        self.start_time = datetime.now()
        
    async def handle_client(self, websocket, path):
        """Handle client connection"""
        player = None
        try:
            # Wait for initial connect message
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            msg_type, data = NetworkProtocol.parse_message(message)
            
            if msg_type != MessageType.CONNECT:
                await websocket.close()
                return
                
            # Create player
            player_id = data.get('player_id', f'player_{self.total_connections}')
            player_name = data.get('player_name', 'Player')
            player = Player(player_id, websocket, player_name)
            
            self.players[player_id] = player
            self.total_connections += 1
            
            logger.info(f"Player {player_id} ({player_name}) connected from {websocket.remote_address}")
            
            # Send connection confirmation
            await websocket.send(
                NetworkProtocol.create_message(
                    MessageType.CONNECT,
                    {
                        'status': 'connected',
                        'player_id': player_id,
                        'server_info': {
                            'version': '1.0.0',
                            'max_lobbies': self.max_lobbies,
                            'active_lobbies': len(self.lobbies)
                        }
                    }
                )
            )
            
            # Handle messages
            async for message in websocket:
                await self.handle_message(player, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Player {player.id if player else 'unknown'} disconnected")
        except asyncio.TimeoutError:
            logger.warning("Client failed to send connect message")
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            if player:
                await self.handle_disconnect(player)
                
    async def handle_message(self, player: Player, message: str):
        """Handle incoming message from player"""
        msg_type, data = NetworkProtocol.parse_message(message)
        
        if not msg_type:
            return
            
        try:
            if msg_type == MessageType.CREATE_LOBBY:
                await self.create_lobby(player, data)
            elif msg_type == MessageType.JOIN_LOBBY:
                await self.join_lobby(player, data)
            elif msg_type == MessageType.LEAVE_LOBBY:
                await self.leave_lobby(player, data)
            elif msg_type == MessageType.LOBBY_LIST:
                await self.send_lobby_list(player)
            elif msg_type == MessageType.PLAYER_READY:
                await self.player_ready(player, data)
            elif msg_type == MessageType.START_GAME:
                await self.start_game(player, data)
            elif msg_type == MessageType.PLAYER_UPDATE:
                await self.handle_player_update(player, data)
            elif msg_type == MessageType.PLAYER_ACTION:
                await self.handle_player_action(player, data)
            elif msg_type == MessageType.RECONNECT:
                await self.handle_reconnect(player, data)
            elif msg_type == MessageType.PING:
                await self.handle_ping(player)
                
        except Exception as e:
            logger.error(f"Error handling message {msg_type} from {player.id}: {e}")
            
    async def create_lobby(self, player: Player, data: Dict):
        """Create new lobby"""
        if len(self.lobbies) >= self.max_lobbies:
            await self.send_to_player(player, 
                NetworkProtocol.create_message(
                    MessageType.LOBBY_INFO,
                    {'error': 'Server full - maximum lobbies reached'}
                )
            )
            return
            
        lobby_code = data.get('lobby_code', self._generate_lobby_code())
        
        if lobby_code in self.lobbies:
            await self.send_to_player(player,
                NetworkProtocol.create_message(
                    MessageType.LOBBY_INFO,
                    {'error': 'Lobby code already exists'}
                )
            )
            return
            
        # Leave current lobby if in one
        if player.lobby_code:
            await self.leave_lobby(player, {'lobby_code': player.lobby_code})
            
        # Create new lobby
        max_players = data.get('max_players', 6)
        lobby = Lobby(lobby_code, player.id, max_players)
        lobby.add_player(player)
        self.lobbies[lobby_code] = lobby
        
        logger.info(f"Lobby {lobby_code} created by {player.id}")
        
        # Send lobby info to creator
        await self.send_to_player(player,
            NetworkProtocol.create_message(
                MessageType.LOBBY_INFO,
                lobby.get_lobby_info()
            )
        )
        
    async def join_lobby(self, player: Player, data: Dict):
        """Join existing lobby"""
        lobby_code = data.get('lobby_code')
        
        if not lobby_code or lobby_code not in self.lobbies:
            await self.send_to_player(player,
                NetworkProtocol.create_message(
                    MessageType.LOBBY_INFO,
                    {'error': 'Lobby not found'}
                )
            )
            return
            
        lobby = self.lobbies[lobby_code]
        
        if len(lobby.players) >= lobby.max_players:
            await self.send_to_player(player,
                NetworkProtocol.create_message(
                    MessageType.LOBBY_INFO,
                    {'error': 'Lobby full'}
                )
            )
            return
            
        if lobby.game_started:
            # Allow reconnection only
            if player.id not in [p.id for p in lobby.players.values()]:
                await self.send_to_player(player,
                    NetworkProtocol.create_message(
                        MessageType.LOBBY_INFO,
                        {'error': 'Game already started'}
                    )
                )
                return
                
        # Leave current lobby if in one
        if player.lobby_code:
            await self.leave_lobby(player, {'lobby_code': player.lobby_code})
            
        # Add character data if provided
        if 'character' in data:
            player.character = data['character']
            
        # Add to lobby
        lobby.add_player(player)
        
        logger.info(f"Player {player.id} joined lobby {lobby_code}")
        
        # Broadcast updated lobby info
        await self.broadcast_to_lobby(lobby_code,
            NetworkProtocol.create_message(
                MessageType.LOBBY_INFO,
                lobby.get_lobby_info()
            )
        )
        
    async def leave_lobby(self, player: Player, data: Dict):
        """Leave current lobby"""
        lobby_code = data.get('lobby_code') or player.lobby_code
        
        if not lobby_code or lobby_code not in self.lobbies:
            return
            
        lobby = self.lobbies[lobby_code]
        host_changed = lobby.remove_player(player.id)
        
        logger.info(f"Player {player.id} left lobby {lobby_code}")
        
        # Remove empty lobbies
        if not lobby.players:
            del self.lobbies[lobby_code]
            logger.info(f"Lobby {lobby_code} removed (empty)")
            return
            
        # Notify remaining players
        message = NetworkProtocol.create_message(
            MessageType.LOBBY_INFO,
            lobby.get_lobby_info()
        )
        
        if host_changed:
            # Also send host change notification
            await self.broadcast_to_lobby(lobby_code,
                NetworkProtocol.create_message(
                    MessageType.HOST_CHANGE,
                    {'new_host_id': lobby.host_id}
                )
            )
            
        await self.broadcast_to_lobby(lobby_code, message)
        
    async def player_ready(self, player: Player, data: Dict):
        """Update player ready state"""
        if not player.lobby_code:
            return
            
        player.ready = data.get('ready', False)
        
        lobby = self.lobbies.get(player.lobby_code)
        if lobby:
            await self.broadcast_to_lobby(player.lobby_code,
                NetworkProtocol.create_message(
                    MessageType.LOBBY_INFO,
                    lobby.get_lobby_info()
                )
            )
            
    async def start_game(self, player: Player, data: Dict):
        """Start game (host only)"""
        lobby_code = data.get('lobby_code') or player.lobby_code
        
        if not lobby_code or lobby_code not in self.lobbies:
            return
            
        lobby = self.lobbies[lobby_code]
        
        # Check if player is host
        if lobby.host_id != player.id:
            await self.send_to_player(player,
                NetworkProtocol.create_message(
                    MessageType.START_GAME,
                    {'error': 'Only host can start game'}
                )
            )
            return
            
        # Check if all players are ready
        if not all(p.ready for p in lobby.players.values()):
            await self.send_to_player(player,
                NetworkProtocol.create_message(
                    MessageType.START_GAME,
                    {'error': 'Not all players ready'}
                )
            )
            return
            
        lobby.game_started = True
        
        logger.info(f"Game started in lobby {lobby_code}")
        
        # Notify all players
        await self.broadcast_to_lobby(lobby_code,
            NetworkProtocol.create_message(
                MessageType.START_GAME,
                {
                    'lobby_code': lobby_code,
                    'seed': int(datetime.now().timestamp())  # For synchronized randomness
                }
            )
        )
        
    async def handle_player_update(self, player: Player, data: Dict):
        """Handle player position/state update"""
        if not player.lobby_code:
            return
            
        # Update player state
        player.position = tuple(data.get('position', (0, 0)))
        player.health = data.get('health', 100)
        
        # Broadcast to other players in lobby
        lobby = self.lobbies.get(player.lobby_code)
        if lobby and lobby.game_started:
            # Send to all OTHER players
            for other_player in lobby.players.values():
                if other_player.id != player.id and other_player.connected:
                    await self.send_to_player(other_player, 
                        NetworkProtocol.create_message(
                            MessageType.PLAYER_UPDATE,
                            data
                        )
                    )
                    
    async def handle_player_action(self, player: Player, data: Dict):
        """Handle player action (attack, ability, etc)"""
        if not player.lobby_code:
            return
            
        lobby = self.lobbies.get(player.lobby_code)
        if lobby and lobby.game_started:
            # Broadcast action to all players (including sender for confirmation)
            await self.broadcast_to_lobby(player.lobby_code,
                NetworkProtocol.create_message(
                    MessageType.PLAYER_ACTION,
                    data
                )
            )
            
    async def handle_reconnect(self, player: Player, data: Dict):
        """Handle player reconnection"""
        lobby_code = data.get('lobby_code')
        
        if not lobby_code or lobby_code not in self.lobbies:
            await self.send_to_player(player,
                NetworkProtocol.create_message(
                    MessageType.RECONNECT,
                    {'error': 'Lobby not found'}
                )
            )
            return
            
        lobby = self.lobbies[lobby_code]
        
        # Check if player was in this lobby
        old_player_id = data.get('player_id')
        if old_player_id in lobby.players:
            # Update player reference
            old_player = lobby.players[old_player_id]
            player.character = old_player.character
            player.ready = old_player.ready
            
            # Replace old player with reconnected one
            del lobby.players[old_player_id]
            lobby.add_player(player)
            
            logger.info(f"Player {player.id} reconnected to lobby {lobby_code}")
            
            # Send current game state
            await self.send_to_player(player,
                NetworkProtocol.create_message(
                    MessageType.RECONNECT,
                    {
                        'status': 'reconnected',
                        'lobby_info': lobby.get_lobby_info(),
                        'game_state': lobby.game_state if lobby.game_started else None
                    }
                )
            )
            
            # Notify others
            await self.broadcast_to_lobby(lobby_code,
                NetworkProtocol.create_message(
                    MessageType.LOBBY_INFO,
                    lobby.get_lobby_info()
                ),
                exclude_player_id=player.id
            )
        else:
            # Try to join as new player
            await self.join_lobby(player, {'lobby_code': lobby_code})
            
    async def handle_ping(self, player: Player):
        """Handle ping from player"""
        player.last_ping = datetime.now()
        await self.send_to_player(player,
            NetworkProtocol.create_message(MessageType.PONG, {})
        )
        
    async def handle_disconnect(self, player: Player):
        """Handle player disconnect"""
        if player.id in self.players:
            del self.players[player.id]
            
        # Mark as disconnected but keep in lobby for reconnection
        if player.lobby_code and player.lobby_code in self.lobbies:
            lobby = self.lobbies[player.lobby_code]
            if player.id in lobby.players:
                lobby.players[player.id].connected = False
                
                # If game hasn't started, remove from lobby
                if not lobby.game_started:
                    await self.leave_lobby(player, {'lobby_code': player.lobby_code})
                else:
                    # Notify others of disconnect
                    await self.broadcast_to_lobby(player.lobby_code,
                        NetworkProtocol.create_message(
                            MessageType.DISCONNECT,
                            {'player_id': player.id}
                        )
                    )
                    
    async def broadcast_to_lobby(self, lobby_code: str, message: str, exclude_player_id: str = None):
        """Broadcast message to all players in lobby"""
        if lobby_code not in self.lobbies:
            return
            
        lobby = self.lobbies[lobby_code]
        for player in lobby.players.values():
            if player.connected and player.id != exclude_player_id:
                await self.send_to_player(player, message)
                
    async def send_to_player(self, player: Player, message: str):
        """Send message to specific player"""
        if player.connected and player.websocket:
            try:
                await player.websocket.send(message)
            except Exception as e:
                logger.error(f"Failed to send to {player.id}: {e}")
                player.connected = False
                
    async def send_lobby_list(self, player: Player):
        """Send list of active lobbies"""
        lobby_list = [
            {
                'code': lobby.code,
                'players': len(lobby.players),
                'max_players': lobby.max_players,
                'game_started': lobby.game_started,
                'host': lobby.host_id
            }
            for lobby in self.lobbies.values()
        ]
        
        await self.send_to_player(player,
            NetworkProtocol.create_message(
                MessageType.LOBBY_LIST,
                {'lobbies': lobby_list}
            )
        )
        
    def _generate_lobby_code(self) -> str:
        """Generate unique lobby code"""
        import random
        import string
        
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if code not in self.lobbies:
                return code
                
    async def periodic_cleanup(self):
        """Periodic cleanup of stale lobbies"""
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            
            # Remove empty lobbies older than 10 minutes
            now = datetime.now()
            stale_lobbies = []
            
            for code, lobby in self.lobbies.items():
                if not lobby.players:
                    age = (now - lobby.created_at).total_seconds()
                    if age > 600:  # 10 minutes
                        stale_lobbies.append(code)
                        
            for code in stale_lobbies:
                del self.lobbies[code]
                logger.info(f"Removed stale lobby {code}")
                
    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"Starting Heaven Burns Red server on {self.host}:{self.port}")
        logger.info(f"Maximum lobbies: {self.max_lobbies}")
        
        # Start cleanup task
        asyncio.create_task(self.periodic_cleanup())
        
        # Start server
        async with websockets.serve(
            self.handle_client, 
            self.host, 
            self.port,
            ping_interval=20,  # Send ping every 20 seconds
            ping_timeout=10    # Timeout after 10 seconds
        ):
            logger.info("Server started successfully!")
            logger.info(f"Players can connect to: ws://{self.host}:{self.port}")
            
            # Keep server running
            await asyncio.Future()
            
    def get_server_stats(self):
        """Get server statistics"""
        uptime = datetime.now() - self.start_time
        return {
            'uptime': str(uptime),
            'total_connections': self.total_connections,
            'active_players': len(self.players),
            'active_lobbies': len(self.lobbies),
            'lobbies': [
                {
                    'code': lobby.code,
                    'players': len(lobby.players),
                    'game_started': lobby.game_started
                }
                for lobby in self.lobbies.values()
            ]
        }

def main():
    """Main server entry point"""
    parser = argparse.ArgumentParser(description='Heaven Burns Red Game Server')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='Server port (default: 8080)')
    parser.add_argument('--max-lobbies', type=int, default=20, help='Maximum concurrent lobbies (default: 20)')
    
    args = parser.parse_args()
    
    # Create and start server
    server = GameServer(args.host, args.port)
    server.max_lobbies = args.max_lobbies
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        
        # Print final stats
        stats = server.get_server_stats()
        logger.info(f"Final statistics:")
        logger.info(f"  Total connections: {stats['total_connections']}")
        logger.info(f"  Server uptime: {stats['uptime']}")

if __name__ == "__main__":
    main()