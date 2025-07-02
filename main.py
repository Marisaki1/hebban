"""
Heaven Burns Red - Main Game Entry Point
Clean implementation for Arcade 3.0.0, Pillow 11.0.0, Pymunk 6.9.0
"""

import os
import sys
import arcade

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.game import HeavenBurnsRed
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE

def main():
    """Main function"""
    print("=" * 60)
    print("HEAVEN BURNS RED - Platform Game")
    print("Arcade 3.0.0 | Pillow 11.0.0 | Pymunk 6.9.0")
    print("=" * 60)
    
    try:
        game = HeavenBurnsRed(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        game.setup()
        print("✓ Game started successfully")
        arcade.run()
    except KeyboardInterrupt:
        print("\n✓ Game interrupted by user")
    except Exception as e:
        print(f"✗ Fatal error: {e}")
        raise
    finally:
        print("✓ Game closed")

if __name__ == "__main__":
    main()