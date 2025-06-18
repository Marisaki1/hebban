# ============================================================================
# FILE: src/networking/protocol.py
# ============================================================================
import json
from enum import Enum
from typing import Dict, Any

class MessageType(Enum):
    """Network message types"""
    # Connection
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"
    
    # Lobby
    CREATE_LOBBY = "create_lobby"
    JOIN_LOBBY = "join_lobby"
    LOBBY_INFO = "lobby_info"
    PLAYER_READY = "player_ready"
    START_GAME = "start_game"
    
    # Game
    PLAYER_UPDATE = "player_update"
    ENEMY_UPDATE = "enemy_update"
    GAME_STATE = "game_state"
    PLAYER_ACTION = "player_action"
    
class NetworkProtocol:
    """Network protocol for game communication"""
    
    @staticmethod
    def create_message(msg_type: MessageType, data: Dict[str, Any]) -> str:
        """Create network message"""
        message = {
            'type': msg_type.value,
            'data': data,
            'timestamp': datetime.now().timestamp()
        }
        return json.dumps(message)
        
    @staticmethod
    def parse_message(message: str) -> tuple:
        """Parse network message"""
        try:
            data = json.loads(message)
            msg_type = MessageType(data['type'])
            return msg_type, data['data']
        except:
            return None, None
            
    @staticmethod
    def create_player_update(player_id: str, position: tuple, velocity: tuple, state: str) -> str:
        """Create player update message"""
        return NetworkProtocol.create_message(
            MessageType.PLAYER_UPDATE,
            {
                'player_id': player_id,
                'position': position,
                'velocity': velocity,
                'state': state
            }
        )