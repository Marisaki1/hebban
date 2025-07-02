"""
Character and squad data definitions
"""

from typing import Dict, List, Optional, Any

# Squad data with all characters
SQUAD_DATA = {
    "31A": {
        "id": "31A",
        "name": "31A Squad",
        "description": "Elite combat unit specializing in aerial combat against Cancers",
        "unlock_condition": "default",
        "squad_bonus": {
            "type": "balanced",
            "health_bonus": 10,
            "attack_bonus": 5
        },
        "formation": "assault",
        "members": [
            {
                "id": "ruka",
                "name": "Ruka Kayamori",
                "title": "Squad Leader",
                "bio": "Leader of 31A, skilled in both combat and tactics",
                "health": 100,
                "speed": 6,
                "jump_power": 15,
                "attack": 8,
                "defense": 6,
                "abilities": ["Double Jump", "Dash Attack", "Leadership Boost"],
                "color": (220, 100, 100),
                "unlock_condition": "default"
            },
            {
                "id": "yuki",
                "name": "Yuki Izumi", 
                "title": "Scout",
                "bio": "Swift and agile scout specializing in reconnaissance",
                "health": 80,
                "speed": 9,
                "jump_power": 18,
                "attack": 6,
                "defense": 4,
                "abilities": ["Air Dash", "Quick Strike", "Enhanced Vision"],
                "color": (100, 150, 220),
                "unlock_condition": "default"
            },
            {
                "id": "karen",
                "name": "Karen Kohiruimaki",
                "title": "Heavy Assault",
                "bio": "Defensive specialist with heavy armor and weapons",
                "health": 120,
                "speed": 4,
                "jump_power": 12,
                "attack": 10,
                "defense": 8,
                "abilities": ["Shield Bash", "Ground Pound", "Armor Up"],
                "color": (100, 220, 100),
                "unlock_condition": "default"
            },
            {
                "id": "tsukasa",
                "name": "Tsukasa Munakata",
                "title": "Tech Specialist", 
                "bio": "Technology expert with energy-based attacks",
                "health": 90,
                "speed": 7,
                "jump_power": 16,
                "attack": 7,
                "defense": 5,
                "abilities": ["Teleport", "Energy Blast", "Tech Shield"],
                "color": (200, 150, 100),
                "unlock_condition": "default"
            },
            {
                "id": "megumi",
                "name": "Megumi Yakigaya",
                "title": "Support",
                "bio": "Healing and support specialist",
                "health": 85,
                "speed": 7,
                "jump_power": 17,
                "attack": 6,
                "defense": 6,
                "abilities": ["Healing Aura", "Light Beam", "Purify"],
                "color": (220, 220, 100),
                "unlock_condition": "default"
            },
            {
                "id": "ichigo", 
                "name": "Ichigo Tanaka",
                "title": "Pyro Specialist",
                "bio": "Fire-based attacks and area control",
                "health": 95,
                "speed": 6,
                "jump_power": 15,
                "attack": 9,
                "defense": 5,
                "abilities": ["Fire Ball", "Flame Dash", "Fire Shield"],
                "color": (220, 120, 50),
                "unlock_condition": "default"
            }
        ]
    },
    "31B": {
        "id": "31B",
        "name": "31B Squad",
        "description": "Heavy assault squad with focus on defensive tactics",
        "unlock_condition": "complete_chapter_2",
        "squad_bonus": {
            "type": "defensive",
            "health_bonus": 20,
            "defense_bonus": 10
        },
        "formation": "defensive",
        "members": [
            {
                "id": "seika",
                "name": "Seika Lamprogue",
                "title": "Ice Specialist",
                "bio": "Ice-based attacks and crowd control",
                "health": 110,
                "speed": 5,
                "jump_power": 14,
                "attack": 8,
                "defense": 7,
                "abilities": ["Ice Wall", "Freeze Ray", "Blizzard"],
                "color": (100, 200, 220),
                "unlock_condition": "complete_chapter_2"
            },
            {
                "id": "mion",
                "name": "Mion Murasame",
                "title": "Stealth Operative",
                "bio": "Stealth and assassination specialist",
                "health": 85,
                "speed": 9,
                "jump_power": 16,
                "attack": 9,
                "defense": 4,
                "abilities": ["Shadow Step", "Smoke Bomb", "Critical Strike"],
                "color": (80, 80, 120),
                "unlock_condition": "complete_chapter_2"
            },
            {
                "id": "aoi",
                "name": "Aoi Koga",
                "title": "Lightning Specialist",
                "bio": "Electric attacks and high mobility",
                "health": 100,
                "speed": 8,
                "jump_power": 17,
                "attack": 8,
                "defense": 5,
                "abilities": ["Thunder Strike", "Electric Field", "Chain Lightning"],
                "color": (200, 200, 50),
                "unlock_condition": "complete_chapter_2"
            },
            {
                "id": "sumire",
                "name": "Sumire Heanna",
                "title": "Wind Specialist",
                "bio": "Wind-based attacks and aerial control",
                "health": 90,
                "speed": 8,
                "jump_power": 19,
                "attack": 7,
                "defense": 6,
                "abilities": ["Wind Slash", "Tornado", "Air Walk"],
                "color": (150, 220, 150),
                "unlock_condition": "complete_chapter_2"
            },
            {
                "id": "kura",
                "name": "Kura Kokoa",
                "title": "Earth Specialist",
                "bio": "Earth-based attacks and defensive abilities",
                "health": 115,
                "speed": 4,
                "jump_power": 13,
                "attack": 9,
                "defense": 8,
                "abilities": ["Rock Throw", "Earth Quake", "Stone Shield"],
                "color": (150, 100, 50),
                "unlock_condition": "complete_chapter_2"
            },
            {
                "id": "maria",
                "name": "Maria Alucard",
                "title": "Time Specialist",
                "bio": "Time manipulation and support abilities",
                "health": 80,
                "speed": 7,
                "jump_power": 16,
                "attack": 6,
                "defense": 5,
                "abilities": ["Time Slow", "Blink", "Temporal Shield"],
                "color": (180, 100, 180),
                "unlock_condition": "complete_chapter_2"
            }
        ]
    },
    "31C": {
        "id": "31C",
        "name": "31C Squad",
        "description": "Stealth operations squad for infiltration missions",
        "unlock_condition": "complete_chapter_3",
        "squad_bonus": {
            "type": "speed",
            "speed_bonus": 15,
            "evasion_bonus": 20
        },
        "formation": "infiltration",
        "members": [
            {
                "id": "nina",
                "name": "Nina Williams",
                "title": "Infiltration Leader",
                "bio": "Master of stealth and infiltration tactics",
                "health": 90,
                "speed": 9,
                "jump_power": 17,
                "attack": 8,
                "defense": 5,
                "abilities": ["Stealth", "Silent Strike", "Invisibility"],
                "color": (120, 120, 120),
                "unlock_condition": "complete_chapter_3"
            },
            {
                "id": "rei",
                "name": "Rei Hino",
                "title": "Mystic Specialist",
                "bio": "Spiritual powers and mystic abilities",
                "health": 85,
                "speed": 7,
                "jump_power": 16,
                "attack": 7,
                "defense": 6,
                "abilities": ["Spirit Fire", "Ward", "Exorcism"],
                "color": (180, 50, 50),
                "unlock_condition": "complete_chapter_3"
            },
            {
                "id": "luna",
                "name": "Luna Tsukino",
                "title": "Lunar Specialist",
                "bio": "Moon-based powers and night operations",
                "health": 80,
                "speed": 8,
                "jump_power": 18,
                "attack": 6,
                "defense": 5,
                "abilities": ["Moon Beam", "Lunar Shield", "Night Vision"],
                "color": (150, 150, 200),
                "unlock_condition": "complete_chapter_3"
            },
            {
                "id": "stella",
                "name": "Stella Vermillion",
                "title": "Star Specialist",
                "bio": "Stellar energy manipulation and ranged attacks",
                "health": 85,
                "speed": 7,
                "jump_power": 16,
                "attack": 8,
                "defense": 5,
                "abilities": ["Star Burst", "Meteor", "Cosmic Shield"],
                "color": (200, 200, 100),
                "unlock_condition": "complete_chapter_3"
            },
            {
                "id": "aria",
                "name": "Aria Kanzaki",
                "title": "Sound Specialist",
                "bio": "Sound-based attacks and area effects",
                "health": 90,
                "speed": 8,
                "jump_power": 17,
                "attack": 7,
                "defense": 6,
                "abilities": ["Sonic Boom", "Sound Barrier", "Resonance"],
                "color": (100, 180, 100),
                "unlock_condition": "complete_chapter_3"
            },
            {
                "id": "nova",
                "name": "Nova Prime",
                "title": "Energy Specialist",
                "bio": "Pure energy manipulation and devastating attacks",
                "health": 95,
                "speed": 7,
                "jump_power": 15,
                "attack": 10,
                "defense": 6,
                "abilities": ["Energy Blast", "Power Surge", "Energy Shield"],
                "color": (200, 100, 200),
                "unlock_condition": "complete_chapter_3"
            }
        ]
    }
}

def get_squad_data(squad_id: str) -> Optional[Dict[str, Any]]:
    """Get squad data by ID"""
    return SQUAD_DATA.get(squad_id)

def get_all_squads() -> List[Dict[str, Any]]:
    """Get all squad data"""
    return list(SQUAD_DATA.values())

def get_character_data(squad_id: str, character_id: str) -> Optional[Dict[str, Any]]:
    """Get specific character data from a squad"""
    squad = get_squad_data(squad_id)
    if squad:
        for member in squad['members']:
            if member['id'] == character_id:
                return member
    return None

def get_unlocked_squads(save_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get list of unlocked squads based on save data"""
    unlocked_ids = save_data.get('unlocked_squads', ['31A'])
    return [squad for squad_id, squad in SQUAD_DATA.items() if squad_id in unlocked_ids]