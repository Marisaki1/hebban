# src/stages/stage_data.py
"""
Stage data definitions for all chapters and days
"""

from enum import Enum
from typing import Dict, List, Optional, Any

class StageType(Enum):
    """Types of stages"""
    COMBAT = "combat"
    ESCAPE = "escape"
    SURVIVAL = "survival"
    BOSS = "boss"
    COLLECTION = "collection"

# Stage data structure
CHAPTERS = {
    "chapter_1": {
        "id": "chapter_1",
        "name": "First Contact",
        "description": "The Cancer invasion begins. 31A Squad's first deployment.",
        "unlock_condition": "default",
        "days": {
            "day_1": {
                "id": "day_1",
                "name": "Day 1 - City Under Siege",
                "description": "Defend the city from the initial Cancer attack",
                "type": StageType.COMBAT,
                "unlock_condition": "default",
                "map": "city_ruins",
                "music": "battle_theme",
                "gravity_zones": {
                    "default": "normal",
                    "zone_1": {"type": "low", "area": [1000, 0, 1500, 500]}
                },
                "enemy_waves": [
                    {
                        "trigger": "start",
                        "enemies": [
                            {"type": "cancer_small", "position": [500, 200], "count": 3},
                            {"type": "cancer_small", "position": [800, 200], "count": 2}
                        ]
                    },
                    {
                        "trigger": "timer",
                        "delay": 30,
                        "enemies": [
                            {"type": "cancer_medium", "position": [1000, 300], "count": 2},
                            {"type": "cancer_small", "position": [700, 200], "count": 3}
                        ]
                    }
                ],
                "win_conditions": {
                    "primary": {
                        "type": "eliminate_all",
                        "description": "Defeat all Cancers"
                    },
                    "bonus": [
                        {
                            "type": "time_limit",
                            "description": "Complete in under 3 minutes",
                            "time": 180
                        },
                        {
                            "type": "no_damage",
                            "description": "Complete without taking damage"
                        }
                    ]
                },
                "rewards": {
                    "score": 1000,
                    "unlock_next": "day_2"
                }
            },
            "day_2": {
                "id": "day_2",
                "name": "Day 2 - Rooftop Escape",
                "description": "Navigate the rooftops to reach the evacuation point",
                "type": StageType.ESCAPE,
                "unlock_condition": "complete_day_1",
                "map": "city_rooftops",
                "music": "escape_theme",
                "gravity_zones": {
                    "default": "normal",
                    "wind_zone": {"type": "low", "area": [0, 400, 2000, 800]}
                },
                "checkpoints": [
                    {"position": [200, 200], "id": "start"},
                    {"position": [800, 400], "id": "mid_1"},
                    {"position": [1400, 600], "id": "mid_2"},
                    {"position": [1900, 800], "id": "end"}
                ],
                "win_conditions": {
                    "primary": {
                        "type": "reach_destination",
                        "description": "Reach the helicopter pad",
                        "destination": [1900, 800]
                    },
                    "bonus": [
                        {
                            "type": "collect_all",
                            "description": "Rescue all 3 civilians",
                            "items": ["civilian_1", "civilian_2", "civilian_3"]
                        },
                        {
                            "type": "speed_run",
                            "description": "Complete in under 2 minutes",
                            "time": 120
                        }
                    ]
                },
                "collectibles": [
                    {"type": "civilian", "id": "civilian_1", "position": [600, 300]},
                    {"type": "civilian", "id": "civilian_2", "position": [1200, 500]},
                    {"type": "civilian", "id": "civilian_3", "position": [1600, 700]}
                ],
                "rewards": {
                    "score": 1500,
                    "unlock_next": "day_3"
                }
            },
            "day_3": {
                "id": "day_3",
                "name": "Day 3 - Last Stand",
                "description": "Hold the position until reinforcements arrive",
                "type": StageType.SURVIVAL,
                "unlock_condition": "complete_day_2",
                "map": "city_square",
                "music": "intense_battle",
                "enemy_waves": [
                    {
                        "trigger": "timer",
                        "delay": 0,
                        "enemies": [
                            {"type": "cancer_small", "position": [200, 200], "count": 5}
                        ]
                    },
                    {
                        "trigger": "timer",
                        "delay": 20,
                        "enemies": [
                            {"type": "cancer_medium", "position": [1800, 200], "count": 3},
                            {"type": "cancer_small", "position": [1000, 200], "count": 4}
                        ]
                    },
                    {
                        "trigger": "timer",
                        "delay": 40,
                        "enemies": [
                            {"type": "cancer_large", "position": [1000, 200], "count": 2},
                            {"type": "cancer_medium", "position": [500, 200], "count": 3}
                        ]
                    }
                ],
                "win_conditions": {
                    "primary": {
                        "type": "survive_time",
                        "description": "Survive for 90 seconds",
                        "time": 90
                    },
                    "bonus": [
                        {
                            "type": "kill_count",
                            "description": "Defeat 30 enemies",
                            "count": 30
                        },
                        {
                            "type": "protect_objective",
                            "description": "Keep the generator above 50% health",
                            "objective_id": "generator",
                            "min_health": 50
                        }
                    ]
                },
                "objectives": [
                    {
                        "id": "generator",
                        "type": "defense_target",
                        "position": [1000, 300],
                        "health": 500
                    }
                ],
                "rewards": {
                    "score": 2000,
                    "unlock_next": "day_4"
                }
            },
            "day_4": {
                "id": "day_4",
                "name": "Day 4 - First Boss",
                "description": "Face the Cancer Commander",
                "type": StageType.BOSS,
                "unlock_condition": "complete_day_3",
                "map": "destroyed_plaza",
                "music": "boss_theme",
                "boss": {
                    "type": "cancer_commander",
                    "position": [1000, 300],
                    "health": 1000,
                    "phases": [
                        {
                            "health_threshold": 100,
                            "pattern": "aggressive",
                            "spawn_adds": True
                        },
                        {
                            "health_threshold": 50,
                            "pattern": "defensive",
                            "speed_boost": 1.5
                        },
                        {
                            "health_threshold": 25,
                            "pattern": "berserk",
                            "damage_boost": 2.0
                        }
                    ]
                },
                "win_conditions": {
                    "primary": {
                        "type": "defeat_boss",
                        "description": "Defeat the Cancer Commander"
                    },
                    "bonus": [
                        {
                            "type": "no_items",
                            "description": "Defeat without using items"
                        },
                        {
                            "type": "perfect_dodges",
                            "description": "Perfect dodge 10 attacks",
                            "count": 10
                        }
                    ]
                },
                "rewards": {
                    "score": 5000,
                    "unlock_next": "day_5",
                    "unlock_chapter": "chapter_2"
                }
            }
        }
    },
    "chapter_2": {
        "id": "chapter_2",
        "name": "Into the Depths",
        "description": "Investigation of the Cancer source leads underground",
        "unlock_condition": "complete_chapter_1",
        "days": {
            "day_1": {
                "id": "day_1",
                "name": "Day 1 - Underground Entrance",
                "description": "Find and secure the entrance to the Cancer hive",
                "type": StageType.COLLECTION,
                "unlock_condition": "default",
                "map": "cave_entrance",
                "music": "mystery_theme",
                "gravity_zones": {
                    "default": "normal",
                    "cave_area": {"type": "low", "area": [800, 0, 1600, 400]}
                },
                "collectibles": [
                    {"type": "key_fragment", "id": "fragment_1", "position": [400, 200]},
                    {"type": "key_fragment", "id": "fragment_2", "position": [1000, 400]},
                    {"type": "key_fragment", "id": "fragment_3", "position": [1600, 300]},
                    {"type": "intel", "id": "intel_1", "position": [600, 500]},
                    {"type": "intel", "id": "intel_2", "position": [1400, 200]}
                ],
                "win_conditions": {
                    "primary": {
                        "type": "collect_items",
                        "description": "Collect all 3 key fragments",
                        "items": ["fragment_1", "fragment_2", "fragment_3"],
                        "required_count": 3
                    },
                    "bonus": [
                        {
                            "type": "collect_all",
                            "description": "Find all intel documents",
                            "items": ["intel_1", "intel_2"]
                        },
                        {
                            "type": "stealth",
                            "description": "Complete without alerting enemies",
                            "max_alerts": 0
                        }
                    ]
                },
                "rewards": {
                    "score": 2500,
                    "unlock_next": "day_2"
                }
            }
        }
    }
}

def get_chapter_data(chapter_id: str) -> Optional[Dict[str, Any]]:
    """Get chapter data by ID"""
    return CHAPTERS.get(chapter_id)

def get_stage_data(chapter_id: str, day_id: str) -> Optional[Dict[str, Any]]:
    """Get specific stage data"""
    chapter = get_chapter_data(chapter_id)
    if chapter:
        return chapter.get('days', {}).get(day_id)
    return None

def get_unlocked_chapters(save_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get list of unlocked chapters based on save data"""
    unlocked = []
    progress = save_data.get('progress', {})
    completed_stages = progress.get('completed_stages', [])
    
    for chapter_id, chapter in CHAPTERS.items():
        unlock_condition = chapter.get('unlock_condition', 'locked')
        
        if unlock_condition == 'default':
            unlocked.append(chapter)
        elif unlock_condition.startswith('complete_'):
            # Check if required chapter is completed
            required = unlock_condition.replace('complete_', '')
            if f"{required}_day_4" in completed_stages:  # Assuming 4 days per chapter
                unlocked.append(chapter)
                
    return unlocked

def get_unlocked_stages(chapter_id: str, save_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get list of unlocked stages in a chapter"""
    chapter = get_chapter_data(chapter_id)
    if not chapter:
        return []
        
    unlocked = []
    progress = save_data.get('progress', {})
    completed_stages = progress.get('completed_stages', [])
    
    for day_id, day in chapter.get('days', {}).items():
        unlock_condition = day.get('unlock_condition', 'locked')
        
        if unlock_condition == 'default':
            unlocked.append(day)
        elif unlock_condition.startswith('complete_'):
            # Check if required stage is completed
            required = unlock_condition.replace('complete_', '')
            stage_key = f"{chapter_id}_{required}"
            if stage_key in completed_stages:
                unlocked.append(day)
                
    return unlocked

def is_stage_unlocked(chapter_id: str, day_id: str, save_data: Dict[str, Any]) -> bool:
    """Check if a specific stage is unlocked"""
    unlocked_stages = get_unlocked_stages(chapter_id, save_data)
    return any(stage['id'] == day_id for stage in unlocked_stages)