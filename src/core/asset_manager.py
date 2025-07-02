# src/core/asset_manager.py
"""
Asset Manager for Arcade 3.0.0 and Pillow 11.0.0 - Completely rewritten
"""
import os
import arcade
from typing import Dict, Optional

class AssetManager:
    """Manages game assets with robust fallbacks for Arcade 3.0.0 and Pillow 11.0.0"""
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
        """Generate default placeholder assets using Arcade 3.0.0 and Pillow 11.0.0 compatible methods"""
        # Create default textures
        self._create_default_texture('default_character', (64, 64), (100, 150, 200))
        self._create_default_texture('default_enemy', (64, 64), (200, 100, 100))
        self._create_default_texture('default_ui_button', (200, 50), (80, 80, 80))
        self._create_default_texture('default_squad_icon', (50, 50), (150, 150, 150))
        
    def _create_default_texture(self, name: str, size: tuple, color: tuple):
        """Create a default colored texture using Arcade 3.0.0 and Pillow 11.0.0 compatible methods"""
        try:
            # Method 1: Try Arcade 3.0.0's Texture.create_filled
            texture = arcade.Texture.create_filled(name, size, color)
            self.textures[name] = texture
            print(f"✓ Created texture {name} using Arcade 3.0.0 create_filled")
            return
        except Exception as e:
            print(f"Method 1 failed for {name}: {e}")
        
        try:
            # Method 2: Try using Pillow 11.0.0 to create image then convert to texture
            from PIL import Image
            
            # Ensure we have RGBA color tuple
            if len(color) == 3:
                color = color + (255,)
            elif len(color) == 4:
                pass  # Already RGBA
            else:
                color = (color[0], color[1], color[2], 255)
            
            # Create image using Pillow 11.0.0
            image = Image.new('RGBA', size, color)
            texture = arcade.Texture(name, image)
            self.textures[name] = texture
            print(f"✓ Created texture {name} using Pillow 11.0.0")
            return
        except Exception as e:
            print(f"Method 2 failed for {name}: {e}")
        
        try:
            # Method 3: Try older arcade methods for compatibility
            if hasattr(arcade, 'make_soft_square_texture'):
                size_val = max(size)
                texture = arcade.make_soft_square_texture(size_val, color, outer_alpha=255)
                self.textures[name] = texture
                print(f"✓ Created texture {name} using make_soft_square_texture")
                return
        except Exception as e:
            print(f"Method 3 failed for {name}: {e}")
        
        try:
            # Method 4: Create empty texture as ultimate fallback
            if hasattr(arcade.Texture, 'create_empty'):
                texture = arcade.Texture.create_empty(name, size)
                self.textures[name] = texture
                print(f"Created empty texture for {name}")
                return
        except Exception as e:
            print(f"Method 4 failed for {name}: {e}")
        
        # Final fallback - store None and handle it in get_texture
        print(f"All texture creation methods failed for {name}")
        self.textures[name] = None
        
    def get_texture(self, path: str, fallback: str = 'default_character') -> Optional[arcade.Texture]:
        """Get texture with fallback support for Arcade 3.0.0"""
        # Return cached texture if available
        if path in self.textures and self.textures[path] is not None:
            return self.textures[path]
            
        # Try to load the texture from file using Arcade 3.0.0 methods
        for base_path in self.asset_paths.values():
            full_path = os.path.join(base_path, path)
            if os.path.exists(full_path):
                try:
                    # Arcade 3.0.0 simplified texture loading
                    texture = arcade.load_texture(full_path)
                    self.textures[path] = texture
                    return texture
                except Exception as e:
                    print(f"Error loading texture {full_path}: {e}")
                    
        # Try direct path loading
        if os.path.exists(path):
            try:
                texture = arcade.load_texture(path)
                self.textures[path] = texture
                return texture
            except Exception as e:
                print(f"Error loading texture {path}: {e}")
                    
        # Return fallback texture
        fallback_texture = self.textures.get(fallback)
        if fallback_texture is not None:
            return fallback_texture
        else:
            # Create emergency fallback
            return self._create_emergency_texture(path)
        
    def _create_emergency_texture(self, name: str) -> Optional[arcade.Texture]:
        """Create an emergency fallback texture using Pillow 11.0.0"""
        try:
            # Use Pillow 11.0.0 to create a simple emergency texture
            from PIL import Image, ImageDraw
            
            # Create a 32x32 magenta texture with text
            image = Image.new('RGBA', (32, 32), (255, 0, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Add a border
            draw.rectangle([0, 0, 31, 31], outline=(255, 255, 255, 255), width=1)
            
            # Try to add text (fallback if font fails)
            try:
                # Draw simple text indicator
                draw.text((2, 2), "?", fill=(255, 255, 255, 255))
            except:
                # Draw a simple cross if text fails
                draw.line([0, 0, 31, 31], fill=(255, 255, 255, 255), width=1)
                draw.line([0, 31, 31, 0], fill=(255, 255, 255, 255), width=1)
            
            texture = arcade.Texture(f"emergency_{name}", image)
            return texture
        except Exception as e:
            print(f"Emergency texture creation failed: {e}")
            return None
    
    def load_game_assets(self):
        """Load all game assets with error handling"""
        print("Loading game assets...")
        
        # Load character sprites with fallbacks
        characters = ['ruka', 'yuki', 'karen', 'tsukasa', 'megumi', 'ichigo']
        for char in characters:
            try:
                self._load_character_sprites(char)
            except Exception as e:
                print(f"Error loading sprites for {char}: {e}")
                # Create fallback
                self._create_default_texture(f"{char}_idle", (64, 64), (100, 100, 200))
                self._create_default_texture(f"{char}_portrait", (128, 128), (120, 120, 220))
                
        print("Asset loading complete!")
        
    def _load_character_sprites(self, character_id: str):
        """Load sprites for a specific character"""
        # Try to load character portrait
        portrait_paths = [
            f"assets/sprites/characters/portraits/{character_id}_portrait.png",
            f"assets/sprites/characters/{character_id}_portrait.png",
            f"portraits/{character_id}_portrait.png"
        ]
        
        for portrait_path in portrait_paths:
            if os.path.exists(portrait_path):
                try:
                    self.textures[f"{character_id}_portrait"] = arcade.load_texture(portrait_path)
                    print(f"✓ Loaded portrait for {character_id}")
                    break
                except Exception as e:
                    print(f"Error loading portrait {portrait_path}: {e}")
        else:
            # Create default portrait if none found
            self._create_default_texture(f"{character_id}_portrait", (128, 128), (120, 120, 220))
                
        # Try to load idle sprite
        idle_paths = [
            f"assets/sprites/characters/{character_id}_idle.png",
            f"sprites/characters/{character_id}_idle.png",
            f"{character_id}_idle.png"
        ]
        
        for idle_path in idle_paths:
            if os.path.exists(idle_path):
                try:
                    self.textures[f"{character_id}_idle"] = arcade.load_texture(idle_path)
                    print(f"✓ Loaded idle sprite for {character_id}")
                    break
                except Exception as e:
                    print(f"Error loading idle sprite {idle_path}: {e}")
        else:
            # Create default idle sprite if none found
            self._create_default_texture(f"{character_id}_idle", (64, 64), (100, 150, 200))
                
    def create_colored_texture(self, name: str, size: tuple, color: tuple) -> Optional[arcade.Texture]:
        """Create a solid colored texture using Arcade 3.0.0 methods"""
        try:
            # Use the main texture creation method
            self._create_default_texture(name, size, color)
            return self.textures.get(name)
        except Exception as e:
            print(f"Error creating colored texture {name}: {e}")
            return None
        
    def create_sprite_from_texture(self, texture_name: str) -> arcade.Sprite:
        """Create a sprite from a cached texture"""
        texture = self.get_texture(texture_name)
        sprite = arcade.Sprite()
        if texture:
            sprite.texture = texture
        return sprite
        
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
                try:
                    print(f"  {name}: {texture.width}x{texture.height}")
                except:
                    print(f"  {name}: Texture object (size unknown)")
            else:
                print(f"  {name}: NULL")
                
    def get_version_info(self):
        """Get version information for debugging"""
        info = {}
        
        # Arcade version
        try:
            info['arcade'] = arcade.version.VERSION
        except:
            try:
                info['arcade'] = arcade.__version__
            except:
                info['arcade'] = "Unknown"
        
        # Pillow version
        try:
            from PIL import __version__ as pil_version
            info['pillow'] = pil_version
        except:
            try:
                import PIL
                info['pillow'] = PIL.__version__
            except:
                info['pillow'] = "Unknown"
        
        return info

# Create global instance
asset_manager = AssetManager()