# src/stages/winning_conditions.py
"""
Winning condition system for stages
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Callable
import arcade

class WinCondition(Enum):
    """Types of winning conditions"""
    ELIMINATE_ALL = "eliminate_all"
    REACH_DESTINATION = "reach_destination"
    SURVIVE_TIME = "survive_time"
    DEFEAT_BOSS = "defeat_boss"
    COLLECT_ITEMS = "collect_items"
    COLLECT_ALL = "collect_all"
    TIME_LIMIT = "time_limit"
    SPEED_RUN = "speed_run"
    NO_DAMAGE = "no_damage"
    NO_ITEMS = "no_items"
    KILL_COUNT = "kill_count"
    PROTECT_OBJECTIVE = "protect_objective"
    STEALTH = "stealth"
    PERFECT_DODGES = "perfect_dodges"

class ConditionChecker:
    """Base class for condition checkers"""
    
    def __init__(self, condition_data: Dict[str, Any]):
        self.condition_type = WinCondition(condition_data['type'])
        self.description = condition_data['description']
        self.completed = False
        self.failed = False
        self.progress = 0
        self.target = 0
        
    def check(self, game_state: Dict[str, Any]) -> bool:
        """Check if condition is met"""
        return False
        
    def get_progress_text(self) -> str:
        """Get progress display text"""
        if self.completed:
            return f"✓ {self.description}"
        elif self.failed:
            return f"✗ {self.description}"
        else:
            return f"• {self.description} ({self.progress}/{self.target})"

class EliminateAllChecker(ConditionChecker):
    """Check if all enemies are eliminated"""
    
    def check(self, game_state: Dict[str, Any]) -> bool:
        enemy_count = game_state.get('enemy_count', 0)
        total_waves = game_state.get('total_waves', 0)
        current_wave = game_state.get('current_wave', 0)
        
        self.progress = game_state.get('enemies_defeated', 0)
        self.target = game_state.get('total_enemies', 0)
        
        # Check if all waves completed and no enemies remain
        if current_wave >= total_waves and enemy_count == 0:
            self.completed = True
            return True
        return False

class ReachDestinationChecker(ConditionChecker):
    """Check if player reached destination"""
    
    def __init__(self, condition_data: Dict[str, Any]):
        super().__init__(condition_data)
        self.destination = condition_data['destination']
        self.tolerance = 50  # Distance tolerance
        
    def check(self, game_state: Dict[str, Any]) -> bool:
        player_pos = game_state.get('player_position', (0, 0))
        
        # Calculate distance to destination
        dx = player_pos[0] - self.destination[0]
        dy = player_pos[1] - self.destination[1]
        distance = (dx * dx + dy * dy) ** 0.5
        
        self.progress = max(0, int(100 - (distance / 10)))  # Progress as percentage
        self.target = 100
        
        if distance <= self.tolerance:
            self.completed = True
            return True
        return False

class SurviveTimeChecker(ConditionChecker):
    """Check if player survived for required time"""
    
    def __init__(self, condition_data: Dict[str, Any]):
        super().__init__(condition_data)
        self.required_time = condition_data['time']
        self.target = self.required_time
        
    def check(self, game_state: Dict[str, Any]) -> bool:
        elapsed_time = game_state.get('elapsed_time', 0)
        self.progress = int(elapsed_time)
        
        if elapsed_time >= self.required_time:
            self.completed = True
            return True
        return False

class DefeatBossChecker(ConditionChecker):
    """Check if boss is defeated"""
    
    def check(self, game_state: Dict[str, Any]) -> bool:
        boss_health = game_state.get('boss_health', 0)
        boss_max_health = game_state.get('boss_max_health', 1)
        
        self.progress = boss_max_health - boss_health
        self.target = boss_max_health
        
        if boss_health <= 0:
            self.completed = True
            return True
        return False

class CollectItemsChecker(ConditionChecker):
    """Check if required items are collected"""
    
    def __init__(self, condition_data: Dict[str, Any]):
        super().__init__(condition_data)
        self.required_items = condition_data.get('items', [])
        self.required_count = condition_data.get('required_count', len(self.required_items))
        self.target = self.required_count
        
    def check(self, game_state: Dict[str, Any]) -> bool:
        collected_items = game_state.get('collected_items', [])
        
        # Count how many required items are collected
        collected_count = sum(1 for item in self.required_items if item in collected_items)
        self.progress = collected_count
        
        if collected_count >= self.required_count:
            self.completed = True
            return True
        return False

class TimeLimitChecker(ConditionChecker):
    """Check if stage completed within time limit"""
    
    def __init__(self, condition_data: Dict[str, Any]):
        super().__init__(condition_data)
        self.time_limit = condition_data['time']
        
    def check(self, game_state: Dict[str, Any]) -> bool:
        elapsed_time = game_state.get('elapsed_time', 0)
        stage_completed = game_state.get('primary_complete', False)
        
        self.progress = int(elapsed_time)
        self.target = self.time_limit
        
        if elapsed_time > self.time_limit:
            self.failed = True
        elif stage_completed and elapsed_time <= self.time_limit:
            self.completed = True
            return True
        return False

class NoDamageChecker(ConditionChecker):
    """Check if player took no damage"""
    
    def check(self, game_state: Dict[str, Any]) -> bool:
        damage_taken = game_state.get('damage_taken', 0)
        stage_completed = game_state.get('primary_complete', False)
        
        if damage_taken > 0:
            self.failed = True
        elif stage_completed and damage_taken == 0:
            self.completed = True
            return True
        return False

class WinConditionChecker:
    """Manages all win conditions for a stage"""
    
    def __init__(self, win_conditions: Dict[str, Any]):
        self.primary_condition = self._create_checker(win_conditions['primary'])
        self.bonus_conditions = [
            self._create_checker(condition) 
            for condition in win_conditions.get('bonus', [])
        ]
        
        self.primary_complete = False
        self.all_bonus_complete = False
        
    def _create_checker(self, condition_data: Dict[str, Any]) -> ConditionChecker:
        """Create appropriate checker for condition type"""
        condition_type = WinCondition(condition_data['type'])
        
        checker_map = {
            WinCondition.ELIMINATE_ALL: EliminateAllChecker,
            WinCondition.REACH_DESTINATION: ReachDestinationChecker,
            WinCondition.SURVIVE_TIME: SurviveTimeChecker,
            WinCondition.DEFEAT_BOSS: DefeatBossChecker,
            WinCondition.COLLECT_ITEMS: CollectItemsChecker,
            WinCondition.COLLECT_ALL: CollectItemsChecker,
            WinCondition.TIME_LIMIT: TimeLimitChecker,
            WinCondition.SPEED_RUN: TimeLimitChecker,
            WinCondition.NO_DAMAGE: NoDamageChecker,
            # Add more as needed
        }
        
        checker_class = checker_map.get(condition_type, ConditionChecker)
        return checker_class(condition_data)
        
    def update(self, game_state: Dict[str, Any]):
        """Update all condition checks"""
        # Check primary condition
        if not self.primary_complete:
            self.primary_complete = self.primary_condition.check(game_state)
            game_state['primary_complete'] = self.primary_complete
            
        # Check bonus conditions
        bonus_complete_count = 0
        for condition in self.bonus_conditions:
            if condition.check(game_state):
                bonus_complete_count += 1
                
        self.all_bonus_complete = (bonus_complete_count == len(self.bonus_conditions))
        
    def is_stage_complete(self) -> bool:
        """Check if stage is complete (primary condition met)"""
        return self.primary_complete
        
    def is_stage_failed(self) -> bool:
        """Check if stage is failed"""
        return self.primary_condition.failed
        
    def get_completion_percentage(self) -> float:
        """Get overall completion percentage"""
        total_conditions = 1 + len(self.bonus_conditions)
        completed = 1 if self.primary_complete else 0
        completed += sum(1 for c in self.bonus_conditions if c.completed)
        
        return (completed / total_conditions) * 100
        
    def get_score_multiplier(self) -> float:
        """Get score multiplier based on completion"""
        base_multiplier = 1.0
        
        # Bonus for each completed bonus condition
        for condition in self.bonus_conditions:
            if condition.completed:
                base_multiplier += 0.5
                
        return base_multiplier
        
    def get_progress_display(self) -> List[str]:
        """Get list of progress strings for display"""
        progress = []
        
        # Primary condition
        progress.append(f"[PRIMARY] {self.primary_condition.get_progress_text()}")
        
        # Bonus conditions
        for condition in self.bonus_conditions:
            progress.append(f"[BONUS] {condition.get_progress_text()}")
            
        return progress