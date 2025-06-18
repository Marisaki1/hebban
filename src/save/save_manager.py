# ============================================================================
# FILE: src/save/save_manager.py
# ============================================================================
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import hashlib

class SaveData:
    """Container for save game data"""
    def __init__(self):
        self.save_id = self._generate_save_id()
        self.timestamp = datetime.now().isoformat()
        self.game_data = {
            'version': '1.0.0',
            'player_name': 'Player',
            'selected_squad': None,
            'selected_character': None,
            'unlocked_squads': ['31A'],  # Default unlocked squad
            'progress': {
                'current_level': 1,
                'completed_levels': [],
                'total_score': 0,
                'play_time': 0
            },
            'settings': {
                'master_volume': 1.0,
                'sfx_volume': 1.0,
                'music_volume': 1.0,
                'controls': {}
            }
        }
        
    def _generate_save_id(self) -> str:
        """Generate unique save ID"""
        timestamp = str(datetime.now().timestamp())
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]

class SaveManager:
    """Manages game saves with support for multiple slots"""
    def __init__(self, save_directory: str = "saves"):
        self.save_directory = save_directory
        self.current_save: Optional[SaveData] = None
        self.save_slots = 3
        self._ensure_save_directory()
        
    def _ensure_save_directory(self):
        """Ensure save directory exists"""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
            
    def get_save_files(self) -> List[Dict]:
        """Get list of available save files"""
        saves = []
        for i in range(1, self.save_slots + 1):
            filename = f"save_slot_{i}.json"
            filepath = os.path.join(self.save_directory, filename)
            
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        saves.append({
                            'slot': i,
                            'exists': True,
                            'data': data,
                            'timestamp': data.get('timestamp', 'Unknown')
                        })
                except:
                    saves.append({'slot': i, 'exists': False})
            else:
                saves.append({'slot': i, 'exists': False})
                
        return saves
        
    def save_game(self, slot: int) -> bool:
        """Save game to specified slot"""
        if not 1 <= slot <= self.save_slots:
            return False
            
        if not self.current_save:
            self.current_save = SaveData()
            
        filename = f"save_slot_{slot}.json"
        filepath = os.path.join(self.save_directory, filename)
        
        try:
            # Update timestamp
            self.current_save.timestamp = datetime.now().isoformat()
            
            # Save to file
            save_dict = {
                'save_id': self.current_save.save_id,
                'timestamp': self.current_save.timestamp,
                'game_data': self.current_save.game_data
            }
            
            with open(filepath, 'w') as f:
                json.dump(save_dict, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
            
    def load_game(self, slot: int) -> bool:
        """Load game from specified slot"""
        if not 1 <= slot <= self.save_slots:
            return False
            
        filename = f"save_slot_{slot}.json"
        filepath = os.path.join(self.save_directory, filename)
        
        if not os.path.exists(filepath):
            return False
            
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            self.current_save = SaveData()
            self.current_save.save_id = data['save_id']
            self.current_save.timestamp = data['timestamp']
            self.current_save.game_data = data['game_data']
            
            return True
        except Exception as e:
            print(f"Error loading game: {e}")
            return False
            
    def delete_save(self, slot: int) -> bool:
        """Delete save from specified slot"""
        if not 1 <= slot <= self.save_slots:
            return False
            
        filename = f"save_slot_{slot}.json"
        filepath = os.path.join(self.save_directory, filename)
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            return True
        except:
            return False