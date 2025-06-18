# ============================================================================
# FILE: src/core/asset_manager.py
# ============================================================================
import os
import arcade
from typing import Dict, Optional
from PIL import Image, ImageDraw

class AssetManager:
    """Manages game assets with fallback support"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.textures: Dict[str, arcade.Texture] = {}
            self.sounds: Dict[str, arcade.Sound] = {}
            self.asset_paths = {
                'sprites': 'assets/sprites',
                'sounds': 'assets/sounds',
                'ui': 'assets/sprites/ui',
                'characters': 'assets/sprites/characters',
                'enemies': 'assets/sprites/enemies'
            }
            self.generate_default_assets()
    
    def generate_default_assets(self):
        """Generate default placeholder assets"""
        # Create default character sprite
        self._create_default_sprite('default_character', (64, 64), (100, 150, 200))
        self._create_default_sprite('default_enemy', (64, 64), (200, 100, 100))
        self._create_default_sprite('default_ui_button', (200, 50), (80, 80, 80))
        self._create_default_sprite('default_squad_icon', (50, 50), (150, 150, 150))
        
    def _create_default_sprite(self, name: str, size: tuple, color: tuple):
        """Create a default colored rectangle sprite"""
        image = Image.new('RGBA', size, color + (255,))
        draw = ImageDraw.Draw(image)
        # Add border
        draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(255, 255, 255, 255), width=2)
        
        texture = arcade.Texture(name, image)
        self.textures[name] = texture
        
    def get_texture(self, path: str, fallback: str = 'default_character') -> arcade.Texture:
        """Get texture with fallback support"""
        if path in self.textures:
            return self.textures[path]
            
        # Try to load the texture
        for base_path in self.asset_paths.values():
            full_path = os.path.join(base_path, path)
            if os.path.exists(full_path):
                try:
                    texture = arcade.load_texture(full_path)
                    self.textures[path] = texture
                    return texture
                except:
                    pass
                    
        # Return fallback
        return self.textures.get(fallback, self._create_error_texture())
        
    def _create_error_texture(self) -> arcade.Texture:
        """Create an error texture"""
        image = Image.new('RGBA', (64, 64), (255, 0, 255, 255))
        return arcade.Texture('error', image)
