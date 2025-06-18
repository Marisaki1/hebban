# ============================================================================
# FILE: src/networking/server.py
# ============================================================================
import asyncio
import websockets
import json
from typing import Dict, Set
from src.networking.protocol import NetworkProtocol, MessageType

class GameServer:
    """WebSocket game server for multiplayer"""
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.lobbies: Dict[str, Dict] = {}
        self.player_data: Dict[str, Dict] = {}
        
    async def handle_client(self, websocket, path):
        """Handle client connection"""
        client_id = None
        try:
            # Wait for connect message
            message = await websocket.recv()
            msg_type, data = NetworkProtocol.parse_message(message)
            
            if msg_type == MessageType.CONNECT:
                client_id = data['player_id']
                self.clients[client_id] = websocket
                print(f"Player {client_id} connected")
                
                # Send confirmation
                await websocket.send(
                    NetworkProtocol.create_message(
                        MessageType.CONNECT,
                        {'status': 'connected', 'player_id': client_id}
                    )
                )
                
            # Handle messages
            async for message in websocket:
                await self.handle_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            print(f"Player {client_id} disconnected")
        finally:
            if client_id:
                await self.handle_disconnect(client_id)
                
    async def handle_message(self, client_id: str, message: str):
        """Handle incoming message from client"""
        msg_type, data = NetworkProtocol.parse_message(message)
        
        if msg_type == MessageType.CREATE_LOBBY:
            await self.create_lobby(client_id, data)
        elif msg_type == MessageType.JOIN_LOBBY:
            await self.join_lobby(client_id, data)
        elif msg_type == MessageType.PLAYER_READY:
            await self.player_ready(client_id, data)
        elif msg_type == MessageType.PLAYER_UPDATE:
            await self.broadcast_player_update(client_id, data)
            
    async def create_lobby(self, host_id: str, data: Dict):
        """Create new lobby"""
        lobby_code = data['lobby_code']
        
        self.lobbies[lobby_code] = {
            'host': host_id,
            'players': [host_id],
            'ready_states': {host_id: False},
            'game_started': False
        }
        
        # Send lobby info to host
        await self.send_to_client(
            host_id,
            NetworkProtocol.create_message(
                MessageType.LOBBY_INFO,
                {
                    'lobby_code': lobby_code,
                    'players': self.lobbies[lobby_code]['players'],
                    'ready_states': self.lobbies[lobby_code]['ready_states']
                }
            )
        )
        
    async def join_lobby(self, player_id: str, data: Dict):
        """Join existing lobby"""
        lobby_code = data['lobby_code']
        
        if lobby_code not in self.lobbies:
            await self.send_to_client(
                player_id,
                NetworkProtocol.create_message(
                    MessageType.LOBBY_INFO,
                    {'error': 'Lobby not found'}
                )
            )
            return
            
        lobby = self.lobbies[lobby_code]
        if len(lobby['players']) >= 8:
            await self.send_to_client(
                player_id,
                NetworkProtocol.create_message(
                    MessageType.LOBBY_INFO,
                    {'error': 'Lobby full'}
                )
            )
            return
            
        # Add player to lobby
        lobby['players'].append(player_id)
        lobby['ready_states'][player_id] = False
        
        # Broadcast updated lobby info
        await self.broadcast_to_lobby(
            lobby_code,
            NetworkProtocol.create_message(
                MessageType.LOBBY_INFO,
                {
                    'lobby_code': lobby_code,
                    'players': lobby['players'],
                    'ready_states': lobby['ready_states']
                }
            )
        )
        
    async def broadcast_to_lobby(self, lobby_code: str, message: str):
        """Broadcast message to all players in lobby"""
        if lobby_code not in self.lobbies:
            return
            
        lobby = self.lobbies[lobby_code]
        for player_id in lobby['players']:
            if player_id in self.clients:
                await self.send_to_client(player_id, message)
                
    async def send_to_client(self, client_id: str, message: str):
        """Send message to specific client"""
        if client_id in self.clients:
            try:
                await self.clients[client_id].send(message)
            except:
                # Client disconnected
                await self.handle_disconnect(client_id)
                
    async def handle_disconnect(self, client_id: str):
        """Handle client disconnect"""
        # Remove from clients
        if client_id in self.clients:
            del self.clients[client_id]
            
        # Remove from lobbies
        for lobby_code, lobby in list(self.lobbies.items()):
            if client_id in lobby['players']:
                lobby['players'].remove(client_id)
                if client_id in lobby['ready_states']:
                    del lobby['ready_states'][client_id]
                    
                # If host left, close lobby
                if lobby['host'] == client_id:
                    del self.lobbies[lobby_code]
                else:
                    # Notify remaining players
                    await self.broadcast_to_lobby(
                        lobby_code,
                        NetworkProtocol.create_message(
                            MessageType.DISCONNECT,
                            {'player_id': client_id}
                        )
                    )
                    
    async def start_server(self):
        """Start the WebSocket server"""
        print(f"Starting server on {self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever