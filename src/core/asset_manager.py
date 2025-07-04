"""
Fixed asset manager for Arcade 3.0.0 and Pillow 11.0.0
"""

import os
import arcade
from typing import Dict, Optional
from PIL import Image, ImageDraw

class AssetManager:
    """Manages game assets - Fixed for Arcade 3.0.0"""
    
    def __init__(self):
        self.textures: Dict[str, arcade.Texture] = {}
        self.sounds: Dict[str, arcade.Sound] = {}
        
    def load_default_assets(self):
        """Load/create default game assets"""
        # Create default character textures
        characters = ['ruka', 'yuki', 'karen', 'tsukasa', 'megumi', 'ichigo']
        colors = [
            (220, 100, 100),  # ruka - red
            (100, 150, 220),  # yuki - blue  
            (100, 220, 100),  # karen - green
            (200, 150, 100),  # tsukasa - orange
            (220, 220, 100),  # megumi - yellow
            (220, 120, 50),   # ichigo - fire orange
        ]
        
        for i, char in enumerate(characters):
            color = colors[i]
            self._create_character_textures(char, color)
            
        # Create enemy textures
        enemy_colors = {
            'small': (150, 50, 50),
            'medium': (200, 80, 80), 
            'large': (250, 100, 100),
            'boss': (300, 150, 150)
        }
        
        for size, color in enemy_colors.items():
            self._create_enemy_texture(size, color)
            
        # Create UI textures
        self._create_ui_textures()
        
    def _create_character_textures(self, char_id: str, color: tuple):
        """Create character textures"""
        # Portrait
        portrait = self._create_colored_texture(f"{char_id}_portrait", (128, 128), color, char_id[0].upper())
        self.textures[f"{char_id}_portrait"] = portrait
        
        # Idle sprite
        idle = self._create_colored_texture(f"{char_id}_idle", (64, 64), color, char_id[0].upper())
        self.textures[f"{char_id}_idle"] = idle
        
        # Walking animation frames
        for i in range(4):
            walk_color = tuple(max(0, min(255, c + (i * 10 - 20))) for c in color)
            walk_frame = self._create_colored_texture(f"{char_id}_walk_{i}", (64, 64), walk_color, str(i+1))
            self.textures[f"{char_id}_walk_{i}"] = walk_frame
            
    def _create_enemy_texture(self, size: str, color: tuple):
        """Create enemy texture"""
        sizes = {'small': 32, 'medium': 48, 'large': 64, 'boss': 96}
        sprite_size = sizes.get(size, 32)
        
        texture = self._create_colored_texture(f"enemy_{size}", (sprite_size, sprite_size), color, "C")
        self.textures[f"enemy_{size}"] = texture
        
    def _create_ui_textures(self):
        """Create UI textures"""
        # Platform texture
        platform = self._create_colored_texture("platform", (200, 20), (100, 100, 100), "")
        self.textures["platform"] = platform
        
        # Button texture
        button = self._create_colored_texture("button", (200, 50), (80, 80, 80), "")
        self.textures["button"] = button
        
    def _create_colored_texture(self, name: str, size: tuple, color: tuple, text: str = "") -> arcade.Texture:
        """Create a colored texture using Pillow 11.0.0 - FIXED for Arcade 3.0.0"""
        try:
            # Create image with Pillow
            image = Image.new('RGBA', size, color + (255,))
            draw = ImageDraw.Draw(image)
            
            # Add border
            draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(255, 255, 255, 255), width=2)
            
            # Add text if provided
            if text:
                # Calculate text position
                try:
                    bbox = draw.textbbox((0, 0), text)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                except:
                    # Fallback text size estimation
                    text_width = len(text) * 12
                    text_height = 16
                    
                text_x = (size[0] - text_width) // 2
                text_y = (size[1] - text_height) // 2
                
                draw.text((text_x, text_y), text, fill=(255, 255, 255, 255))
                
            # Create Arcade texture - FIXED for Arcade 3.0.0

            # Use the constructor with name as first parameter (old style that still works)
            return arcade.Texture(name, image)
            
        except Exception as e:
            print(f"Error creating texture {name}: {e}")

            # Fallback - create simple colored texture using class method
            try:
                return arcade.Texture.create_filled(name, size, color + (255,))
            except:
                # If that fails too, create a basic texture
                fallback_image = Image.new('RGBA', size, color + (255,))
                return arcade.Texture(name, fallback_image)
        
    def get_texture(self, name: str) -> Optional[arcade.Texture]:
        """Get texture by name"""
        return self.textures.get(name)
        
    def load_sound(self, name: str, filepath: str) -> bool:
        """Load sound file"""
        if os.path.exists(filepath):
            try:
                sound = arcade.load_sound(filepath)
                self.sounds[name] = sound
                return True
            except Exception as e:
                print(f"Error loading sound {filepath}: {e}")
        return False
        
    def get_sound(self, name: str) -> Optional[arcade.Sound]:
        """Get sound by name"""
        return self.sounds.get(name)
        
    def create_sprite(self, texture_name: str) -> arcade.Sprite:
        """Create sprite from texture"""
        sprite = arcade.Sprite()
        texture = self.get_texture(texture_name)
        if texture:
            sprite.texture = texture
        return sprite