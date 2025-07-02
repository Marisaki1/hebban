# src/core/sprite_manager.py
"""
Sprite Manager for loading and managing character sprites - Fixed for Arcade 3.0 and Pillow 11.0.0
"""

import os
import arcade
from typing import Dict, List, Optional, Tuple
from src.systems.animation import Animation, AnimationController, AnimationState
from src.data.squad_data import SPRITE_CONFIG

class SpriteManager:
    """Manages all sprite loading and animation creation - Fixed for Arcade 3.0 and Pillow 11.0.0"""
    
    def __init__(self):
        self.sprite_cache: Dict[str, arcade.Texture] = {}
        self.animation_cache: Dict[str, Animation] = {}
        self.sprite_base_path = "assets/sprites/characters"
        self.portrait_path = "assets/sprites/characters/portraits"
        
        # Animation speed multipliers (can be adjusted per character)
        self.animation_speeds: Dict[str, float] = {
            "idle": 1.0,
            "walk": 1.0,
            "run": 1.0,
            "jump": 1.0,
            "fall": 1.0,
            "attack1": 1.0,
            "attack2": 1.0,
            "hurt": 1.0,
            "death": 1.0
        }
        
    def set_animation_speed(self, animation_name: str, speed_multiplier: float):
        """Set the speed multiplier for a specific animation type"""
        if animation_name in self.animation_speeds:
            self.animation_speeds[animation_name] = speed_multiplier
            
    def set_character_animation_speed(self, character_id: str, animation_name: str, speed_multiplier: float):
        """Set animation speed for a specific character's animation"""
        key = f"{character_id}_{animation_name}_speed"
        self.animation_speeds[key] = speed_multiplier
        
    def get_animation_speed(self, character_id: str, animation_name: str) -> float:
        """Get the animation speed for a character's animation"""
        # Check for character-specific speed first
        char_key = f"{character_id}_{animation_name}_speed"
        if char_key in self.animation_speeds:
            return self.animation_speeds[char_key]
        # Fall back to general animation speed
        return self.animation_speeds.get(animation_name, 1.0)
        
    def load_character_sprites(self, character_id: str) -> bool:
        """Load all sprites for a character using Arcade 3.0 and Pillow 11.0.0"""
        loaded_any = False
        
        # Expected sprite files
        sprite_files = {
            "idle": f"{character_id}_idle.png",
            "walk": f"{character_id}_walk.png",
            "run": f"{character_id}_run.png",
            "jump": f"{character_id}_jump.png",
            "fall": f"{character_id}_fall.png",
            "attack1": f"{character_id}_attack1.png",
            "attack2": f"{character_id}_attack2.png",
            "hurt": f"{character_id}_hurt.png",
            "death": f"{character_id}_death.png"
        }
        
        # Load each sprite sheet
        for anim_name, filename in sprite_files.items():
            filepath = os.path.join(self.sprite_base_path, filename)
            
            if os.path.exists(filepath):
                try:
                    # Load the sprite sheet
                    config = SPRITE_CONFIG["animations"][anim_name]
                    frames = self._load_sprite_sheet(
                        filepath,
                        character_id,
                        anim_name,
                        config["frame_count"],
                        SPRITE_CONFIG["frame_size"]
                    )
                    
                    if frames:
                        # Create animation with configurable speed
                        speed_mult = self.get_animation_speed(character_id, anim_name)
                        frame_duration = config["frame_duration"] / speed_mult
                        
                        animation = Animation(
                            frames,
                            frame_duration,
                            config["loop"]
                        )
                        
                        # Cache the animation
                        anim_key = f"{character_id}_{anim_name}"
                        self.animation_cache[anim_key] = animation
                        loaded_any = True
                        
                        print(f"✓ Loaded {anim_name} animation for {character_id}")
                except Exception as e:
                    print(f"Error loading sprite sheet {filepath}: {e}")
            else:
                print(f"Warning: Sprite file not found: {filepath}")
                
            # Create placeholder animation if loading failed or file missing
            if f"{character_id}_{anim_name}" not in self.animation_cache:
                frames = []
                config = SPRITE_CONFIG["animations"][anim_name]
                for i in range(config["frame_count"]):
                    placeholder = self._create_placeholder_texture(character_id, anim_name)
                    if placeholder:
                        frames.append(placeholder)
                
                if frames:
                    speed_mult = self.get_animation_speed(character_id, anim_name)
                    frame_duration = config["frame_duration"] / speed_mult
                    
                    animation = Animation(
                        frames,
                        frame_duration,
                        config["loop"]
                    )
                    
                    anim_key = f"{character_id}_{anim_name}"
                    self.animation_cache[anim_key] = animation
                    loaded_any = True
        
        # Load portrait
        portrait_file = f"{character_id}_portrait.png"
        portrait_path = os.path.join(self.portrait_path, portrait_file)
        
        if os.path.exists(portrait_path):
            try:
                texture = arcade.load_texture(portrait_path)
                self.sprite_cache[f"{character_id}_portrait"] = texture
                print(f"✓ Loaded portrait for {character_id}")
                loaded_any = True
            except Exception as e:
                print(f"Error loading portrait for {character_id}: {e}")
        
        # Create placeholder portrait if not loaded
        if f"{character_id}_portrait" not in self.sprite_cache:
            placeholder_portrait = self._create_placeholder_texture(character_id, "portrait", (256, 256))
            if placeholder_portrait:
                self.sprite_cache[f"{character_id}_portrait"] = placeholder_portrait
                loaded_any = True
                
        return loaded_any
        
    def _load_sprite_sheet(self, filepath: str, character_id: str, animation_name: str, 
                          frame_count: int, frame_size: Tuple[int, int]) -> List[arcade.Texture]:
        """Load a sprite sheet and return list of frame textures using Arcade 3.0"""
        frames = []
        
        try:
            # Calculate frame width (assuming horizontal layout)
            frame_width, frame_height = frame_size
            
            # Load each frame using Arcade 3.0 methods
            for i in range(frame_count):
                # Create a unique name for each frame
                frame_name = f"{character_id}_{animation_name}_frame{i}"
                
                try:
                    # Load frame from sprite sheet
                    texture = arcade.load_texture(
                        filepath,
                        x=i * frame_width,
                        y=0,
                        width=frame_width,
                        height=frame_height
                    )
                    
                    # Cache the texture
                    self.sprite_cache[frame_name] = texture
                    frames.append(texture)
                    
                except Exception as e:
                    print(f"Error loading frame {i} from {filepath}: {e}")
                    # Create placeholder frame
                    placeholder = self._create_placeholder_texture(character_id, f"{animation_name}_f{i}")
                    if placeholder:
                        frames.append(placeholder)
                
        except Exception as e:
            print(f"Error loading sprite sheet {filepath}: {e}")
            
        # If no frames loaded, create placeholder frames
        if not frames:
            for i in range(frame_count):
                placeholder = self._create_placeholder_texture(character_id, f"{animation_name}_f{i}")
                if placeholder:
                    frames.append(placeholder)
                
        return frames
        
    def _create_placeholder_texture(self, character_id: str, animation_name: str, size: Tuple[int, int] = None) -> Optional[arcade.Texture]:
        """Create a placeholder texture if sprite is missing using Pillow 11.0.0"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Use default size if not specified
            if size is None:
                size = SPRITE_CONFIG["frame_size"]
            width, height = size
            
            # Get character color from squad data
            from src.data.squad_data import SQUAD_DATA
            char_color = (100, 100, 100)  # Default gray
            
            # Find character in squads to get their color
            for squad in SQUAD_DATA.values():
                for member in squad['members']:
                    if member['id'] == character_id:
                        color = member.get('color', (100, 100, 100))
                        char_color = color[:3]  # Ensure RGB only
                        break
            
            # Create image with character color using Pillow 11.0.0
            # Ensure RGBA format for compatibility
            rgba_color = char_color + (255,)  # Add alpha
            image = Image.new('RGBA', (width, height), rgba_color)
            draw = ImageDraw.Draw(image)
            
            # Draw border
            draw.rectangle([0, 0, width-1, height-1], outline=(255, 255, 255, 255), width=2)
            
            # Add text to identify the character and animation
            text_lines = [character_id[:4].upper(), animation_name[:4]]
            
            # Try to use a better font if available, otherwise use default
            try:
                # Try to find a system font
                font_paths = [
                    "arial.ttf", "Arial.ttf", "arial.TTF",
                    "/System/Library/Fonts/Arial.ttf",  # macOS
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                    "C:/Windows/Fonts/arial.ttf"  # Windows
                ]
                
                font = None
                for font_path in font_paths:
                    try:
                        font = ImageFont.truetype(font_path, 12)
                        break
                    except:
                        continue
                        
                if font is None:
                    font = ImageFont.load_default()
                    
            except Exception:
                font = None
                
            # Draw text
            y_offset = height // 3
            for line in text_lines:
                try:
                    if font:
                        bbox = draw.textbbox((0, 0), line, font=font)
                        text_width = bbox[2] - bbox[0]
                    else:
                        # Estimate text width if font loading failed
                        text_width = len(line) * 8
                        
                    text_x = (width - text_width) // 2
                    draw.text((text_x, y_offset), line, fill=(255, 255, 255, 255), font=font)
                    y_offset += 15
                except Exception as e:
                    print(f"Error drawing text on placeholder: {e}")
                    # Draw a simple rectangle as fallback
                    draw.rectangle([text_x, y_offset, text_x + text_width, y_offset + 10], fill=(255, 255, 255, 255))
                    y_offset += 15
            
            # Convert to arcade texture using proper Arcade 3.0 constructor
            texture_name = f"{character_id}_{animation_name}_placeholder"
            texture = arcade.Texture(texture_name, image)
            return texture
            
        except Exception as e:
            print(f"Error creating placeholder texture: {e}")
            return None
        
    def create_animation_controller(self, character_id: str) -> AnimationController:
        """Create a fully configured animation controller for a character"""
        controller = AnimationController()
        
        # Map animation names to AnimationState enum
        anim_mapping = {
            "idle": AnimationState.IDLE,
            "walk": AnimationState.WALK,
            "run": AnimationState.RUN,
            "jump": AnimationState.JUMP,
            "fall": AnimationState.FALL,
            "attack1": AnimationState.ATTACK_1,
            "attack2": AnimationState.ATTACK_2,
            "hurt": AnimationState.HURT,
            "death": AnimationState.DEATH
        }
        
        # Add all cached animations for this character
        for anim_name, state in anim_mapping.items():
            anim_key = f"{character_id}_{anim_name}"
            if anim_key in self.animation_cache:
                controller.add_animation(state, self.animation_cache[anim_key])
            else:
                print(f"Warning: No animation found for {anim_key}")
                
        return controller
        
    def get_portrait(self, character_id: str) -> Optional[arcade.Texture]:
        """Get the portrait texture for a character"""
        portrait_key = f"{character_id}_portrait"
        
        # Return cached if available
        if portrait_key in self.sprite_cache:
            return self.sprite_cache[portrait_key]
        
        # Try to load it
        self.load_character_sprites(character_id)
        return self.sprite_cache.get(portrait_key)
        
    def preload_squad_sprites(self, squad_members: List[str]):
        """Preload all sprites for a squad"""
        print(f"Preloading sprites for squad members: {squad_members}")
        
        for member_id in squad_members:
            try:
                success = self.load_character_sprites(member_id)
                if not success:
                    print(f"Warning: No sprites loaded for {member_id}")
            except Exception as e:
                print(f"Error preloading sprites for {member_id}: {e}")
                
    def update_all_animation_speeds(self):
        """Update all cached animations with current speed settings"""
        for key, animation in self.animation_cache.items():
            try:
                parts = key.split('_')
                if len(parts) >= 2:
                    char_id = parts[0]
                    anim_name = '_'.join(parts[1:])
                    
                    # Get the speed multiplier
                    speed_mult = self.get_animation_speed(char_id, anim_name)
                    
                    # Get original frame duration from config
                    if anim_name in SPRITE_CONFIG["animations"]:
                        base_duration = SPRITE_CONFIG["animations"][anim_name]["frame_duration"]
                        animation.frame_duration = base_duration / speed_mult
            except Exception as e:
                print(f"Error updating animation speed for {key}: {e}")

    def get_texture_count(self) -> int:
        """Get number of loaded textures"""
        return len([t for t in self.sprite_cache.values() if t is not None])
        
    def clear_cache(self):
        """Clear all cached sprites"""
        self.sprite_cache.clear()
        self.animation_cache.clear()
        
    def debug_info(self):
        """Print debug information"""
        print(f"Sprite Manager - Textures: {self.get_texture_count()}, Animations: {len(self.animation_cache)}")
        for name, texture in list(self.sprite_cache.items())[:10]:  # Show first 10
            if texture:
                try:
                    print(f"  {name}: {texture.width}x{texture.height}")
                except:
                    print(f"  {name}: Texture object")

# Global sprite manager instance
sprite_manager = SpriteManager()