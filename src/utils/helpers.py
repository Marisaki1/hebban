"""
Utility helper functions
"""

import os
import json
import random
import math
from typing import Dict, Any, Optional, Tuple

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
    
    # Only create if files don't exist
    config_files = ['characters.json', 'squads.json', 'input_mappings.json', 'levels.json']
    
    for config_file in config_files:
        filepath = os.path.join('config', config_file)
        if not os.path.exists(filepath):
            print(f"Config file {config_file} would be created here")
            # In a full implementation, would create actual config files

def calculate_damage(attacker_stats: Dict, defender_stats: Dict, skill_multiplier: float = 1.0) -> int:
    """Calculate damage based on stats"""
    base_damage = attacker_stats.get('attack', 10)
    defense = defender_stats.get('defense', 5)
    damage = max(1, int((base_damage * skill_multiplier) - (defense * 0.5)))
    
    # Add random variation
    damage = int(damage * random.uniform(0.9, 1.1))
    return damage

def interpolate_position(start: Tuple[float, float], end: Tuple[float, float], t: float) -> Tuple[float, float]:
    """Interpolate between two positions"""
    x = start[0] + (end[0] - start[0]) * t
    y = start[1] + (end[1] - start[1]) * t
    return (x, y)

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))

def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation between start and end"""
    return start + (end - start) * t

def distance_between_points(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Calculate distance between two points"""
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return math.sqrt(dx * dx + dy * dy)

def normalize_vector(vector: Tuple[float, float]) -> Tuple[float, float]:
    """Normalize a 2D vector"""
    x, y = vector
    length = math.sqrt(x * x + y * y)
    if length == 0:
        return (0, 0)
    return (x / length, y / length)

def angle_between_points(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Get angle between two points in radians"""
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return math.atan2(dy, dx)

def format_time(seconds: float) -> str:
    """Format time in seconds to MM:SS format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def wrap_text(text: str, max_width: int) -> list:
    """Wrap text to fit within max_width characters per line"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line + word) <= max_width:
            current_line += word + " "
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    
    if current_line:
        lines.append(current_line.strip())
    
    return lines

def generate_random_name() -> str:
    """Generate a random player name"""
    prefixes = [
        "Ruka", "Yuki", "Karen", "Tsukasa", "Megumi", "Ichigo",
        "Squad", "Cancer", "Aerial", "Combat", "Elite", "Guardian",
        "Phoenix", "Shadow", "Lightning", "Storm", "Blade", "Star"
    ]
    
    suffixes = [
        "Fan", "Master", "Slayer", "Ace", "Hero", "Legend",
        "Pro", "Elite", "Prime", "Alpha", "Beta", "Gamma"
    ]
    
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    number = random.randint(10, 999)
    
    return f"{prefix}{suffix}{number}"

def ease_in_out(t: float) -> float:
    """Smooth easing function for animations"""
    return t * t * (3.0 - 2.0 * t)

def ease_in_cubic(t: float) -> float:
    """Cubic ease-in function"""
    return t * t * t

def ease_out_cubic(t: float) -> float:
    """Cubic ease-out function"""  
    return 1 - pow(1 - t, 3)

def screen_shake_offset(intensity: float, decay: float, time: float) -> Tuple[float, float]:
    """Calculate screen shake offset"""
    if intensity <= 0:
        return (0, 0)
    
    # Decay the intensity over time
    current_intensity = intensity * math.exp(-decay * time)
    
    # Generate random offset
    angle = random.uniform(0, 2 * math.pi)
    magnitude = random.uniform(0, current_intensity)
    
    x = math.cos(angle) * magnitude
    y = math.sin(angle) * magnitude
    
    return (x, y)

def color_lerp(color1: Tuple[int, int, int], color2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    """Interpolate between two RGB colors"""
    r = int(lerp(color1[0], color2[0], t))
    g = int(lerp(color1[1], color2[1], t))
    b = int(lerp(color1[2], color2[2], t))
    
    return (clamp(r, 0, 255), clamp(g, 0, 255), clamp(b, 0, 255))

def ensure_directory_exists(directory: str):
    """Ensure a directory exists, create if it doesn't"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()

def is_point_in_rectangle(point: Tuple[float, float], rect_center: Tuple[float, float], 
                         rect_width: float, rect_height: float) -> bool:
    """Check if point is inside rectangle"""
    px, py = point
    cx, cy = rect_center
    
    half_width = rect_width / 2
    half_height = rect_height / 2
    
    return (cx - half_width <= px <= cx + half_width and
            cy - half_height <= py <= cy + half_height)