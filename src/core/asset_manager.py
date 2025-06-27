# ============================================================================
# FILE: src/core/asset_manager.py - Fixed for Arcade 3.0
# ============================================================================
import os
import arcade
from typing import Dict, Optional

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
        try:
            # Use Arcade 3.0's make_soft_square_texture
            texture = arcade.make_soft_square_texture(
                max(size), 
                color,
                outer_alpha=255
            )
            self.textures[name] = texture
        except Exception as e:
            print(f"Error creating default texture {name}: {e}")
            # Create a very basic fallback
            try:
                # Try alternative method with PIL
                from PIL import Image
                image = Image.new('RGBA', size, color + (255,))
                texture = arcade.Texture(image)
                self.textures[name] = texture
            except Exception as e2:
                print(f"Fallback texture creation failed for {name}: {e2}")
                # Store None, we'll handle this in get_texture
                self.textures[name] = None
        
    def get_texture(self, path: str, fallback: str = 'default_character') -> arcade.Texture:
        """Get texture with fallback support"""
        if path in self.textures and self.textures[path] is not None:
            return self.textures[path]
            
        # Try to load the texture
        for base_path in self.asset_paths.values():
            full_path = os.path.join(base_path, path)
            if os.path.exists(full_path):
                try:
                    texture = arcade.load_texture(full_path)
                    self.textures[path] = texture
                    return texture
                except Exception as e:
                    print(f"Error loading texture {full_path}: {e}")
                    
        # Return fallback
        fallback_texture = self.textures.get(fallback)
        if fallback_texture is not None:
            return fallback_texture
        else:
            return self._create_error_texture()
        
    def _create_error_texture(self) -> arcade.Texture:
        """Create an error texture - Arcade 3.0 Compatible"""
        try:
            # Create a magenta error texture using Arcade 3.0 method
            return arcade.make_soft_square_texture(64, (255, 0, 255), outer_alpha=255)
        except Exception as e:
            print(f"Error creating error texture: {e}")
            # Final fallback - try to load any existing texture
            try:
                # Create minimal texture using PIL
                from PIL import Image
                image = Image.new('RGBA', (64, 64), (255, 0, 255, 255))
                return arcade.Texture(image)
            except Exception:
                # If all else fails, return None and let the calling code handle it
                return None
    
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
                    # Create fallback using Arcade 3.0 method
                    self.textures[name] = arcade.make_soft_square_texture(32, (128, 128, 128), outer_alpha=255)
                    
    def create_colored_texture(self, name: str, size: tuple, color: tuple) -> arcade.Texture:
        """Create a solid colored texture - Arcade 3.0 Helper"""
        try:
            # Use Arcade 3.0's make_soft_square_texture
            texture = arcade.make_soft_square_texture(max(size), color, outer_alpha=255)
            self.textures[name] = texture
            return texture
        except Exception as e:
            print(f"Error creating colored texture {name}: {e}")
            # Fallback to PIL
            try:
                from PIL import Image
                image = Image.new('RGBA', size, color + (255,))
                texture = arcade.Texture(image)
                self.textures[name] = texture
                return texture
            except Exception:
                return None
        
    def preload_textures(self, texture_list: list):
        """Preload a list of textures"""
        for texture_path in texture_list:
            self.get_texture(texture_path)
            
    def get_texture_count(self) -> int:
        """Get number of loaded textures"""
        return len([t for t in self.textures.values() if t is not None])
        
    def clear_cache(self):
        """Clear texture cache"""
        self.textures.clear()
        self.generate_default_assets()