# ============================================================================
# FILE: src/networking/client.py
# ============================================================================
class GameClient:
    """WebSocket game client"""
    def __init__(self):
        self.websocket = None
        self.connected = False
        self.player_id = None
        self.lobby_code = None
        self.message_queue = asyncio.Queue()
        
    async def connect(self, host='localhost', port=8080, player_id='player1'):
        """Connect to game server"""
        uri = f"ws://{host}:{port}"
        self.player_id = player_id
        
        try:
            self.websocket = await websockets.connect(uri)
            self.connected = True
            
            # Send connect message
            await self.websocket.send(
                NetworkProtocol.create_message(
                    MessageType.CONNECT,
                    {'player_id': player_id}
                )
            )
            
            # Start listening for messages
            asyncio.create_task(self.listen())
            
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.connected = False
            
    async def listen(self):
        """Listen for messages from server"""
        try:
            async for message in self.websocket:
                await self.message_queue.put(message)
        except websockets.exceptions.ConnectionClosed:
            self.connected = False
            
    async def send_message(self, message: str):
        """Send message to server"""
        if self.connected and self.websocket:
            await self.websocket.send(message)
            
    async def create_lobby(self, lobby_code: str):
        """Create new lobby"""
        await self.send_message(
            NetworkProtocol.create_message(
                MessageType.CREATE_LOBBY,
                {'lobby_code': lobby_code}
            )
        )
        self.lobby_code = lobby_code
        
    async def join_lobby(self, lobby_code: str):
        """Join existing lobby"""
        await self.send_message(
            NetworkProtocol.create_message(
                MessageType.JOIN_LOBBY,
                {'lobby_code': lobby_code}
            )
        )
        self.lobby_code = lobby_code
        
    async def send_player_update(self, position: tuple, velocity: tuple, state: str):
        """Send player position update"""
        await self.send_message(
            NetworkProtocol.create_player_update(
                self.player_id, position, velocity, state
            )
        )
        
    async def process_messages(self, game_state):
        """Process incoming messages"""
        while not self.message_queue.empty():
            message = await self.message_queue.get()
            msg_type, data = NetworkProtocol.parse_message(message)
            
            if msg_type == MessageType.PLAYER_UPDATE:
                # Update other player positions
                player_id = data['player_id']
                if player_id != self.player_id:
                    game_state.update_player(player_id, data)
            elif msg_type == MessageType.LOBBY_INFO:
                # Update lobby state
                game_state.update_lobby(data)