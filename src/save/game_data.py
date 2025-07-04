# src/save/game_data.py
"""
Fixed save game data structure
"""

from datetime import datetime
from typing import Dict, Any, List

class GameData:
    """Container for all game save data"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.created_at = datetime.now().isoformat()
        self.last_saved = datetime.now().isoformat()
        
        # Player data
        self.player_data = {
            'name': 'Player',
            'player_id': None,
            'total_playtime': 0,
            'achievements': []
        }
        
        # Single player progress
        self.single_player = {
            'selected_squad': '31A',
            'selected_character': 'ruka',
            'current_level': 1,
            'current_wave': 1,
            'completed_levels': [],
            'high_scores': {},
            'unlocked_squads': ['31A'],
            'unlocked_characters': []
        }
        
        # Multiplayer data
        self.multiplayer = {
            'last_lobby_code': None,
            'favorite_character': None,
            'stats': {
                'games_played': 0,
                'games_won': 0,
                'total_score': 0,
                'enemies_defeated': 0
            }
        }
        
        # Settings
        self.settings = {
            'master_volume': 1.0,
            'sfx_volume': 1.0,
            'music_volume': 0.8,
            'controls': {},
            'graphics': {
                'resolution': '1280x720',
                'fullscreen': False,
                'vsync': True
            },
            'network': {
                'last_server': 'localhost:8080',
                'player_name': 'Player'
            }
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving"""
        return {
            'version': self.version,
            'created_at': self.created_at,
            'last_saved': datetime.now().isoformat(),
            'player_data': self.player_data,
            'single_player': self.single_player,
            'multiplayer': self.multiplayer,
            'settings': self.settings
        }
        
    def from_dict(self, data: Dict[str, Any]):
        """Load from dictionary"""
        self.version = data.get('version', '1.0.0')
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.last_saved = data.get('last_saved', datetime.now().isoformat())
        
        # Load each section with defaults
        self.player_data = data.get('player_data', self.player_data)
        self.single_player = data.get('single_player', self.single_player)
        self.multiplayer = data.get('multiplayer', self.multiplayer)
        self.settings = data.get('settings', self.settings)
        
    def get_selected_character(self) -> tuple:
        """Get currently selected squad and character"""
        return (
            self.single_player.get('selected_squad', '31A'),
            self.single_player.get('selected_character', 'ruka')
        )
        
    def set_selected_character(self, squad_id: str, character_id: str):
        """Set selected squad and character"""
        self.single_player['selected_squad'] = squad_id
        self.single_player['selected_character'] = character_id
        
    def update_multiplayer_stats(self, stats: Dict[str, Any]):
        """Update multiplayer statistics"""
        mp_stats = self.multiplayer['stats']
        for key, value in stats.items():
            if key in mp_stats:
                mp_stats[key] += value