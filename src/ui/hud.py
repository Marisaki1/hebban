# src/ui/hud.py
"""
Enhanced HUD with character portraits and ability cooldowns
"""

from typing import List
import arcade
from src.core.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from src.entities.player import Player
from src.core.sprite_manager import sprite_manager
import math

class HUD:
    """Enhanced in-game heads-up display"""
    def __init__(self, player: Player):
        self.player = player
        self.score = 0
        self.show_fps = False
        
        # Load character portrait
        self.portrait = sprite_manager.get_portrait(player.character_id)
        
        # Animation timers
        self.health_flash_timer = 0
        self.score_popup_timer = 0
        self.last_score = 0
        self.score_popup_value = 0
        
        # Combo display
        self.combo_display_timer = 0
        
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
            self.portrait.draw_scaled(
                portrait_x, portrait_y,
                scale=frame_size / self.portrait.width
            )
        else:
            # Placeholder
            arcade.draw_rectangle_filled(
                portrait_x, portrait_y,
                frame_size, frame_size,
                arcade.color.DARK_BLUE_GRAY
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
            arcade.draw_text(
                f"+{self.score_popup_value}",
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
            if hasattr(self.player, 'ability_instances'):
                ability = self.player.ability_instances.get(ability_name.lower().replace(' ', '_'))
                if ability and ability.current_cooldown > 0:
                    bg_color = arcade.color.DARK_GRAY
                    
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
            
            # Cooldown overlay
            if hasattr(self.player, 'ability_instances'):
                ability = self.player.ability_instances.get(ability_name.lower().replace(' ', '_'))
                if ability and ability.current_cooldown > 0:
                    # Draw cooldown sweep
                    cooldown_percentage = ability.current_cooldown / ability.data.cooldown
                    sweep_angle = 360 * cooldown_percentage
                    
                    # Semi-transparent overlay
                    arcade.draw_rectangle_filled(
                        x, y, icon_size, icon_size,
                        (0, 0, 0, 180)
                    )
                    
                    # Cooldown text
                    arcade.draw_text(
                        f"{ability.current_cooldown:.1f}",
                        x, y,
                        arcade.color.WHITE,
                        16,
                        anchor_x="center",
                        anchor_y="center",
                        font_name="Arial",
                        bold=True
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
        if hasattr(self.player, 'combo_timer'):
            fill_percentage = self.player.combo_timer
            fill_width = bg_width * fill_percentage
            
            # Gradient color based on combo level
            combo_colors = [
                arcade.color.YELLOW,
                arcade.color.ORANGE,
                arcade.color.RED
            ]
            color = combo_colors[min(self.player.attack_combo - 1, 2)]
            
            arcade.draw_rectangle_filled(
                combo_x - bg_width/2 + fill_width/2, combo_y,
                fill_width, bg_height - 4,
                color
            )
            
        # Combo text
        combo_text = f"COMBO x{self.player.attack_combo}"
        text_size = 20 + self.player.attack_combo * 2  # Grow with combo
        
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
        for i in range(self.player.attack_combo):
            star_x = combo_x - 30 + i * 30
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