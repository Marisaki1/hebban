# src/networking/protocol.py
"""
Network protocol for game communication
"""

from datetime import datetime
import json
from enum import Enum
from typing import Dict, Any

class MessageType(Enum):
    """Network message types"""
    # Connection
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    RECONNECT = "reconnect"
    PING = "ping"
    PONG = "pong"
    
    # Lobby
    CREATE_LOBBY = "create_lobby"
    JOIN_LOBBY = "join_lobby"
    LEAVE_LOBBY = "leave_lobby"
    LOBBY_INFO = "lobby_info"
    LOBBY_LIST = "lobby_list"
    PLAYER_READY = "player_ready"
    START_GAME = "start_game"
    HOST_CHANGE = "host_change"
    
    # Game
    PLAYER_UPDATE = "player_update"
    ENEMY_UPDATE = "enemy_update"
    GAME_STATE = "game_state"
    PLAYER_ACTION = "player_action"
    ITEM_SPAWN = "item_spawn"
    ITEM_COLLECT = "item_collect"
    GAME_OVER = "game_over"
    
    # Chat
    CHAT_MESSAGE = "chat_message"
    
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
    def create_player_update(player_id: str, position: tuple, velocity: tuple, 
                           state: str, health: int = 100) -> str:
        """Create player update message"""
        return NetworkProtocol.create_message(
            MessageType.PLAYER_UPDATE,
            {
                'player_id': player_id,
                'position': position,
                'velocity': velocity,
                'state': state,
                'health': health,
                'facing_right': True  # Add facing direction
            }
        )
        
    @staticmethod
    def create_enemy_update(enemies: list) -> str:
        """Create enemy update message"""
        enemy_data = []
        for enemy in enemies:
            enemy_data.append({
                'id': id(enemy),  # Unique ID
                'type': enemy.enemy_type,
                'size': enemy.size,
                'position': (enemy.center_x, enemy.center_y),
                'health': enemy.health,
                'state': enemy.ai_state
            })
            
        return NetworkProtocol.create_message(
            MessageType.ENEMY_UPDATE,
            {'enemies': enemy_data}
        )
        
    @staticmethod
    def create_game_state(game_data: dict) -> str:
        """Create full game state message"""
        return NetworkProtocol.create_message(
            MessageType.GAME_STATE,
            game_data
        )