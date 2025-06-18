# ============================================================================
# FILE: src/menu/leaderboard.py
# ============================================================================
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
        self.stages = [
            "Stage 1-1", "Stage 1-2", "Stage 1-3", "Stage 1-4",
            "Stage 2-1", "Stage 2-2", "Stage 2-3", "Stage 2-4"
        ]
        self.current_stage_index = 0
        self.leaderboard_data = self._load_leaderboard_data()
        self.scroll_offset = 0
        self.entries_per_page = 10
        
    def _load_leaderboard_data(self) -> Dict[str, List[LeaderboardEntry]]:
        """Load leaderboard data (mock data for now)"""
        data = {}
        
        # Generate mock data for each stage
        for stage in self.stages:
            entries = []
            for i in range(50):
                entry = LeaderboardEntry(
                    rank=i + 1,
                    name=f"Player{i+1:03d}",
                    score=100000 - (i * 1000),
                    time=f"{2 + (i // 10)}:{(i % 60):02d}",
                    stage=stage
                )
                entries.append(entry)
            data[stage] = entries
            
        return data
        
    def draw(self):
        """Draw leaderboard"""
        arcade.start_render()
        
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
            anchor_x="center",
            font_name="Arial",
            bold=True
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
            ("Rank", 200),
            ("Name", 400),
            ("Score", 600),
            ("Time", 800),
            ("Stage", 1000)
        ]
        
        for header, x in headers:
            arcade.draw_text(
                header,
                x, header_y,
                arcade.color.WHITE,
                18,
                anchor_x="center",
                font_name="Arial",
                bold=True
            )
            
        # Draw separator
        arcade.draw_line(
            150, header_y - 15,
            SCREEN_WIDTH - 150, header_y - 15,
            arcade.color.WHITE, 2
        )
        
        # Leaderboard entries
        entries = self.leaderboard_data[stage_name]
        start_index = self.scroll_offset
        end_index = min(start_index + self.entries_per_page, len(entries))
        
        entry_y = header_y - 50
        for i in range(start_index, end_index):
            entry = entries[i]
            
            # Highlight top 3
            if entry.rank <= 3:
                colors = [arcade.color.GOLD, arcade.color.SILVER, arcade.color.BRONZE]
                color = colors[entry.rank - 1]
            else:
                color = arcade.color.WHITE
                
            # Draw entry data
            arcade.draw_text(f"#{entry.rank}", 200, entry_y, color, 16, anchor_x="center")
            arcade.draw_text(entry.name, 400, entry_y, color, 16, anchor_x="center")
            arcade.draw_text(f"{entry.score:,}", 600, entry_y, color, 16, anchor_x="center")
            arcade.draw_text(entry.time, 800, entry_y, color, 16, anchor_x="center")
            arcade.draw_text(entry.stage, 1000, entry_y, color, 16, anchor_x="center")
            
            entry_y -= 35
            
        # Scroll indicator
        if len(entries) > self.entries_per_page:
            arcade.draw_text(
                f"Page {self.scroll_offset // self.entries_per_page + 1} / {(len(entries) - 1) // self.entries_per_page + 1}",
                SCREEN_WIDTH // 2,
                80,
                arcade.color.WHITE,
                14,
                anchor_x="center"
            )
            
        # Instructions
        arcade.draw_text(
            "Use LEFT/RIGHT to change stage, UP/DOWN to scroll",
            SCREEN_WIDTH // 2,
            40,
            arcade.color.WHITE,
            14,
            anchor_x="center"
        )
        
    def change_stage(self, direction: int):
        """Change selected stage"""
        self.current_stage_index = (self.current_stage_index + direction) % len(self.stages)
        self.scroll_offset = 0
        
    def scroll_leaderboard(self, direction: int):
        """Scroll through leaderboard entries"""
        entries = self.leaderboard_data[self.stages[self.current_stage_index]]
        max_offset = max(0, len(entries) - self.entries_per_page)
        
        self.scroll_offset += direction * self.entries_per_page
        self.scroll_offset = max(0, min(self.scroll_offset, max_offset))