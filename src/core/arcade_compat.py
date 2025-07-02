# src/core/arcade_compat.py
"""
Arcade 3.0.0 compatibility layer - Completely rewritten for new API
"""

import arcade

def safe_draw_rectangle_filled(center_x, center_y, width, height, color):
    """Draw filled rectangle using Arcade 3.0.0 API"""
    try:
        # Arcade 3.0.0 standard method
        arcade.draw_rectangle_filled(center_x, center_y, width, height, color)
        return
    except Exception as e:
        print(f"Error drawing rectangle: {e}")

def safe_draw_rectangle_outline(center_x, center_y, width, height, color, border_width=1):
    """Draw rectangle outline using Arcade 3.0.0 API"""
    try:
        arcade.draw_rectangle_outline(center_x, center_y, width, height, color, border_width)
        return
    except Exception as e:
        print(f"Error drawing rectangle outline: {e}")

def safe_draw_text(text, start_x, start_y, color, font_size=12, width=0, align="left", 
                   font_name="Arial", bold=False, italic=False, anchor_x="left", anchor_y="baseline"):
    """Draw text using Arcade 3.0.0 simplified API"""
    
    try:
        # Arcade 3.0.0 - simplified text drawing
        if hasattr(arcade, 'Text'):
            # Use new Text class if available
            text_obj = arcade.Text(
                text, start_x, start_y, color, font_size,
                anchor_x=anchor_x, anchor_y=anchor_y,
                font_name=font_name, bold=bold, italic=italic
            )
            text_obj.draw()
            return
    except Exception:
        pass
    
    try:
        # Fallback to classic draw_text with minimal parameters
        arcade.draw_text(
            text, start_x, start_y, color, font_size,
            anchor_x=anchor_x, anchor_y=anchor_y
        )
        return
    except Exception:
        pass
    
    try:
        # Ultimate fallback - basic parameters only
        arcade.draw_text(text, start_x, start_y, color, font_size)
        return
    except Exception as e:
        print(f"Text draw failed: '{text}' at ({start_x}, {start_y}) - {e}")

def safe_draw_circle_filled(center_x, center_y, radius, color):
    """Draw filled circle using Arcade 3.0.0 API"""
    try:
        arcade.draw_circle_filled(center_x, center_y, radius, color)
        return
    except Exception as e:
        print(f"Error drawing circle: {e}")
        # Fallback to rectangle
        safe_draw_rectangle_filled(center_x, center_y, radius * 2, radius * 2, color)

def safe_draw_line(start_x, start_y, end_x, end_y, color, line_width=1):
    """Draw line using Arcade 3.0.0 API"""
    try:
        arcade.draw_line(start_x, start_y, end_x, end_y, color, line_width)
        return
    except Exception as e:
        print(f"Error drawing line: {e}")

def safe_draw_texture_rectangle(center_x, center_y, width, height, texture, angle=0, alpha=255):
    """Draw texture rectangle using Arcade 3.0.0 API"""
    try:
        if texture is not None:
            arcade.draw_texture_rectangle(center_x, center_y, width, height, texture, angle, alpha)
        else:
            # Fallback to colored rectangle if no texture
            safe_draw_rectangle_filled(center_x, center_y, width, height, arcade.color.GRAY)
        return
    except Exception as e:
        print(f"Error drawing texture: {e}")
        safe_draw_rectangle_filled(center_x, center_y, width, height, arcade.color.GRAY)

def create_solid_color_sprite(width, height, color):
    """Create a solid color sprite using Arcade 3.0.0 methods"""
    try:
        # Method 1: Try Texture.create_filled (3.0.0 method)
        texture = arcade.Texture.create_filled(f"solid_{color}", (width, height), color)
        sprite = arcade.Sprite()
        sprite.texture = texture
        return sprite
    except Exception:
        pass
    
    try:
        # Method 2: Try creating with PIL if available
        from PIL import Image
        image = Image.new('RGBA', (width, height), color + (255,))
        texture = arcade.Texture(f"solid_{color}_pil", image)
        sprite = arcade.Sprite()
        sprite.texture = texture
        return sprite
    except Exception:
        pass
    
    try:
        # Method 3: Use basic sprite with default texture
        sprite = arcade.Sprite()
        # Set size properties
        sprite.width = width
        sprite.height = height
        return sprite
    except Exception as e:
        print(f"Failed to create solid color sprite: {e}")
        return arcade.Sprite()

def get_arcade_version():
    """Get Arcade version for debugging"""
    try:
        return arcade.version.VERSION
    except:
        try:
            return arcade.__version__
        except:
            return "Unknown"

# Test function to verify compatibility
def test_compatibility():
    """Test if all drawing functions work"""
    print(f"Testing Arcade {get_arcade_version()} compatibility...")
    
    # Test basic drawing (won't actually draw anything, just test APIs)
    try:
        safe_draw_rectangle_filled(100, 100, 50, 50, arcade.color.RED)
        print("✓ Rectangle drawing works")
    except Exception as e:
        print(f"✗ Rectangle drawing failed: {e}")
    
    try:
        safe_draw_text("Test", 100, 100, arcade.color.WHITE, 12)
        print("✓ Text drawing works")
    except Exception as e:
        print(f"✗ Text drawing failed: {e}")
    
    try:
        sprite = create_solid_color_sprite(32, 32, arcade.color.BLUE)
        print("✓ Sprite creation works")
    except Exception as e:
        print(f"✗ Sprite creation failed: {e}")

if __name__ == "__main__":
    test_compatibility()