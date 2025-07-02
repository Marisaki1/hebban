"""
Heads-up display for gameplay
"""

import arcade
import math
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class HUD:
    """In-game heads-up display"""
    
    def __init__(self, player):
        self.player = player
        self.score = 0
        
        # Animation timers
        self.health_flash_timer = 0
        self.score_popup_timer = 0
        self.score_popup_value = 0
        self.last_score = 0
        
        # Combo display
        self.combo_flash_timer = 0
        
        # Health bar animation
        self.displayed_health = player.health
        self.health_lerp_speed = 5.0
        
    def update(self, delta_time: float):
        """Update HUD animations"""
        # Update health flash when low
        if self.player.health / self.player.max_health < 0.3:
            self.health_flash_timer += delta_time
        else:
            self.health_flash_timer = 0
            
        # Smooth health bar animation
        health_diff = self.player.health - self.displayed_health
        if abs(health_diff) > 0.1:
            self.displayed_health += health_diff * self.health_lerp_speed * delta_time
        else:
            self.displayed_health = self.player.health
            
        # Update score popup
        if self.score != self.last_score:
            self.score_popup_value = self.score - self.last_score
            self.score_popup_timer = 2.0
            self.last_score = self.score
            
        if self.score_popup_timer > 0:
            self.score_popup_timer -= delta_time
            
        # Update combo flash
        if hasattr(self.player, 'attack_combo') and self.player.attack_combo > 0:
            self.combo_flash_timer += delta_time
            
    def draw(self):
        """Draw all HUD elements"""
        self.draw_health_bar()
        self.draw_character_info()
        self.draw_score()
        self.draw_combo_meter()
        self.draw_abilities()
        
    def draw_health_bar(self):
        """Draw player health bar"""
        # Health bar position
        bar_x = 20
        bar_y = SCREEN_HEIGHT - 30
        bar_width = 300
        bar_height = 25
        
        # Health bar background
        arcade.draw_rectangle_filled(
            bar_x + bar_width // 2, bar_y,
            bar_width, bar_height,
            arcade.color.DARK_RED
        )
        
        # Health bar fill
        health_percentage = self.displayed_health / self.player.max_health
        fill_width = bar_width * health_percentage
        
        # Health color based on percentage
        if health_percentage > 0.6:
            health_color = arcade.color.GREEN
        elif health_percentage > 0.3:
            health_color = arcade.color.YELLOW
        else:
            # Flash red when critically low
            if self.health_flash_timer % 0.5 < 0.25:
                health_color = arcade.color.RED
            else:
                health_color = arcade.color.DARK_RED
                
        if fill_width > 0:
            arcade.draw_rectangle_filled(
                bar_x + fill_width // 2, bar_y,
                fill_width, bar_height,
                health_color
            )
            
        # Health bar border
        arcade.draw_rectangle_outline(
            bar_x + bar_width // 2, bar_y,
            bar_width, bar_height,
            arcade.color.WHITE, 2
        )
        
        # Health text
        arcade.draw_text(
            f"{int(self.player.health)}/{self.player.max_health}",
            bar_x + bar_width // 2, bar_y,
            arcade.color.WHITE,
            16,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Health label
        arcade.draw_text(
            "Health",
            bar_x, bar_y + 20,
            arcade.color.WHITE,
            14
        )
        
    def draw_character_info(self):
        """Draw character portrait and name"""
        # Character portrait area
        portrait_x = 60
        portrait_y = SCREEN_HEIGHT - 100
        portrait_size = 60
        
        # Portrait background
        char_color = self.player.character_data.get('color', (100, 100, 100))
        arcade.draw_rectangle_filled(
            portrait_x, portrait_y, portrait_size, portrait_size, char_color
        )
        arcade.draw_rectangle_outline(
            portrait_x, portrait_y, portrait_size, portrait_size,
            arcade.color.GOLD, 3
        )
        
        # Character initial
        char_name = self.player.character_data.get('name', 'Player')
        arcade.draw_text(
            char_name[0],
            portrait_x, portrait_y,
            arcade.color.WHITE,
            24,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Character name
        arcade.draw_text(
            char_name,
            portrait_x + 50, portrait_y + 10,
            arcade.color.WHITE,
            14
        )
        
        # Character title
        title = self.player.character_data.get('title', 'Fighter')
        arcade.draw_text(
            title,
            portrait_x + 50, portrait_y - 10,
            arcade.color.YELLOW,
            12
        )
        
    def draw_score(self):
        """Draw score display"""
        score_x = SCREEN_WIDTH - 20
        score_y = SCREEN_HEIGHT - 30
        
        # Score background
        arcade.draw_rectangle_filled(
            score_x - 100, score_y,
            200, 30,
            (0, 0, 0, 100)
        )
        
        # Score text
        arcade.draw_text(
            f"Score: {self.score:,}",
            score_x, score_y,
            arcade.color.WHITE,
            18,
            anchor_x="right",
            anchor_y="center"
        )
        
        # Score popup animation
        if self.score_popup_timer > 0:
            popup_alpha = int(255 * (self.score_popup_timer / 2.0))
            popup_y = score_y - 40 - (2.0 - self.score_popup_timer) * 30
            
            popup_text = f"+{self.score_popup_value}"
            if self.score_popup_value < 0:
                popup_text = str(self.score_popup_value)
                popup_color = (*arcade.color.RED, popup_alpha)
            else:
                popup_color = (*arcade.color.YELLOW, popup_alpha)
                
            arcade.draw_text(
                popup_text,
                score_x, popup_y,
                popup_color,
                16,
                anchor_x="right"
            )
            
    def draw_combo_meter(self):
        """Draw combo meter"""
        if not hasattr(self.player, 'attack_combo') or self.player.attack_combo <= 0:
            return
            
        combo_x = SCREEN_WIDTH // 2
        combo_y = SCREEN_HEIGHT - 80
        
        # Combo background
        bg_width = 250
        bg_height = 50
        arcade.draw_rectangle_filled(
            combo_x, combo_y,
            bg_width, bg_height,
            (0, 0, 0, 150)
        )
        arcade.draw_rectangle_outline(
            combo_x, combo_y,
            bg_width, bg_height,
            arcade.color.WHITE, 2
        )
        
        # Combo timer bar
        if hasattr(self.player, 'combo_timer') and hasattr(self.player, 'max_combo_time'):
            timer_percentage = self.player.combo_timer / self.player.max_combo_time
            timer_width = (bg_width - 10) * timer_percentage
            
            # Timer color based on remaining time
            if timer_percentage > 0.5:
                timer_color = arcade.color.GREEN
            elif timer_percentage > 0.2:
                timer_color = arcade.color.YELLOW
            else:
                timer_color = arcade.color.RED
                
            if timer_width > 0:
                arcade.draw_rectangle_filled(
                    combo_x - bg_width//2 + timer_width//2 + 5, combo_y - 15,
                    timer_width, 8,
                    timer_color
                )
                
        # Combo text with scaling effect
        combo_scale = 1.0 + (self.player.attack_combo * 0.1)
        if self.combo_flash_timer % 0.3 < 0.15:  # Flash effect
            combo_scale *= 1.2
            
        text_size = int(20 * combo_scale)
        combo_text = f"COMBO x{self.player.attack_combo}"
        
        # Combo color based on level
        if self.player.attack_combo >= 10:
            combo_color = arcade.color.PURPLE
        elif self.player.attack_combo >= 5:
            combo_color = arcade.color.RED
        elif self.player.attack_combo >= 3:
            combo_color = arcade.color.ORANGE
        else:
            combo_color = arcade.color.YELLOW
            
        arcade.draw_text(
            combo_text,
            combo_x, combo_y + 5,
            combo_color,
            text_size,
            anchor_x="center",
            anchor_y="center"
        )
        
    def draw_abilities(self):
        """Draw ability cooldown indicators"""
        abilities = getattr(self.player, 'abilities', [])
        if not abilities:
            return
            
        # Ability icons position
        icon_size = 50
        spacing = 10
        start_x = 50
        start_y = 150
        
        for i, ability in enumerate(abilities[:4]):  # Show up to 4 abilities
            x = start_x + i * (icon_size + spacing)
            y = start_y
            
            # Ability icon background
            bg_color = arcade.color.DARK_BLUE_GRAY
            
            # Check if ability is on cooldown (placeholder)
            on_cooldown = False  # In full implementation, check actual cooldowns
            
            if on_cooldown:
                bg_color = arcade.color.DARK_GRAY
                
            arcade.draw_rectangle_filled(x, y, icon_size, icon_size, bg_color)
            arcade.draw_rectangle_outline(x, y, icon_size, icon_size, arcade.color.WHITE, 2)
            
            # Ability key hint
            keys = ['Z', 'X', 'C', 'V']
            if i < len(keys):
                arcade.draw_text(
                    keys[i],
                    x - icon_size//2 + 5, y + icon_size//2 - 15,
                    arcade.color.WHITE,
                    10
                )
                
            # Ability name (abbreviated)
            ability_name = ability if isinstance(ability, str) else str(ability)
            short_name = ability_name[:4]
            arcade.draw_text(
                short_name,
                x, y,
                arcade.color.WHITE,
                10,
                anchor_x="center",
                anchor_y="center"
            )
            
            # Cooldown overlay (if on cooldown)
            if on_cooldown:
                cooldown_percentage = 0.5  # Placeholder
                overlay_height = icon_size * cooldown_percentage
                
                arcade.draw_rectangle_filled(
                    x, y - icon_size//2 + overlay_height//2,
                    icon_size, overlay_height,
                    (0, 0, 0, 150)
                )
                
    def add_score(self, points: int):
        """Add score with popup effect"""
        self.score += points
        self.score_popup_value = points
        self.score_popup_timer = 2.0