# src/networking/client.py - Fixed version
"""
WebSocket game client for multiplayer - FIXED
"""

import asyncio
import websockets
import json
from typing import Dict, Set, Optional, Callable
from src.networking.protocol import NetworkProtocol, MessageType

class GameClient:
    """WebSocket game client for multiplayer - FIXED"""
    
    def __init__(self):
        self.websocket = None
        self.connected = False
        self.player_id = None
        self.lobby_code = None
        self.message_queue = asyncio.Queue()
        self.running = False
        self.connection_uri = None
        
        # Callbacks for game events
        self.callbacks = {
            MessageType.CONNECT: [],
            MessageType.DISCONNECT: [],
            MessageType.LOBBY_INFO: [],
            MessageType.PLAYER_UPDATE: [],
            MessageType.GAME_STATE: [],
            MessageType.PING: [],
            MessageType.PLAYER_READY: [],
            MessageType.START_GAME: [],
            MessageType.HOST_CHANGE: [],
            MessageType.ENEMY_UPDATE: [],
            MessageType.PLAYER_ACTION: []
        }
        
    def register_callback(self, msg_type: MessageType, callback: Callable):
        """Register callback for message type"""
        if msg_type in self.callbacks:
            self.callbacks[msg_type].append(callback)
            
    async def connect(self, host: str, port: int, player_id: str, player_name: str = "Player"):
        """Connect to game server"""
        self.connection_uri = f"ws://{host}:{port}"
        self.player_id = player_id
        
        try:
            self.websocket = await websockets.connect(self.connection_uri)
            self.connected = True
            self.running = True
            
            # Send connect message with player info
            await self.websocket.send(
                NetworkProtocol.create_message(
                    MessageType.CONNECT,
                    {
                        'player_id': player_id,
                        'player_name': player_name,
                        'version': '1.0.0'
                    }
                )
            )
            
            # Start listening for messages
            asyncio.create_task(self.listen())
            
            return True
            
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            self.connected = False
            return False
            
    async def listen(self):
        """Listen for messages from server"""
        try:
            while self.running and self.websocket:
                message = await self.websocket.recv()
                await self.message_queue.put(message)
                
                # Process message immediately
                msg_type, data = NetworkProtocol.parse_message(message)
                if msg_type and msg_type in self.callbacks:
                    for callback in self.callbacks[msg_type]:
                        try:
                            callback(data)
                        except Exception as e:
                            print(f"Error in callback for {msg_type}: {e}")
                            
        except websockets.exceptions.ConnectionClosed:
            print("Connection to server lost")
            self.connected = False
            self.running = False
            
            # Notify disconnection
            for callback in self.callbacks[MessageType.DISCONNECT]:
                callback({'reason': 'connection_lost'})
                
        except Exception as e:
            print(f"Error in listen loop: {e}")
            self.connected = False
            self.running = False
            
    async def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
        self.connected = False
        self.websocket = None
        
    async def send_message(self, message: str):
        """Send message to server"""
        if self.connected and self.websocket:
            try:
                await self.websocket.send(message)
            except Exception as e:
                print(f"Failed to send message: {e}")
                
    async def create_lobby_with_character(self, lobby_code: str, max_players: int = 6, character_data: dict = None):
        """Create new lobby with character data"""
        await self.send_message(
            NetworkProtocol.create_message(
                MessageType.CREATE_LOBBY,
                {
                    'lobby_code': lobby_code,
                    'max_players': max_players,
                    'character': character_data
                }
            )
        )
        self.lobby_code = lobby_code
        
    async def join_lobby(self, lobby_code: str, character_data: dict = None):
        """Join existing lobby"""
        await self.send_message(
            NetworkProtocol.create_message(
                MessageType.JOIN_LOBBY,
                {
                    'lobby_code': lobby_code,
                    'character': character_data
                }
            )
        )
        self.lobby_code = lobby_code
        
    async def leave_lobby(self):
        """Leave current lobby"""
        if self.lobby_code:
            await self.send_message(
                NetworkProtocol.create_message(
                    MessageType.LEAVE_LOBBY,
                    {'lobby_code': self.lobby_code}
                )
            )
            self.lobby_code = None
            
    async def set_ready(self, ready: bool):
        """Set ready state in lobby"""
        await self.send_message(
            NetworkProtocol.create_message(
                MessageType.PLAYER_READY,
                {
                    'ready': ready,
                    'lobby_code': self.lobby_code
                }
            )
        )
        
    async def start_game(self):
        """Start game (host only)"""
        await self.send_message(
            NetworkProtocol.create_message(
                MessageType.START_GAME,
                {'lobby_code': self.lobby_code}
            )
        )
        
    async def send_player_update(self, position: tuple, velocity: tuple, state: str, health: int = 100):
        """Send player position/state update"""
        await self.send_message(
            NetworkProtocol.create_player_update(
                self.player_id, position, velocity, state, health
            )
        )
        
    async def send_player_action(self, action: str, data: dict = None):
        """Send player action (attack, ability, etc)"""
        await self.send_message(
            NetworkProtocol.create_message(
                MessageType.PLAYER_ACTION,
                {
                    'player_id': self.player_id,
                    'action': action,
                    'data': data or {}
                }
            )
        )
        
    async def reconnect(self, lobby_code: str):
        """Attempt to reconnect to a lobby"""
        if not self.connected and self.connection_uri:
            # Try to reconnect
            success = await self.connect(
                self.connection_uri.split("://")[1].split(":")[0],
                int(self.connection_uri.split(":")[-1]),
                self.player_id
            )
            
            if success:
                # Rejoin the lobby
                await self.send_message(
                    NetworkProtocol.create_message(
                        MessageType.RECONNECT,
                        {
                            'lobby_code': lobby_code,
                            'player_id': self.player_id
                        }
                    )
                )
                return True
        return False