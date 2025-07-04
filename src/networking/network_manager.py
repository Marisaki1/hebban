# src/networking/network_manager.py
"""
Fixed network manager with proper connection handling
"""

import asyncio
import threading
from typing import Optional, Dict, Callable, List
from src.networking.client import GameClient
from src.networking.protocol import MessageType
import uuid

class NetworkManager:
    """Fixed network manager with proper state management"""
    
    def __init__(self):
        self.client = GameClient()
        self.is_connected = False
        self.is_host = False
        self.player_id = str(uuid.uuid4())[:8]
        self.player_name = "Player"
        self.lobby_info = None
        self.other_players = {}
        
        # Asyncio setup
        self.loop = None
        self.thread = None
        
        # Connection state
        self.is_connecting = False
        self.connection_failed = False
        
        # Callbacks
        self._on_lobby_update = None
        self._on_game_start = None
        self._on_player_update = None
        self._on_disconnect = None
        self._on_host_change = None
        
    def start(self, server_host: str = "localhost", server_port: int = 8080):
        """Start network manager"""
        if self.is_connecting or self.is_connected:
            print("Already connecting or connected")
            return
            
        self.is_connecting = True
        self.connection_failed = False
        
        # Clean up old thread if exists
        if self.thread and self.thread.is_alive():
            self.stop()
            
        self.thread = threading.Thread(target=self._run_async_loop, args=(server_host, server_port))
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        """Stop network manager"""
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)
            self.loop.call_soon_threadsafe(self.loop.stop)
            
        if self.thread:
            self.thread.join(timeout=1.0)
            
        self.is_connected = False
        self.is_connecting = False
        self.loop = None
        self.thread = None
        
    def _run_async_loop(self, host: str, port: int):
        """Run asyncio loop in separate thread"""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Connect to server
            self.loop.run_until_complete(self._connect(host, port))
            
            # Keep running if connected
            if self.is_connected:
                self.loop.run_forever()
            else:
                self.connection_failed = True
                
        except Exception as e:
            print(f"Network thread error: {e}")
            self.connection_failed = True
        finally:
            self.is_connecting = False
            
    async def _connect(self, host: str, port: int):
        """Connect to server"""
        try:
            # Register callbacks first
            self.client.register_callback(MessageType.LOBBY_INFO, self._handle_lobby_info)
            self.client.register_callback(MessageType.START_GAME, self._handle_game_start)
            self.client.register_callback(MessageType.PLAYER_UPDATE, self._handle_player_update)
            self.client.register_callback(MessageType.DISCONNECT, self._handle_disconnect)
            self.client.register_callback(MessageType.HOST_CHANGE, self._handle_host_change)
            self.client.register_callback(MessageType.CONNECT, self._handle_connect_response)
            
            # Connect
            success = await self.client.connect(host, port, self.player_id, self.player_name)
            
            if success:
                self.is_connected = True
                print(f"✓ Connected to server at {host}:{port}")
            else:
                self.is_connected = False
                self.connection_failed = True
                print(f"✗ Failed to connect to server at {host}:{port}")
                
        except Exception as e:
            print(f"Connection error: {e}")
            self.is_connected = False
            self.connection_failed = True
            
    def _handle_connect_response(self, data: dict):
        """Handle connection response"""
        if data.get('status') == 'connected':
            self.is_connected = True
            print("✓ Connection confirmed by server")
            
    def create_lobby(self, lobby_code: str):
        """Create a new lobby"""
        if self.is_connected and self.loop:
            self.is_host = True
            asyncio.run_coroutine_threadsafe(
                self.client.create_lobby(lobby_code, 6),
                self.loop
            ).result(timeout=1.0)
            
    def join_lobby(self, lobby_code: str, character_data: dict = None):
        """Join existing lobby"""
        if self.is_connected and self.loop:
            self.is_host = False
            asyncio.run_coroutine_threadsafe(
                self.client.join_lobby(lobby_code, character_data),
                self.loop
            ).result(timeout=1.0)
            
    def leave_lobby(self):
        """Leave current lobby"""
        if self.is_connected and self.loop:
            asyncio.run_coroutine_threadsafe(
                self.client.leave_lobby(),
                self.loop
            ).result(timeout=1.0)
            self.lobby_info = None
            self.is_host = False
            
    def set_ready(self, ready: bool):
        """Set ready state"""
        if self.is_connected and self.loop:
            asyncio.run_coroutine_threadsafe(
                self.client.set_ready(ready),
                self.loop
            ).result(timeout=1.0)
            
    def start_game(self):
        """Start game (host only)"""
        if self.is_connected and self.loop and self.is_host:
            asyncio.run_coroutine_threadsafe(
                self.client.start_game(),
                self.loop
            ).result(timeout=1.0)
            
    def send_player_update(self, position: tuple, velocity: tuple, state: str, health: int):
        """Send player update"""
        if self.is_connected and self.loop:
            # Fire and forget - don't wait for result
            asyncio.run_coroutine_threadsafe(
                self.client.send_player_update(position, velocity, state, health),
                self.loop
            )
            
    def send_player_action(self, action: str, data: dict = None):
        """Send player action"""
        if self.is_connected and self.loop:
            # Fire and forget - don't wait for result
            asyncio.run_coroutine_threadsafe(
                self.client.send_player_action(action, data),
                self.loop
            )
            
    def disconnect(self):
        """Disconnect from server"""
        self.stop()
        
    # Callbacks
    def set_lobby_update_callback(self, callback: Callable):
        """Set callback for lobby updates"""
        self._on_lobby_update = callback
        
    def set_game_start_callback(self, callback: Callable):
        """Set callback for game start"""
        self._on_game_start = callback
        
    def set_player_update_callback(self, callback: Callable):
        """Set callback for player updates"""
        self._on_player_update = callback
        
    def set_disconnect_callback(self, callback: Callable):
        """Set callback for disconnection"""
        self._on_disconnect = callback
        
    def set_host_change_callback(self, callback: Callable):
        """Set callback for host change"""
        self._on_host_change = callback
        
    # Handlers
    def _handle_lobby_info(self, data: dict):
        """Handle lobby info update"""
        self.lobby_info = data
        if self._on_lobby_update:
            self._on_lobby_update(data)
            
    def _handle_game_start(self, data: dict):
        """Handle game start"""
        if self._on_game_start:
            self._on_game_start(data)
            
    def _handle_player_update(self, data: dict):
        """Handle player update"""
        player_id = data.get('player_id')
        if player_id and player_id != self.player_id:
            self.other_players[player_id] = data
            
        if self._on_player_update:
            self._on_player_update(data)
            
    def _handle_disconnect(self, data: dict):
        """Handle disconnection"""
        self.is_connected = False
        if self._on_disconnect:
            self._on_disconnect(data)
            
    def _handle_host_change(self, data: dict):
        """Handle host change"""
        new_host_id = data.get('new_host_id')
        if new_host_id == self.player_id:
            self.is_host = True
            
        if self._on_host_change:
            self._on_host_change(data)