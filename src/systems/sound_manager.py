"""
Sound management system
"""

import arcade
import os
from typing import Dict, Optional

class SoundManager:
    """Manages all game audio"""
    
    def __init__(self):
        self.master_volume = 1.0
        self.sfx_volume = 1.0
        self.music_volume = 0.8
        
        self.current_music = None
        self.music_player = None
        
        # Sound cache
        self.sounds: Dict[str, arcade.Sound] = {}
        
        # Sound mappings (placeholder files)
        self.sound_mappings = {
            "collect_health": "collect_health.wav",
            "collect_coin": "collect_coin.wav", 
            "collect_powerup": "collect_powerup.wav",
            "dash_attack": "dash_attack.wav",
            "air_dash": "air_dash.wav",
            "quick_strike": "quick_strike.wav",
            "game_over": "game_over.wav",
            "victory": "victory.wav",
            "jump": "jump.wav",
            "land": "land.wav",
            "hurt": "hurt.wav",
            "enemy_hit": "enemy_hit.wav",
            "enemy_death": "enemy_death.wav",
            "menu_select": "menu_select.wav",
            "menu_navigate": "menu_navigate.wav",
            "menu_back": "menu_back.wav"
        }
        
        # Music mappings
        self.music_mappings = {
            "menu_theme": "menu_theme.ogg",
            "battle_theme": "battle_theme.ogg",
            "escape_theme": "escape_theme.ogg",
            "boss_theme": "boss_theme.ogg",
            "victory_theme": "victory_theme.ogg"
        }
        
    def set_master_volume(self, volume: float):
        """Set master volume (0.0 to 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.music_player:
            self.music_player.volume = self.music_volume * self.master_volume
            
    def set_sfx_volume(self, volume: float):
        """Set SFX volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        
    def load_sound(self, sound_name: str) -> bool:
        """Load a sound file"""
        if sound_name in self.sounds:
            return True
            
        # Try to find sound file
        filename = self.sound_mappings.get(sound_name, f"{sound_name}.wav")
        
        # Check common sound directories
        search_paths = [
            f"assets/sounds/sfx/{filename}",
            f"assets/sounds/{filename}",
            f"sounds/{filename}",
            filename
        ]
        
        for filepath in search_paths:
            if os.path.exists(filepath):
                try:
                    self.sounds[sound_name] = arcade.load_sound(filepath)
                    return True
                except Exception as e:
                    print(f"Error loading sound {filepath}: {e}")
                    
        # Create placeholder sound (silent)
        print(f"Sound file not found: {filename} - using placeholder")
        return False
        
    def play_sfx(self, sound_name: str, volume: float = 1.0):
        """Play a sound effect"""
        if sound_name not in self.sounds:
            if not self.load_sound(sound_name):
                return  # Skip if sound couldn't be loaded
                
        if sound_name in self.sounds:
            try:
                final_volume = volume * self.sfx_volume * self.master_volume
                arcade.play_sound(self.sounds[sound_name], final_volume)
            except Exception as e:
                print(f"Error playing sound {sound_name}: {e}")
                
    def play_music(self, track_name: str, loop: bool = True, volume: float = 1.0):
        """Play background music"""
        if track_name == self.current_music:
            return  # Already playing
            
        # Stop current music
        self.stop_music()
        
        # Try to find music file
        filename = self.music_mappings.get(track_name, f"{track_name}.ogg")
        
        search_paths = [
            f"assets/sounds/music/{filename}",
            f"assets/sounds/{filename}",
            f"music/{filename}",
            filename
        ]
        
        for filepath in search_paths:
            if os.path.exists(filepath):
                try:
                    music = arcade.load_sound(filepath)
                    final_volume = volume * self.music_volume * self.master_volume
                    self.music_player = arcade.play_sound(music, final_volume, looping=loop)
                    self.current_music = track_name
                    return
                except Exception as e:
                    print(f"Error playing music {filepath}: {e}")
                    
        print(f"Music file not found: {filename}")
        
    def stop_music(self):
        """Stop current music"""
        if self.music_player:
            try:
                self.music_player.pause()
            except:
                pass
            self.music_player = None
        self.current_music = None
        
    def pause_music(self):
        """Pause current music"""
        if self.music_player:
            try:
                self.music_player.pause()
            except:
                pass
                
    def resume_music(self):
        """Resume paused music"""
        if self.music_player:
            try:
                self.music_player.play()
            except:
                pass
                
    def is_music_playing(self) -> bool:
        """Check if music is currently playing"""
        return self.music_player is not None and self.current_music is not None
        
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_music()
        self.sounds.clear()