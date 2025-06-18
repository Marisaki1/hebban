# ============================================================================
# FILE: src/utils/helpers.py
# ============================================================================

import os
import json
import random
from typing import Dict, Any, Optional
import arcade  # Assumed used somewhere else in your project

# These need to be defined or imported elsewhere in your project
# Example placeholders below (remove and replace them with your actual data)
CHARACTERS_JSON = "{}"
SQUADS_JSON = "{}"
INPUT_MAPPINGS_JSON = "{}"
LEVELS_JSON = "{}"

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

def create_default_configs():
    """Create default configuration files if they don't exist"""
    os.makedirs('config', exist_ok=True)
    configs = {
        'characters.json': CHARACTERS_JSON,
        'squads.json': SQUADS_JSON,
        'input_mappings.json': INPUT_MAPPINGS_JSON,
        'levels.json': LEVELS_JSON
    }
    for filename, content in configs.items():
        filepath = os.path.join('config', filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
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
