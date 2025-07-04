# src/stages/__init__.py
"""
Stage system for Heaven Burns Red
"""

from .stage_data import (
    CHAPTERS,
    get_chapter_data,
    get_stage_data,
    get_unlocked_chapters,
    get_unlocked_stages,
    is_stage_unlocked
)

from .stage_loader import StageLoader
from .winning_conditions import WinCondition, WinConditionChecker

__all__ = [
    'CHAPTERS',
    'get_chapter_data',
    'get_stage_data',
    'get_unlocked_chapters',
    'get_unlocked_stages',
    'is_stage_unlocked',
    'StageLoader',
    'WinCondition',
    'WinConditionChecker'
]