# ============================================================================
# FILE: src/utils/helpers.py
# ============================================================================
import os
import json
import random
from typing import Dict, Any, Optional

def load_json_config(filename: str) -> Dict[str, Any]:
    """Load JSON configuration file"""
    config_path = os.path.join('config', filename)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON {filename}: {e}")
        return {}

def get_default_characters():
    """Get default character configuration"""
    return {
        "characters": {
            "31A": {
                "ruka": {
                    "id": "ruka",
                    "name": "Ruka Kayamori",
                    "title": "Squad Leader",
                    "bio": "Leader of 31A, skilled in both combat and tactics",
                    "stats": {
                        "health": 100,
                        "speed": 6,
                        "jump_power": 15,
                        "attack": 8,
                        "defense": 6
                    },
                    "abilities": [
                        "Double Jump",
                        "Dash Attack",
                        "Leadership Boost"
                    ],
                    "sprite_sheet": "ruka_sprites.png",
                    "portrait": "ruka_portrait.png",
                    "unlock_condition": "default"
                },
                "yuki": {
                    "id": "yuki",
                    "name": "Yuki Izumi",
                    "title": "Scout",
                    "bio": "Swift and agile scout specializing in reconnaissance",
                    "stats": {
                        "health": 80,
                        "speed": 9,
                        "jump_power": 18,
                        "attack": 6,
                        "defense": 4
                    },
                    "abilities": [
                        "Air Dash",
                        "Quick Strike",
                        "Enhanced Vision"
                    ],
                    "sprite_sheet": "yuki_sprites.png",
                    "portrait": "yuki_portrait.png",
                    "unlock_condition": "default"
                }
            }
        }
    }

def get_default_squads():
    """Get default squad configuration"""
    return {
        "squads": [
            {
                "id": "31A",
                "name": "31A Squad",
                "description": "Elite combat unit specializing in aerial combat against Cancers",
                "unlock_condition": "default",
                "squad_bonus": {
                    "type": "balanced",
                    "health_bonus": 10,
                    "attack_bonus": 5
                },
                "members": [
                    {"id": "ruka", "name": "Ruka", "health": 100, "speed": 6, "jump_power": 15, "abilities": ["Double Jump", "Dash Attack"]},
                    {"id": "yuki", "name": "Yuki", "health": 80, "speed": 8, "jump_power": 18, "abilities": ["Air Dash", "Quick Strike"]},
                    {"id": "karen", "name": "Karen", "health": 120, "speed": 4, "jump_power": 12, "abilities": ["Shield Bash", "Ground Pound"]},
                    {"id": "tsukasa", "name": "Tsukasa", "health": 90, "speed": 7, "jump_power": 16, "abilities": ["Teleport", "Energy Blast"]},
                    {"id": "megumi", "name": "Megumi", "health": 85, "speed": 7, "jump_power": 17, "abilities": ["Healing Aura", "Light Beam"]},
                    {"id": "ichigo", "name": "Ichigo", "health": 95, "speed": 6, "jump_power": 15, "abilities": ["Fire Ball", "Flame Dash"]}
                ],
                "formation": "assault"
            },
            {
                "id": "31B",
                "name": "31B Squad",
                "description": "Heavy assault squad with focus on defensive tactics",
                "unlock_condition": "complete_chapter_2",
                "squad_bonus": {
                    "type": "defensive",
                    "health_bonus": 20,
                    "defense_bonus": 10
                },
                "members": [
                    {"id": "seika", "name": "Seika", "health": 110, "speed": 5, "jump_power": 14, "abilities": ["Ice Wall", "Freeze Ray"]},
                    {"id": "mion", "name": "Mion", "health": 85, "speed": 9, "jump_power": 16, "abilities": ["Shadow Step", "Smoke Bomb"]},
                    {"id": "aoi", "name": "Aoi", "health": 100, "speed": 6, "jump_power": 15, "abilities": ["Thunder Strike", "Electric Field"]},
                    {"id": "sumire", "name": "Sumire", "health": 90, "speed": 7, "jump_power": 17, "abilities": ["Wind Slash", "Tornado"]},
                    {"id": "kura", "name": "Kura", "health": 95, "speed": 6, "jump_power": 15, "abilities": ["Rock Throw", "Earth Quake"]},
                    {"id": "maria", "name": "Maria", "health": 80, "speed": 8, "jump_power": 18, "abilities": ["Time Slow", "Blink"]}
                ],
                "formation": "defensive"
            }
        ]
    }

def get_default_input_mappings():
    """Get default input mappings"""
    return {
        "keyboard": {
            "move_left": ["A", "LEFT"],
            "move_right": ["D", "RIGHT"],
            "jump": ["SPACE", "W", "UP"],
            "action_1": ["Z", "J"],
            "action_2": ["X", "K"],
            "pause": ["ESCAPE", "P"],
            "menu_up": ["W", "UP"],
            "menu_down": ["S", "DOWN"],
            "menu_left": ["A", "LEFT"],
            "menu_right": ["D", "RIGHT"],
            "menu_select": ["ENTER", "SPACE"],
            "menu_back": ["ESCAPE", "BACKSPACE"]
        },
        "controller": {
            "xbox": {
                "move_left": "LEFT_STICK_LEFT",
                "move_right": "LEFT_STICK_RIGHT",
                "jump": "A",
                "action_1": "X",
                "action_2": "Y",
                "pause": "START",
                "menu_up": "DPAD_UP",
                "menu_down": "DPAD_DOWN",
                "menu_left": "DPAD_LEFT",
                "menu_right": "DPAD_RIGHT",
                "menu_select": "A",
                "menu_back": "B"
            }
        }
    }

def get_default_levels():
    """Get default levels configuration"""
    return {
        "chapters": [
            {
                "id": "chapter_1",
                "name": "First Contact",
                "description": "The Cancer invasion begins",
                "levels": [
                    {
                        "id": "1-1",
                        "name": "City Under Siege",
                        "description": "Defend the city from the initial Cancer attack",
                        "tilemap": "level_1_1.tmx",
                        "background": "city_ruins_bg.png",
                        "music": "battle_theme_1.ogg",
                        "gravity_zones": {
                            "default": "normal",
                            "zone_1": {"type": "low", "area": [1000, 0, 1500, 500]}
                        },
                        "enemy_spawns": [
                            {"type": "cancer_small", "position": [500, 200], "count": 3},
                            {"type": "cancer_medium", "position": [1000, 300], "count": 2},
                            {"type": "cancer_large", "position": [1500, 200], "count": 1}
                        ],
                        "objectives": [
                            {"type": "eliminate_all", "description": "Defeat all Cancers"},
                            {"type": "time_limit", "description": "Complete in under 5 minutes", "time": 300}
                        ],
                        "par_time": 180,
                        "unlock_condition": "default"
                    }
                ]
            }
        ]
    }

def create_default_configs():
    """Create default configuration files if they don't exist"""
    os.makedirs('config', exist_ok=True)
    
    configs = {
        'characters.json': get_default_characters(),
        'squads.json': get_default_squads(),
        'input_mappings.json': get_default_input_mappings(),
        'levels.json': get_default_levels()
    }
    
    for filename, content in configs.items():
        filepath = os.path.join('config', filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2)
            print(f"Created default config: {filename}")

def calculate_damage(attacker_stats: Dict, defender_stats: Dict, skill_multiplier: float = 1.0) -> int:
    """Calculate damage based on stats"""
    base_damage = attacker_stats.get('attack', 10)
    defense = defender_stats.get('defense', 5)
    damage = max(1, int((base_damage * skill_multiplier) - (defense * 0.5)))
    damage = int(damage * random.uniform(0.9, 1.1))
    return damage

def interpolate_position(start: tuple, end: tuple, t: float) -> tuple:
    """Interpolate between two positions"""
    x = start[0] + (end[0] - start[0]) * t
    y = start[1] + (end[1] - start[1]) * t
    return (x, y)

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))