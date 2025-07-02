"""
Global leaderboard menu
"""

import arcade
from src.menu.menu_state import MenuState
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.input.input_manager import InputAction

class LeaderboardEntry:
    """Single leaderboard entry"""
    
    def __init__(self, rank: int, name: str, score: int, time: str, stage: str):
        self.rank = rank
        self.name = name
        self.score = score
        self.time = time
        self.stage = stage

class LeaderboardMenu(MenuState):
    """Global leaderboard per stage"""
    
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Global Leaderboard"
        self.scene_name = "leaderboard"
        
        # Available stages
        self.stages = [
            "1-1", "1-2", "1-3", "1-4",
            "2-1", "2-2", "2-3", "2-4",
            "3-1", "3-2", "3-3", "3-4"
        ]
        
        self.current_stage_index = 0
        self.leaderboard_data = self._generate_leaderboard_data()
        self.scroll_offset = 0
        self.entries_per_page = 12
        
    def _generate_leaderboard_data(self):
        """Generate dummy leaderboard data"""
        import random
        
        data = {}
        
        # Player names for variety
        player_names = [
            "RukaFan", "YukiSpeed", "KarenTank", "TsukasaTech", "MegumiHealer", "IchigoFire",
            "SquadLeader", "CancerSlayer", "AerialAce", "ComboMaster", "SpeedRunner", "Perfectionist",
            "EliteGamer", "ProPlayer", "SkillMaster", "Champion", "Warrior", "Guardian",
            "Phoenix", "Shadow", "Lightning", "Storm", "Blade", "Star", "Nova", "Crimson",
            "Azure", "Emerald", "Golden", "Silver", "Diamond", "Platinum", "Titanium", "Steel"
        ]
        
        for stage in self.stages:
            entries = []
            for i in range(50):  # 50 entries per stage
                # Generate realistic scores (higher for later stages)
                stage_num = int(stage.split('-')[0]) + int(stage.split('-')[1]) * 0.1
                base_score = int(stage_num * 10000)
                score = base_score + random.randint(-5000, 15000) - (i * 200)
                score = max(score, 1000)  # Minimum score
                
                # Generate realistic times (2-8 minutes)
                base_time = 120 + (stage_num * 30)  # Base time in seconds
                time_variation = random.randint(-30, 60) + (i * 5)
                total_seconds = int(base_time + time_variation)
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                time_str = f"{minutes}:{seconds:02d}"
                
                # Pick random name
                name = random.choice(player_names) + str(random.randint(10, 999))
                
                entry = LeaderboardEntry(
                    rank=i + 1,
                    name=name,
                    score=score,
                    time=time_str,
                    stage=stage
                )
                entries.append(entry)
                
            data[stage] = entries
            
        return data
        
    def on_enter(self):
        """Setup leaderboard controls"""
        super().on_enter()
        
        self.input_manager.clear_scene_callbacks(self.scene_name)
        
        # Stage navigation
        self.input_manager.register_action_callback(
            InputAction.MENU_LEFT, self.previous_stage, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_RIGHT, self.next_stage, self.scene_name
        )
        
        # Scroll navigation
        self.input_manager.register_action_callback(
            InputAction.MENU_UP, self.scroll_up, self.scene_name
        )
        self.input_manager.register_action_callback(
            InputAction.MENU_DOWN, self.scroll_down, self.scene_name
        )
        
        self.input_manager.register_action_callback(
            InputAction.BACK, self.go_back, self.scene_name
        )
        
    def previous_stage(self):
        """Go to previous stage"""
        self.current_stage_index = (self.current_stage_index - 1) % len(self.stages)
        self.scroll_offset = 0
        
    def next_stage(self):
        """Go to next stage"""
        self.current_stage_index = (self.current_stage_index + 1) % len(self.stages)
        self.scroll_offset = 0
        
    def scroll_up(self):
        """Scroll up through leaderboard"""
        self.scroll_offset = max(0, self.scroll_offset - 1)
        
    def scroll_down(self):
        """Scroll down through leaderboard"""
        stage_name = self.stages[self.current_stage_index]
        entries = self.leaderboard_data[stage_name]
        max_offset = max(0, len(entries) - self.entries_per_page)
        self.scroll_offset = min(max_offset, self.scroll_offset + 1)
        
    def draw(self):
        """Draw leaderboard"""
        # Background
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            (20, 20, 20)
        )
        
        # Title
        arcade.draw_text(
            self.title,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 60,
            arcade.color.CRIMSON,
            36,
            anchor_x="center"
        )
        
        # Stage selector
        stage_name = self.stages[self.current_stage_index]
        arcade.draw_text(
            f"< {stage_name} >",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 120,
            arcade.color.YELLOW,
            24,
            anchor_x="center"
        )
        
        # Leaderboard headers
        header_y = SCREEN_HEIGHT - 180
        headers = [
            ("Rank", 150),
            ("Player", 350),
            ("Score", 550),
            ("Time", 750),
            ("Character", 950)
        ]
        
        for header, x in headers:
            arcade.draw_text(
                header,
                x, header_y,
                arcade.color.WHITE,
                18,
                anchor_x="center"
            )
            
        # Draw separator line
        arcade.draw_line(
            100, header_y - 20,
            SCREEN_WIDTH - 100, header_y - 20,
            arcade.color.WHITE, 2
        )
        
        # Leaderboard entries
        entries = self.leaderboard_data[stage_name]
        start_index = self.scroll_offset
        end_index = min(start_index + self.entries_per_page, len(entries))
        
        entry_y = header_y - 60
        for i in range(start_index, end_index):
            entry = entries[i]
            
            # Highlight top 3 ranks
            if entry.rank <= 3:
                colors = [arcade.color.GOLD, arcade.color.SILVER, (205, 127, 50)]  # Bronze
                text_color = colors[entry.rank - 1]
                
                # Draw trophy background for top 3
                arcade.draw_rectangle_filled(
                    SCREEN_WIDTH // 2, entry_y,
                    SCREEN_WIDTH - 200, 25,
                    (*text_color, 50)
                )
            else:
                text_color = arcade.color.WHITE
                
            # Draw entry data
            arcade.draw_text(f"#{entry.rank}", 150, entry_y, text_color, 14, anchor_x="center")
            arcade.draw_text(entry.name, 350, entry_y, text_color, 14, anchor_x="center")
            arcade.draw_text(f"{entry.score:,}", 550, entry_y, text_color, 14, anchor_x="center")
            arcade.draw_text(entry.time, 750, entry_y, text_color, 14, anchor_x="center")
            
            # Random character for display
            characters = ["Ruka", "Yuki", "Karen", "Tsukasa", "Megumi", "Ichigo"]
            import random
            char = characters[i % len(characters)]
            arcade.draw_text(char, 950, entry_y, text_color, 14, anchor_x="center")
            
            entry_y -= 35
            
        # Scroll indicator
        if len(entries) > self.entries_per_page:
            current_page = self.scroll_offset // self.entries_per_page + 1
            total_pages = (len(entries) - 1) // self.entries_per_page + 1
            
            arcade.draw_text(
                f"Page {current_page} / {total_pages}",
                SCREEN_WIDTH // 2,
                80,
                arcade.color.WHITE,
                16,
                anchor_x="center"
            )
            
        # Instructions
        arcade.draw_text(
            "LEFT/RIGHT: Change stage  •  UP/DOWN: Scroll  •  ESC: Back",
            SCREEN_WIDTH // 2,
            40,
            arcade.color.WHITE,
            14,
            anchor_x="center"
        )