# ============================================================================
# FILE: src/core/asset_manager.py - Updated for Arcade 3.0
# ============================================================================
import os
import arcade
from typing import Dict, Optional
from PIL import Image, ImageDraw

from src.core.asset_loader import AssetLoader

class AssetManager:
    """Manages game assets with fallback support - Arcade 3.0 Compatible"""
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
        """Create a default colored rectangle sprite - Arcade 3.0 Compatible"""
        image = Image.new('RGBA', size, color + (255,))
        draw = ImageDraw.Draw(image)
        # Add border
        draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(255, 255, 255, 255), width=2)
        
        # Create texture from PIL image - Arcade 3.0 Method
        try:
            # Try new Arcade 3.0 method first
            texture = arcade.Texture.create_filled(name, size, color + (255,))
        except (AttributeError, TypeError):
            # Fallback to PIL image conversion for Arcade 3.0
            try:
                texture = arcade.Texture(name, image)
            except TypeError:
                # Alternative Arcade 3.0 syntax
                texture = arcade.Texture.create_from_pil_image(image, name)
        
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
        """Create an error texture - Arcade 3.0 Compatible"""
        try:
            # Try Arcade 3.0 method
            return arcade.Texture.create_filled('error', (64, 64), (255, 0, 255, 255))
        except (AttributeError, TypeError):
            # Fallback method
            image = Image.new('RGBA', (64, 64), (255, 0, 255, 255))
            try:
                return arcade.Texture('error', image)
            except TypeError:
                return arcade.Texture.create_from_pil_image(image, 'error')
    

    def load_game_assets(self):
        """Load all game assets"""
        # Load character sprites
        characters = ['ruka', 'yuki', 'karen', 'tsukasa']
        for char in characters:
            AssetLoader.load_character_sprites(self, char)
            
        # Load UI elements
        ui_assets = [
            'button_normal.png',
            'button_hover.png',
            'button_pressed.png',
            'health_bar_bg.png',
            'health_bar_fill.png'
        ]
        
        for asset in ui_assets:
            path = f"assets/sprites/ui/{asset}"
            if os.path.exists(path):
                name = asset.replace('.png', '')
                try:
                    self.textures[name] = arcade.load_texture(path)
                except Exception as e:
                    print(f"Error loading UI asset {path}: {e}")
                    # Create fallback
                    self.textures[name] = self._create_error_texture()
                    
    def create_colored_texture(self, name: str, size: tuple, color: tuple) -> arcade.Texture:
        """Create a solid colored texture - Arcade 3.0 Helper"""
        try:
            # Arcade 3.0 method
            texture = arcade.Texture.create_filled(name, size, color)
        except (AttributeError, TypeError):
            # Fallback to PIL
            image = Image.new('RGBA', size, color)
            try:
                texture = arcade.Texture(name, image)
            except TypeError:
                texture = arcade.Texture.create_from_pil_image(image, name)
        
        self.textures[name] = texture
        return texture
        
    def preload_textures(self, texture_list: list):
        """Preload a list of textures"""
        for texture_path in texture_list:
            self.get_texture(texture_path)
            
    def get_texture_count(self) -> int:
        """Get number of loaded textures"""
        return len(self.textures)
        
    def clear_cache(self):
        """Clear texture cache"""
        self.textures.clear()
        self.generate_default_assets()