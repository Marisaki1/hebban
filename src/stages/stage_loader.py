# src/stages/stage_loader.py
"""
Stage loading and management system for Heaven Burns Red
"""

import arcade
import random
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from src.entities.enemy import CancerEnemy, EnemySpawner
from src.systems.gravity import GravityManager, GravityMode

class StageType(Enum):
    """Types of stages"""
    COMBAT = "combat"
    ESCAPE = "escape"
    SURVIVAL = "survival"
    BOSS = "boss"
    COLLECTION = "collection"
    TUTORIAL = "tutorial"

class DifficultyLevel(Enum):
    """Difficulty levels"""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    NIGHTMARE = "nightmare"

@dataclass
class StageObjective:
    """Individual stage objective"""
    id: str
    description: str
    type: str  # "eliminate", "time_limit", "collect", "reach_point", "survive"
    target_value: Any = None
    current_value: Any = None
    completed: bool = False
    
    def check_completion(self, game_state: Dict) -> bool:
        """Check if objective is completed"""
        if self.completed:
            return True
            
        if self.type == "eliminate":
            # Target value is number of enemies to eliminate
            self.current_value = game_state.get('enemies_defeated', 0)
            self.completed = self.current_value >= self.target_value
            
        elif self.type == "time_limit":
            # Must complete within time limit
            self.current_value = game_state.get('elapsed_time', 0)
            # This is a constraint, not a goal - checked elsewhere
            
        elif self.type == "collect":
            # Collect certain number of items
            self.current_value = game_state.get('items_collected', 0)
            self.completed = self.current_value >= self.target_value
            
        elif self.type == "reach_point":
            # Reach specific coordinates
            player_pos = game_state.get('player_position', (0, 0))
            target_pos = self.target_value
            distance = ((player_pos[0] - target_pos[0])**2 + (player_pos[1] - target_pos[1])**2)**0.5
            self.completed = distance < 50  # Within 50 pixels
            
        elif self.type == "survive":
            # Survive for certain time
            self.current_value = game_state.get('elapsed_time', 0)
            self.completed = self.current_value >= self.target_value
            
        return self.completed

@dataclass
class WaveConfig:
    """Configuration for enemy wave"""
    wave_number: int
    enemies: List[Dict[str, Any]]  # List of enemy configs
    spawn_delay: float = 0.0
    spawn_interval: float = 2.0

@dataclass
class StageRewards:
    """Rewards for completing stage"""
    score_bonus: int = 0
    unlocks_stages: List[str] = None
    unlocks_characters: List[str] = None
    unlocks_squads: List[str] = None
    
    def __post_init__(self):
        if self.unlocks_stages is None:
            self.unlocks_stages = []
        if self.unlocks_characters is None:
            self.unlocks_characters = []
        if self.unlocks_squads is None:
            self.unlocks_squads = []

class StageBase:
    """Base class for all stages"""
    
    def __init__(self, stage_id: str, stage_data: Dict[str, Any]):
        self.stage_id = stage_id
        self.stage_data = stage_data
        
        # Basic stage info
        self.name = stage_data.get('name', 'Unnamed Stage')
        self.description = stage_data.get('description', 'No description')
        self.stage_type = StageType(stage_data.get('type', 'combat'))
        self.difficulty = DifficultyLevel(stage_data.get('difficulty', 'normal'))
        
        # Stage layout
        self.width = stage_data.get('width', 2000)
        self.height = stage_data.get('height', 800)
        self.background = stage_data.get('background', 'default_bg.png')
        self.music = stage_data.get('music', 'battle_theme.ogg')
        
        # Objectives
        self.objectives = []
        for obj_data in stage_data.get('objectives', []):
            self.objectives.append(StageObjective(
                id=obj_data.get('id', ''),
                description=obj_data.get('description', ''),
                type=obj_data.get('type', 'eliminate'),
                target_value=obj_data.get('target_value'),
                current_value=obj_data.get('current_value', 0)
            ))
            
        # Waves and enemies
        self.waves = []
        for wave_data in stage_data.get('waves', []):
            self.waves.append(WaveConfig(
                wave_number=wave_data.get('wave_number', 1),
                enemies=wave_data.get('enemies', []),
                spawn_delay=wave_data.get('spawn_delay', 0.0),
                spawn_interval=wave_data.get('spawn_interval', 2.0)
            ))
            
        # Platforms and environment
        self.platforms = stage_data.get('platforms', [])
        self.spawn_points = stage_data.get('spawn_points', [])
        self.player_spawn = stage_data.get('player_spawn', (200, 200))
        
        # Gravity zones
        self.gravity_zones = stage_data.get('gravity_zones', {})
        
        # Items and collectibles
        self.items = stage_data.get('items', [])
        
        # Time limits and constraints
        self.time_limit = stage_data.get('time_limit', None)
        self.par_time = stage_data.get('par_time', None)
        
        # Rewards
        rewards_data = stage_data.get('rewards', {})
        self.rewards = StageRewards(
            score_bonus=rewards_data.get('score_bonus', 0),
            unlocks_stages=rewards_data.get('unlocks_stages', []),
            unlocks_characters=rewards_data.get('unlocks_characters', []),
            unlocks_squads=rewards_data.get('unlocks_squads', [])
        )
        
        # Unlock conditions
        self.unlock_condition = stage_data.get('unlock_condition', 'default')
        self.required_stages = stage_data.get('required_stages', [])
        
        # Runtime state
        self.current_wave = 0
        self.is_completed = False
        self.is_failed = False
        self.start_time = 0
        self.completion_time = 0
        
    def is_unlocked(self, progress_data: Dict[str, Any]) -> bool:
        """Check if stage is unlocked"""
        if self.unlock_condition == 'default':
            return True
            
        completed_stages = progress_data.get('completed_stages', [])
        
        # Check required stages
        for required_stage in self.required_stages:
            if required_stage not in completed_stages:
                return False
                
        return True
        
    def check_objectives(self, game_state: Dict[str, Any]) -> Tuple[bool, bool]:
        """Check all objectives. Returns (all_completed, any_failed)"""
        all_completed = True
        any_failed = False
        
        for objective in self.objectives:
            objective.check_completion(game_state)
            
            if not objective.completed:
                all_completed = False
                
            # Check for failure conditions
            if objective.type == "time_limit" and objective.target_value:
                elapsed_time = game_state.get('elapsed_time', 0)
                if elapsed_time > objective.target_value:
                    any_failed = True
                    
        return all_completed, any_failed
        
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get summary of current progress"""
        completed_objectives = sum(1 for obj in self.objectives if obj.completed)
        total_objectives = len(self.objectives)
        
        return {
            'stage_id': self.stage_id,
            'name': self.name,
            'type': self.stage_type.value,
            'difficulty': self.difficulty.value,
            'objectives_completed': completed_objectives,
            'total_objectives': total_objectives,
            'progress_percent': (completed_objectives / max(total_objectives, 1)) * 100,
            'current_wave': self.current_wave,
            'total_waves': len(self.waves),
            'is_completed': self.is_completed,
            'is_failed': self.is_failed,
            'completion_time': self.completion_time
        }
        
    def load_platforms(self, platform_list: arcade.SpriteList, asset_manager):
        """Load platforms for this stage"""
        for platform_data in self.platforms:
            platform = asset_manager.create_sprite("platform")
            platform.center_x = platform_data.get('x', 0)
            platform.center_y = platform_data.get('y', 0)
            platform.scale = platform_data.get('scale', 1.0)
            
            # Set platform size if specified
            width = platform_data.get('width')
            height = platform_data.get('height')
            if width and height:
                # Create custom sized platform
                platform = asset_manager.create_sprite("platform")
                # Would need custom texture creation for different sizes
                
            platform_list.append(platform)
            
    def load_items(self, item_list: arcade.SpriteList, asset_manager):
        """Load collectible items for this stage"""
        from src.entities.items import HealthItem, CoinItem, PowerupItem
        
        for item_data in self.items:
            item_type = item_data.get('type', 'coin')
            x = item_data.get('x', 0)
            y = item_data.get('y', 0)
            
            if item_type == 'health':
                item = HealthItem(x, y, item_data.get('value', 20))
            elif item_type == 'coin':
                item = CoinItem(x, y, item_data.get('value', 10))
            elif item_type == 'powerup':
                item = PowerupItem(x, y, item_data.get('powerup_type', 'speed'))
            else:
                continue
                
            item_list.append(item)
            
    def setup_gravity_zones(self, gravity_manager: GravityManager):
        """Setup gravity zones for this stage"""
        for zone_id, zone_data in self.gravity_zones.items():
            if isinstance(zone_data, dict):
                gravity_mode = GravityMode(zone_data.get('type', 'normal'))
                gravity_manager.set_zone_gravity(zone_id, gravity_mode)
                
    def get_current_wave(self) -> Optional[WaveConfig]:
        """Get current wave configuration"""
        if self.current_wave < len(self.waves):
            return self.waves[self.current_wave]
        return None
        
    def advance_wave(self) -> bool:
        """Advance to next wave. Returns True if there is a next wave"""
        self.current_wave += 1
        return self.current_wave < len(self.waves)
        
    def spawn_wave_enemies(self, enemy_list: arcade.SpriteList, wave_config: WaveConfig):
        """Spawn enemies for a wave"""
        for enemy_data in wave_config.enemies:
            enemy = CancerEnemy(
                enemy_data.get('type', 'basic'),
                enemy_data.get('size', 'small')
            )
            enemy.center_x = enemy_data.get('x', 500)
            enemy.center_y = enemy_data.get('y', 200)
            
            # Apply difficulty multipliers
            difficulty_multipliers = {
                DifficultyLevel.EASY: 0.7,
                DifficultyLevel.NORMAL: 1.0,
                DifficultyLevel.HARD: 1.5,
                DifficultyLevel.NIGHTMARE: 2.0
            }
            
            multiplier = difficulty_multipliers[self.difficulty]
            enemy.health = int(enemy.health * multiplier)
            enemy.damage = int(enemy.damage * multiplier)
            
            enemy_list.append(enemy)

class StageLoader:
    """Loads and manages game stages"""
    
    def __init__(self):
        self.stages: Dict[str, StageBase] = {}
        self.stage_data: Dict[str, Dict] = {}
        self._load_stage_definitions()
        
    def _load_stage_definitions(self):
        """Load stage definitions from data files"""
        # Default stage data - in a full implementation, this would load from JSON files
        self.stage_data = {
            "chapter_1_day_1": {
                "name": "First Contact",
                "description": "The Cancer invasion begins - defend the city!",
                "type": "combat",
                "difficulty": "easy",
                "width": 2000,
                "height": 800,
                "background": "city_ruins_bg.png",
                "music": "battle_theme_1.ogg",
                "player_spawn": (200, 200),
                "objectives": [
                    {
                        "id": "eliminate_all",
                        "description": "Defeat all Cancer enemies",
                        "type": "eliminate",
                        "target_value": 15
                    },
                    {
                        "id": "time_bonus",
                        "description": "Complete in under 3 minutes",
                        "type": "time_limit",
                        "target_value": 180
                    }
                ],
                "waves": [
                    {
                        "wave_number": 1,
                        "spawn_delay": 2.0,
                        "enemies": [
                            {"type": "basic", "size": "small", "x": 600, "y": 200},
                            {"type": "basic", "size": "small", "x": 800, "y": 200},
                            {"type": "basic", "size": "small", "x": 1000, "y": 200}
                        ]
                    },
                    {
                        "wave_number": 2,
                        "spawn_delay": 10.0,
                        "enemies": [
                            {"type": "basic", "size": "small", "x": 1200, "y": 200},
                            {"type": "basic", "size": "medium", "x": 1400, "y": 200},
                            {"type": "basic", "size": "small", "x": 1600, "y": 200}
                        ]
                    },
                    {
                        "wave_number": 3,
                        "spawn_delay": 20.0,
                        "enemies": [
                            {"type": "basic", "size": "medium", "x": 700, "y": 200},
                            {"type": "basic", "size": "medium", "x": 900, "y": 200},
                            {"type": "basic", "size": "large", "x": 1100, "y": 200}
                        ]
                    }
                ],
                "platforms": [
                    {"x": 100, "y": 100, "width": 200, "height": 20},
                    {"x": 400, "y": 200, "width": 200, "height": 20},
                    {"x": 700, "y": 150, "width": 200, "height": 20},
                    {"x": 1000, "y": 250, "width": 200, "height": 20},
                    {"x": 1300, "y": 200, "width": 200, "height": 20},
                    {"x": 1600, "y": 300, "width": 200, "height": 20}
                ],
                "items": [
                    {"type": "health", "x": 500, "y": 350, "value": 20},
                    {"type": "coin", "x": 800, "y": 400, "value": 10},
                    {"type": "coin", "x": 1200, "y": 450, "value": 15}
                ],
                "gravity_zones": {
                    "default": "normal"
                },
                "time_limit": 300,
                "par_time": 180,
                "rewards": {
                    "score_bonus": 1000,
                    "unlocks_stages": ["chapter_1_day_2"]
                },
                "unlock_condition": "default"
            }
        }
        
    def load_stage(self, stage_id: str) -> Optional[StageBase]:
        """Load a stage by ID"""
        if stage_id in self.stages:
            return self.stages[stage_id]
            
        if stage_id not in self.stage_data:
            print(f"Warning: Stage {stage_id} not found in stage data")
            return None
            
        try:
            stage = StageBase(stage_id, self.stage_data[stage_id])
            self.stages[stage_id] = stage
            return stage
        except Exception as e:
            print(f"Error loading stage {stage_id}: {e}")
            return None
            
    def get_available_stages(self, progress_data: Dict[str, Any]) -> List[str]:
        """Get list of stages available to play"""
        available = []
        
        for stage_id, stage_data in self.stage_data.items():
            stage = self.load_stage(stage_id)
            if stage and stage.is_unlocked(progress_data):
                available.append(stage_id)
                
        return available
        
    def get_chapter_stages(self, chapter: int) -> Dict[str, Any]:
        """Get all stages for a specific chapter"""
        chapter_stages = {}
        
        for stage_id, stage_data in self.stage_data.items():
            if stage_id.startswith(f"chapter_{chapter}_"):
                day = int(stage_id.split("_")[-1])
                chapter_stages[day] = {
                    'id': stage_id,
                    'name': stage_data.get('name', 'Unnamed Stage'),
                    'description': stage_data.get('description', ''),
                    'difficulty': stage_data.get('difficulty', 'normal'),
                    'type': stage_data.get('type', 'combat')
                }
                
        return dict(sorted(chapter_stages.items()))
        
    def get_stage_progress(self, stage_id: str, save_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get progress information for a stage"""
        progress = save_data.get('stage_progress', {})
        stage_progress = progress.get(stage_id, {})
        
        return {
            'completed': stage_progress.get('completed', False),
            'best_time': stage_progress.get('best_time', None),
            'best_score': stage_progress.get('best_score', 0),
            'stars_earned': stage_progress.get('stars_earned', 0),
            'attempts': stage_progress.get('attempts', 0)
        }
        
    def update_stage_progress(self, stage_id: str, save_data: Dict[str, Any], 
                            completion_time: float, score: int, completed: bool = True):
        """Update progress for a completed stage"""
        if 'stage_progress' not in save_data:
            save_data['stage_progress'] = {}
            
        if stage_id not in save_data['stage_progress']:
            save_data['stage_progress'][stage_id] = {}
            
        progress = save_data['stage_progress'][stage_id]
        
        # Update completion
        if completed:
            progress['completed'] = True
            
            # Update best times and scores
            if 'best_time' not in progress or completion_time < progress['best_time']:
                progress['best_time'] = completion_time
                
            if score > progress.get('best_score', 0):
                progress['best_score'] = score
                
        # Increment attempts
        progress['attempts'] = progress.get('attempts', 0) + 1
        
        # Calculate stars (1-3 based on performance)
        stage = self.load_stage(stage_id)
        if stage and completed:
            stars = 1  # Base completion star
            
            # Time bonus star
            if stage.par_time and completion_time <= stage.par_time:
                stars += 1
                
            # High score star (placeholder logic)
            if score >= 5000:  # Arbitrary high score threshold
                stars += 1
                
            progress['stars_earned'] = max(progress.get('stars_earned', 0), stars)

# Global stage loader instance
stage_loader = StageLoader()