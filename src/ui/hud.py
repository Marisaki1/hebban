# src/ui/hud.py - Fixed version
"""
Enhanced HUD with character portraits and ability cooldowns
"""

from typing import List
import arcade
import math
from src.core.constants import SCREEN_HEIGHT, SCREEN_WIDTH

class HUD:
    """Enhanced in-game heads-up display"""
    def __init__(self, player):
        self.player = player
        self.score = 0
        self.show_fps = False
        
        # Load character portrait (with fallback)
        self.portrait = self._get_character_portrait()
        
        # Animation timers
        self.health_flash_timer = 0
        self.score_popup_timer = 0
        self.last_score = 0
        self.score_popup_value = 0
        
        # Combo display
        self.combo_display_timer = 0
        
    def _get_character_portrait(self):
        """Get character portrait with fallback"""
        try:
            from src.core.sprite_manager import sprite_manager
            return sprite_manager.get_portrait(self.player.character_id)
        except:
            # Fallback - create a simple colored square
            from src.core.asset_manager import AssetManager
            asset_manager = AssetManager()
            return asset_manager.get_texture('default_character')
        
    def draw(self):
        """Draw HUD elements"""
        # Character portrait frame
        portrait_x = 60
        portrait_y = SCREEN_HEIGHT - 60
        frame_size = 80
        
        # Draw portrait background
        arcade.draw_rectangle_filled(
            portrait_x, portrait_y,
            frame_size + 10, frame_size + 10,
            arcade.color.DARK_GRAY
        )
        arcade.draw_rectangle_outline(
            portrait_x, portrait_y,
            frame_size + 10, frame_size + 10,
            arcade.color.GOLD,
            3
        )
        
        # Draw character portrait
        if self.portrait:
            # Simple texture draw
            arcade.draw_texture_rectangle(
                portrait_x, portrait_y,
                frame_size, frame_size,
                self.portrait
            )
        else:
            # Placeholder
            arcade.draw_rectangle_filled(
                portrait_x, portrait_y,
                frame_size, frame_size,
                arcade.color.DARK_BLUE_GRAY
            )
            # Draw character name initial
            char_name = self.player.character_data.get('name', 'P')
            arcade.draw_text(
                char_name[0],
                portrait_x, portrait_y,
                arcade.color.WHITE,
                32,
                anchor_x="center",
                anchor_y="center",
                font_name="Arial",
                bold=True
            )
            
        # Health bar with gradient
        health_x = portrait_x + 100
        health_y = portrait_y + 20
        health_width = 200
        health_height = 20
        
        # Health bar background
        arcade.draw_rectangle_filled(
            health_x + health_width/2, health_y,
            health_width, health_height,
            arcade.color.BLACK
        )
        
        # Health bar fill
        health_percentage = self.player.health / self.player.max_health
        current_health_width = health_width * health_percentage
        
        # Determine health color based on percentage
        if health_percentage > 0.6:
            health_color = arcade.color.GREEN
        elif health_percentage > 0.3:
            health_color = arcade.color.YELLOW
        else:
            health_color = arcade.color.RED
            # Flash when low health
            if self.health_flash_timer % 0.5 < 0.25:
                health_color = arcade.color.ORANGE
        
        if current_health_width > 0:
            arcade.draw_rectangle_filled(
                health_x + current_health_width/2, health_y,
                current_health_width, health_height,
                health_color
            )
            
        # Health bar border
        arcade.draw_rectangle_outline(
            health_x + health_width/2, health_y,
            health_width, health_height,
            arcade.color.WHITE, 2
        )
        
        # Health text
        arcade.draw_text(
            f"{self.player.health}/{self.player.max_health}",
            health_x + health_width/2, health_y,
            arcade.color.WHITE,
            14,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            bold=True
        )
        
        # Character name
        arcade.draw_text(
            self.player.character_data.get('name', 'Player'),
            health_x, health_y - 30,
            arcade.color.WHITE,
            18,
            font_name="Arial",
            bold=True
        )
        
        # Score display with animation
        score_x = SCREEN_WIDTH - 200
        score_y = SCREEN_HEIGHT - 30
        
        # Background for score
        arcade.draw_rectangle_filled(
            score_x, score_y,
            180, 40,
            (0, 0, 0, 128)
        )
        
        arcade.draw_text(
            f"Score: {self.score:,}",
            score_x, score_y,
            arcade.color.WHITE,
            20,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            bold=True
        )
        
        # Score popup animation
        if self.score_popup_timer > 0:
            popup_y = score_y - 40 - (1 - self.score_popup_timer) * 20
            popup_alpha = int(255 * self.score_popup_timer)
            
            # Handle both numeric and string popup values
            popup_text = str(self.score_popup_value)
            if isinstance(self.score_popup_value, int) and self.score_popup_value > 0:
                popup_text = f"+{self.score_popup_value}"
                
            arcade.draw_text(
                popup_text,
                score_x, popup_y,
                (*arcade.color.YELLOW[:3], popup_alpha),
                16,
                anchor_x="center",
                font_name="Arial"
            )
        
        # Ability cooldown display
        self.draw_ability_cooldowns()
        
        # Combo meter
        if self.player.attack_combo > 0:
            self.draw_combo_meter()
        
        # FPS counter
        if self.show_fps:
            arcade.draw_text(
                f"FPS: {arcade.get_fps():.0f}",
                10, 10,
                arcade.color.WHITE,
                12
            )
            
    def draw_ability_cooldowns(self):
        """Draw ability icons and cooldowns"""
        ability_x = 60
        ability_y = 150
        icon_size = 60
        spacing = 10
        
        # Get player abilities
        abilities = self.player.abilities[:4]  # Show up to 4 abilities
        
        for i, ability_name in enumerate(abilities):
            x = ability_x + i * (icon_size + spacing)
            y = ability_y
            
            # Ability box background
            bg_color = arcade.color.DARK_BLUE_GRAY
            # Note: ability cooldown system would need to be implemented in player class
            
            arcade.draw_rectangle_filled(x, y, icon_size, icon_size, bg_color)
            arcade.draw_rectangle_outline(x, y, icon_size, icon_size, arcade.color.WHITE, 2)
            
            # Ability key hint
            keys = ['Q', 'W', 'E', 'R']
            if i < len(keys):
                arcade.draw_text(
                    keys[i],
                    x - icon_size/2 + 5, y + icon_size/2 - 20,
                    arcade.color.WHITE,
                    12,
                    font_name="Arial",
                    bold=True
                )
                
            # Ability name (abbreviated)
            arcade.draw_text(
                ability_name[:6],
                x, y,
                arcade.color.WHITE,
                10,
                anchor_x="center",
                anchor_y="center"
            )
            
    def draw_combo_meter(self):
        """Draw combo meter with style"""
        combo_x = SCREEN_WIDTH // 2
        combo_y = SCREEN_HEIGHT - 100
        
        # Combo background
        bg_width = 200
        bg_height = 40
        arcade.draw_rectangle_filled(
            combo_x, combo_y,
            bg_width, bg_height,
            (0, 0, 0, 180)
        )
        
        # Combo fill based on timer
        if hasattr(self.player, 'combo_timer') and self.player.combo_timer > 0:
            fill_percentage = self.player.combo_timer / self.player.max_combo_time
            fill_width = bg_width * fill_percentage
            
            # Gradient color based on combo level
            if self.player.attack_combo >= 5:
                color = arcade.color.RED
            elif self.player.attack_combo >= 3:
                color = arcade.color.ORANGE
            else:
                color = arcade.color.YELLOW
            
            arcade.draw_rectangle_filled(
                combo_x - bg_width/2 + fill_width/2, combo_y,
                fill_width, bg_height - 4,
                color
            )
            
        # Combo text
        combo_text = f"COMBO x{self.player.attack_combo}"
        text_size = min(24, 20 + self.player.attack_combo * 2)  # Grow with combo
        
        arcade.draw_text(
            combo_text,
            combo_x, combo_y,
            arcade.color.WHITE,
            text_size,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            bold=True
        )
        
        # Combo multiplier stars
        for i in range(min(self.player.attack_combo, 5)):  # Max 5 stars
            star_x = combo_x - 60 + i * 30
            star_y = combo_y + 30
            arcade.draw_text(
                "★",
                star_x, star_y,
                arcade.color.GOLD,
                20,
                anchor_x="center"
            )
            
    def update(self, delta_time: float):
        """Update HUD animations"""
        # Update health flash
        if self.player.health / self.player.max_health < 0.3:
            self.health_flash_timer += delta_time
        else:
            self.health_flash_timer = 0
            
        # Update score popup
        if self.score != self.last_score:
            self.score_popup_value = self.score - self.last_score
            self.score_popup_timer = 1.0
            self.last_score = self.score
            
        if self.score_popup_timer > 0:
            self.score_popup_timer -= delta_time
            
    def add_score(self, points: int, show_popup: bool = True):
        """Add score with optional popup"""
        self.score += points
        if show_popup:
            self.score_popup_value = points
            self.score_popup_timer = 1.0