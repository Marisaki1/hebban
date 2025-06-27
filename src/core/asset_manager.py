# src/core/asset_manager.py
"""
Asset Manager for Arcade 3.0.0 - Fixed texture creation
"""
import os
import arcade
from typing import Dict, Optional

class AssetManager:
    """Manages game assets with robust fallbacks for Arcade 3.0.0"""
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
        """Generate default placeholder assets using the most compatible method"""
        # Create default textures
        self._create_default_texture('default_character', (64, 64), (100, 150, 200))
        self._create_default_texture('default_enemy', (64, 64), (200, 100, 100))
        self._create_default_texture('default_ui_button', (200, 50), (80, 80, 80))
        self._create_default_texture('default_squad_icon', (50, 50), (150, 150, 150))
        
    def _create_default_texture(self, name: str, size: tuple, color: tuple):
        """Create a default colored texture using the most compatible method"""
        try:
            # Method 1: Try Arcade 3.0's Texture.create_filled
            texture = arcade.Texture.create_filled(name, size, color)
            self.textures[name] = texture
            print(f"✓ Created texture {name} using create_filled")
            return
        except Exception as e:
            print(f"Method 1 failed for {name}: {e}")
        
        try:
            # Method 2: Try using PIL to create image then convert to texture
            from PIL import Image
            image = Image.new('RGBA', size, color + (255,))
            texture = arcade.Texture(name, image)
            self.textures[name] = texture
            print(f"✓ Created texture {name} using PIL")
            return
        except Exception as e:
            print(f"Method 2 failed for {name}: {e}")
        
        try:
            # Method 3: Try make_soft_square_texture if available
            size_val = max(size)
            texture = arcade.make_soft_square_texture(size_val, color, outer_alpha=255)
            self.textures[name] = texture
            print(f"✓ Created texture {name} using make_soft_square_texture")
            return
        except Exception as e:
            print(f"Method 3 failed for {name}: {e}")
        
        try:
            # Method 4: Create empty texture as fallback
            texture = arcade.Texture.create_empty(name, size)
            self.textures[name] = texture
            print(f"Created empty texture for {name}")
            return
        except Exception as e:
            print(f"All methods failed for {name}: {e}")
            # Store None and handle it in get_texture
            self.textures[name] = None
        
    def get_texture(self, path: str, fallback: str = 'default_character') -> Optional[arcade.Texture]:
        """Get texture with fallback support"""
        # Return cached texture if available
        if path in self.textures and self.textures[path] is not None:
            return self.textures[path]
            
        # Try to load the texture from file
        for base_path in self.asset_paths.values():
            full_path = os.path.join(base_path, path)
            if os.path.exists(full_path):
                try:
                    texture = arcade.load_texture(full_path)
                    self.textures[path] = texture
                    return texture
                except Exception as e:
                    print(f"Error loading texture {full_path}: {e}")
                    
        # Return fallback texture
        fallback_texture = self.textures.get(fallback)
        if fallback_texture is not None:
            return fallback_texture
        else:
            # Create emergency fallback
            return self._create_emergency_texture(path)
        
    def _create_emergency_texture(self, name: str) -> Optional[arcade.Texture]:
        """Create an emergency fallback texture"""
        try:
            # Try to create a simple 32x32 magenta texture using PIL
            from PIL import Image
            image = Image.new('RGBA', (32, 32), (255, 0, 255, 255))
            texture = arcade.Texture(f"emergency_{name}", image)
            return texture
        except Exception as e:
            print(f"Emergency texture creation failed: {e}")
            return None
    
    def load_game_assets(self):
        """Load all game assets with error handling"""
        print("Loading game assets...")
        
        # Load character sprites with fallbacks
        characters = ['ruka', 'yuki', 'karen', 'tsukasa']
        for char in characters:
            try:
                self._load_character_sprites(char)
            except Exception as e:
                print(f"Error loading sprites for {char}: {e}")
                # Create fallback
                self._create_default_texture(f"{char}_idle", (64, 64), (100, 100, 200))
                
        print("Asset loading complete!")
        
    def _load_character_sprites(self, character_id: str):
        """Load sprites for a specific character"""
        # Try to load character portrait
        portrait_path = f"assets/sprites/characters/portraits/{character_id}_portrait.png"
        if os.path.exists(portrait_path):
            try:
                self.textures[f"{character_id}_portrait"] = arcade.load_texture(portrait_path)
            except Exception as e:
                print(f"Error loading portrait for {character_id}: {e}")
                
        # Try to load idle sprite
        idle_path = f"assets/sprites/characters/{character_id}_idle.png"
        if os.path.exists(idle_path):
            try:
                self.textures[f"{character_id}_idle"] = arcade.load_texture(idle_path)
            except Exception as e:
                print(f"Error loading idle sprite for {character_id}: {e}")
                
    def create_colored_texture(self, name: str, size: tuple, color: tuple) -> Optional[arcade.Texture]:
        """Create a solid colored texture"""
        try:
            # Try the most compatible method
            texture = arcade.Texture.create_filled(name, size, color)
            self.textures[name] = texture
            return texture
        except Exception as e:
            print(f"Error creating colored texture {name}: {e}")
            return None
        
    def preload_textures(self, texture_list: list):
        """Preload a list of textures"""
        for texture_path in texture_list:
            try:
                self.get_texture(texture_path)
            except Exception as e:
                print(f"Error preloading {texture_path}: {e}")
            
    def get_texture_count(self) -> int:
        """Get number of loaded textures"""
        return len([t for t in self.textures.values() if t is not None])
        
    def clear_cache(self):
        """Clear texture cache"""
        self.textures.clear()
        self.generate_default_assets()

    def debug_info(self):
        """Print debug information about loaded assets"""
        print(f"Loaded textures: {self.get_texture_count()}")
        for name, texture in self.textures.items():
            if texture:
                print(f"  {name}: {texture.width}x{texture.height}")
            else:
                print(f"  {name}: NULL")