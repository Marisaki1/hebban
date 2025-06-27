# src/core/arcade_compat.py
"""
Working Arcade 3.0.0 compatibility layer - Uses SpriteSolidColor primarily
"""

import arcade

# Global flag to track what works
_drawing_mode = None

def _detect_drawing_mode():
    """Detect which drawing methods actually work"""
    global _drawing_mode
    if _drawing_mode is not None:
        return _drawing_mode
    
    # Test what actually works in this Arcade installation
    print("Detecting Arcade drawing capabilities...")
    
    # Test SpriteSolidColor (most reliable)
    try:
        sprite = arcade.SpriteSolidColor(1, 1, arcade.color.WHITE)
        _drawing_mode = "sprites"
        print("✓ Using sprite-based drawing")
        return _drawing_mode
    except Exception as e:
        print(f"✗ SpriteSolidColor failed: {e}")
    
    # If nothing works, we're in trouble
    _drawing_mode = "none"
    print("✗ No working drawing methods found")
    return _drawing_mode

def safe_draw_rectangle_filled(center_x, center_y, width, height, color):
    """Draw filled rectangle using SpriteSolidColor"""
    mode = _detect_drawing_mode()
    
    if mode == "sprites":
        try:
            # Use SpriteSolidColor - this should work
            sprite = arcade.SpriteSolidColor(int(width), int(height), color)
            sprite.center_x = center_x
            sprite.center_y = center_y
            sprite.draw()
            return
        except Exception as e:
            print(f"SpriteSolidColor failed: {e}")
    
    # Final fallback - just print
    print(f"Rectangle: {center_x}, {center_y}, {width}x{height}, {color}")

def safe_draw_rectangle_outline(center_x, center_y, width, height, color, border_width=1):
    """Draw rectangle outline using thin sprites"""
    mode = _detect_drawing_mode()
    
    if mode == "sprites":
        try:
            # Draw 4 thin rectangles to make an outline
            # Top border
            top_sprite = arcade.SpriteSolidColor(int(width), int(border_width), color)
            top_sprite.center_x = center_x
            top_sprite.center_y = center_y + height/2 - border_width/2
            top_sprite.draw()
            
            # Bottom border
            bottom_sprite = arcade.SpriteSolidColor(int(width), int(border_width), color)
            bottom_sprite.center_x = center_x
            bottom_sprite.center_y = center_y - height/2 + border_width/2
            bottom_sprite.draw()
            
            # Left border
            left_sprite = arcade.SpriteSolidColor(int(border_width), int(height), color)
            left_sprite.center_x = center_x - width/2 + border_width/2
            left_sprite.center_y = center_y
            left_sprite.draw()
            
            # Right border
            right_sprite = arcade.SpriteSolidColor(int(border_width), int(height), color)
            right_sprite.center_x = center_x + width/2 - border_width/2
            right_sprite.center_y = center_y
            right_sprite.draw()
            return
        except Exception as e:
            print(f"Rectangle outline failed: {e}")
    
    print(f"Rectangle outline: {center_x}, {center_y}, {width}x{height}, {color}")

def safe_draw_text(text, start_x, start_y, color, font_size=12, width=0, align="left", 
                   font_name="Arial", bold=False, italic=False, anchor_x="left", anchor_y="baseline"):
    """Draw text with maximum compatibility"""
    
    # Try different text drawing methods
    methods = [
        # Method 1: Full parameters
        lambda: arcade.draw_text(text, start_x, start_y, color, font_size, width, align, 
                                font_name, bold, italic, anchor_x, anchor_y),
        # Method 2: Essential parameters only
        lambda: arcade.draw_text(text, start_x, start_y, color, font_size),
        # Method 3: Try arcade.Text class if it exists
        lambda: _draw_with_text_class(text, start_x, start_y, color, font_size),
    ]
    
    for i, method in enumerate(methods):
        try:
            method()
            return
        except Exception as e:
            continue
    
    # Final fallback
    print(f"Text: '{text}' at ({start_x}, {start_y})")

def _draw_with_text_class(text, x, y, color, size):
    """Try using arcade.Text class if available"""
    if hasattr(arcade, 'Text'):
        text_obj = arcade.Text(text, x, y, color, size)
        text_obj.draw()
    else:
        raise AttributeError("No Text class")

def safe_draw_circle_filled(center_x, center_y, radius, color):
    """Draw filled circle using a square sprite"""
    mode = _detect_drawing_mode()
    
    if mode == "sprites":
        try:
            # Use a square as circle approximation
            size = int(radius * 2)
            sprite = arcade.SpriteSolidColor(size, size, color)
            sprite.center_x = center_x
            sprite.center_y = center_y
            sprite.draw()
            return
        except Exception as e:
            print(f"Circle sprite failed: {e}")
    
    print(f"Circle: {center_x}, {center_y}, radius {radius}, {color}")

def safe_draw_line(start_x, start_y, end_x, end_y, color, line_width=1):
    """Draw line using a thin rotated sprite"""
    mode = _detect_drawing_mode()
    
    if mode == "sprites":
        try:
            import math
            
            # Calculate line properties
            dx = end_x - start_x
            dy = end_y - start_y
            length = math.sqrt(dx*dx + dy*dy)
            angle = math.degrees(math.atan2(dy, dx))
            
            # Create thin sprite for line
            sprite = arcade.SpriteSolidColor(int(length), int(line_width), color)
            sprite.center_x = (start_x + end_x) / 2
            sprite.center_y = (start_y + end_y) / 2
            sprite.angle = angle
            sprite.draw()
            return
        except Exception as e:
            print(f"Line sprite failed: {e}")
    
    print(f"Line: ({start_x}, {start_y}) to ({end_x}, {end_y})")

def safe_draw_triangle_filled(x1, y1, x2, y2, x3, y3, color):
    """Draw triangle using a square approximation"""
    mode = _detect_drawing_mode()
    
    if mode == "sprites":
        try:
            # Calculate triangle center and approximate size
            center_x = (x1 + x2 + x3) / 3
            center_y = (y1 + y2 + y3) / 3
            
            # Use a small square as triangle approximation
            sprite = arcade.SpriteSolidColor(20, 20, color)
            sprite.center_x = center_x
            sprite.center_y = center_y
            sprite.draw()
            return
        except Exception as e:
            print(f"Triangle sprite failed: {e}")
    
    print(f"Triangle: ({x1}, {y1}), ({x2}, {y2}), ({x3}, {y3})")

def safe_draw_texture_rectangle(center_x, center_y, width, height, texture, angle=0, alpha=255):
    """Draw texture using sprite"""
    try:
        # Create sprite with texture
        sprite = arcade.Sprite()
        sprite.texture = texture
        sprite.center_x = center_x
        sprite.center_y = center_y
        sprite.angle = angle
        sprite.alpha = alpha
        
        # Scale sprite to desired size if needed
        if texture and texture.width > 0 and texture.height > 0:
            sprite.scale_x = width / texture.width
            sprite.scale_y = height / texture.height
        
        sprite.draw()
        return
    except Exception as e:
        print(f"Texture sprite failed: {e}")
    
    # Fallback to colored rectangle
    safe_draw_rectangle_filled(center_x, center_y, width, height, arcade.color.GRAY)

# Initialize drawing mode on import
_detect_drawing_mode()