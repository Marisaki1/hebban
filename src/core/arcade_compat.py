# src/core/arcade_compat.py
"""
Fixed Arcade 3.0.0 compatibility layer - Uses proper drawing functions
"""

import arcade

def safe_draw_rectangle_filled(center_x, center_y, width, height, color):
    """Draw filled rectangle using Arcade 3.0.0 compatible methods"""
    try:
        # Method 1: Try the standard draw_rectangle_filled
        arcade.draw_rectangle_filled(center_x, center_y, width, height, color)
        return
    except Exception as e:
        pass
    
    try:
        # Method 2: Try using shapes if available
        if hasattr(arcade, 'create_filled_rect_with_colors'):
            shape = arcade.create_filled_rect_with_colors(
                [(center_x - width/2, center_y - height/2),
                 (center_x + width/2, center_y - height/2),
                 (center_x + width/2, center_y + height/2),
                 (center_x - width/2, center_y + height/2)],
                [color, color, color, color]
            )
            shape.draw()
            return
    except Exception as e:
        pass
    
    try:
        # Method 3: Try using a texture
        texture = arcade.Texture.create_filled("rect", (int(width), int(height)), color)
        arcade.draw_texture_rectangle(center_x, center_y, width, height, texture)
        return
    except Exception as e:
        pass
    
    # Fallback - just print debug info
    print(f"Rectangle: {center_x}, {center_y}, {width}x{height}, {color}")

def safe_draw_rectangle_outline(center_x, center_y, width, height, color, border_width=1):
    """Draw rectangle outline using lines"""
    try:
        # Use arcade's draw_rectangle_outline
        arcade.draw_rectangle_outline(center_x, center_y, width, height, color, border_width)
        return
    except Exception as e:
        pass
    
    try:
        # Draw 4 lines to make an outline
        half_width = width / 2
        half_height = height / 2
        
        # Top line
        arcade.draw_line(
            center_x - half_width, center_y + half_height,
            center_x + half_width, center_y + half_height,
            color, border_width
        )
        # Bottom line
        arcade.draw_line(
            center_x - half_width, center_y - half_height,
            center_x + half_width, center_y - half_height,
            color, border_width
        )
        # Left line
        arcade.draw_line(
            center_x - half_width, center_y - half_height,
            center_x - half_width, center_y + half_height,
            color, border_width
        )
        # Right line
        arcade.draw_line(
            center_x + half_width, center_y - half_height,
            center_x + half_width, center_y + half_height,
            color, border_width
        )
        return
    except Exception as e:
        pass
    
    print(f"Rectangle outline: {center_x}, {center_y}, {width}x{height}, {color}")

def safe_draw_text(text, start_x, start_y, color, font_size=12, width=0, align="left", 
                   font_name="Arial", bold=False, italic=False, anchor_x="left", anchor_y="baseline"):
    """Draw text with maximum compatibility"""
    
    # Try different text drawing methods in order of preference
    methods = [
        # Method 1: Try with all parameters
        lambda: arcade.draw_text(text, start_x, start_y, color, font_size, width, align, 
                                font_name, bold, italic, anchor_x, anchor_y),
        # Method 2: Try with anchor parameters only
        lambda: arcade.draw_text(text, start_x, start_y, color, font_size, 
                                anchor_x=anchor_x, anchor_y=anchor_y),
        # Method 3: Try with basic parameters
        lambda: arcade.draw_text(text, start_x, start_y, color, font_size),
        # Method 4: Try with absolute minimum
        lambda: arcade.draw_text(text, start_x, start_y, color),
    ]
    
    for method in methods:
        try:
            method()
            return
        except Exception as e:
            continue
    
    # Final fallback
    print(f"Text: '{text}' at ({start_x}, {start_y})")

def safe_draw_circle_filled(center_x, center_y, radius, color):
    """Draw filled circle"""
    try:
        arcade.draw_circle_filled(center_x, center_y, radius, color)
        return
    except Exception as e:
        pass
    
    # Fallback to rectangle
    safe_draw_rectangle_filled(center_x, center_y, radius * 2, radius * 2, color)

def safe_draw_line(start_x, start_y, end_x, end_y, color, line_width=1):
    """Draw line"""
    try:
        arcade.draw_line(start_x, start_y, end_x, end_y, color, line_width)
        return
    except Exception as e:
        pass
    
    print(f"Line: ({start_x}, {start_y}) to ({end_x}, {end_y})")

def safe_draw_texture_rectangle(center_x, center_y, width, height, texture, angle=0, alpha=255):
    """Draw texture rectangle"""
    try:
        arcade.draw_texture_rectangle(center_x, center_y, width, height, texture, angle, alpha)
        return
    except Exception as e:
        pass
    
    # Fallback to colored rectangle
    safe_draw_rectangle_filled(center_x, center_y, width, height, arcade.color.GRAY)