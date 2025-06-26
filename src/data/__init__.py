from .sprite_manager import sprite_manager
"""
Data module for squad and character configurations
"""
from .squad_data import (
    SQUAD_DATA,
    SPRITE_CONFIG,
    get_squad_data,
    get_all_squads,
    get_character_data
)

__all__ = [
    'SQUAD_DATA',
    'SPRITE_CONFIG', 
    'get_squad_data',
    'get_all_squads',
    'get_character_data'
]
