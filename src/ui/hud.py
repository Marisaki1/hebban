# ============================================================================
# FILE: src/ui/hud.py
# ============================================================================
class HUD:
    """In-game heads-up display"""
    def __init__(self, player: Player):
        self.player = player
        self.score = 0
        self.show_fps = False
        
    def draw(self):
        """Draw HUD elements"""
        # Health bar background
        arcade.draw_rectangle_filled(
            150, SCREEN_HEIGHT - 30,
            200, 20,
            arcade.color.DARK_GRAY
        )
        
        # Health bar
        health_percentage = self.player.health / self.player.max_health
        health_width = 200 * health_percentage
        health_color = arcade.color.GREEN if health_percentage > 0.5 else arcade.color.YELLOW if health_percentage > 0.25 else arcade.color.RED
        
        arcade.draw_rectangle_filled(
            50 + health_width/2, SCREEN_HEIGHT - 30,
            health_width, 20,
            health_color
        )
        
        # Health text
        arcade.draw_text(
            f"{self.player.health}/{self.player.max_health}",
            150, SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            14,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Character name
        arcade.draw_text(
            self.player.character_data.get('name', 'Player'),
            50, SCREEN_HEIGHT - 60,
            arcade.color.WHITE,
            16,
            font_name="Arial"
        )
        
        # Score
        arcade.draw_text(
            f"Score: {self.score:,}",
            SCREEN_WIDTH - 200, SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            18,
            font_name="Arial"
        )
        
        # Abilities
        ability_x = 50
        ability_y = 100
        for i, ability in enumerate(self.player.abilities[:2]):
            # Ability box
            arcade.draw_rectangle_filled(
                ability_x + i * 70, ability_y,
                60, 60,
                arcade.color.DARK_BLUE_GRAY
            )
            arcade.draw_rectangle_outline(
                ability_x + i * 70, ability_y,
                60, 60,
                arcade.color.WHITE,
                2
            )
            
            # Ability key
            key = "Z" if i == 0 else "X"
            arcade.draw_text(
                key,
                ability_x + i * 70, ability_y,
                arcade.color.WHITE,
                16,
                anchor_x="center",
                anchor_y="center"
            )
            
        # FPS counter
        if self.show_fps:
            arcade.draw_text(
                f"FPS: {arcade.get_fps():.0f}",
                10, 10,
                arcade.color.WHITE,
                12
            )