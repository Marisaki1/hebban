import arcade
import os

class AssetLoader:
    """Helper class to load all game assets"""
    
    @staticmethod
    def load_character_sprites(asset_manager, character_id: str):
        """Load all sprites for a character"""
        base_path = f"assets/sprites/characters/{character_id}"
        
        # Load idle sprite
        idle_path = f"{base_path}_idle.png"
        if os.path.exists(idle_path):
            asset_manager.textures[f"{character_id}_idle"] = arcade.load_texture(idle_path)
            
        # Load walk animation (sprite sheet)
        walk_path = f"{base_path}_walk_sheet.png"
        if os.path.exists(walk_path):
            # Load sprite sheet (8 frames, 64x64 each)
            for i in range(8):
                texture = arcade.load_texture(walk_path, x=i*64, y=0, width=64, height=64)
                asset_manager.textures[f"{character_id}_walk_{i}"] = texture
                
        # Load portrait
        portrait_path = f"assets/sprites/characters/portraits/{character_id}_portrait.png"
        if os.path.exists(portrait_path):
            asset_manager.textures[f"{character_id}_portrait"] = arcade.load_texture(portrait_path)