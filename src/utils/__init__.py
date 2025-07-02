"""
Utility functions and helpers
"""

from .helpers import (
    load_json_config,
    create_default_configs,
    calculate_damage,
    interpolate_position,
    clamp,
    lerp,
    distance_between_points,
    normalize_vector,
    angle_between_points,
    format_time,
    wrap_text,
    generate_random_name,
    ease_in_out,
    ease_in_cubic,
    ease_out_cubic,
    screen_shake_offset,
    color_lerp,
    ensure_directory_exists,
    get_file_extension,
    is_point_in_rectangle
)

__all__ = [
    'load_json_config',
    'create_default_configs',
    'calculate_damage',
    'interpolate_position',
    'clamp',
    'lerp',
    'distance_between_points',
    'normalize_vector',
    'angle_between_points',
    'format_time',
    'wrap_text',
    'generate_random_name',
    'ease_in_out',
    'ease_in_cubic',
    'ease_out_cubic',
    'screen_shake_offset',
    'color_lerp',
    'ensure_directory_exists',
    'get_file_extension',
    'is_point_in_rectangle'
]