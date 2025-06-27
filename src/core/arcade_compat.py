# src/core/arcade_compat.py
"""
Arcade compatibility layer to handle different versions
"""

import arcade

def safe_draw_rectangle_filled(center_x, center_y, width, height, color):
    """Draw filled rectangle with version compatibility"""
    try:
        # Try Arcade 3.0+ syntax
        arcade.draw_rectangle_filled(center_x, center_y, width, height, color)
    except AttributeError:
        try:
            # Try alternative syntax
            arcade.draw.draw_rectangle_filled(center_x, center_y, width, height, color)
        except AttributeError:
            # Fallback: Use shape list
            shape_list = arcade.ShapeElementList()
            shape = arcade.create_filled_rect(center_x, center_y, width, height, color)
            shape_list.append(shape)
            shape_list.draw()

def safe_draw_rectangle_outline(center_x, center_y, width, height, color, border_width=1):
    """Draw rectangle outline with version compatibility"""
    try:
        arcade.draw_rectangle_outline(center_x, center_y, width, height, color, border_width)
    except AttributeError:
        try:
            arcade.draw.draw_rectangle_outline(center_x, center_y, width, height, color, border_width)
        except AttributeError:
            # Fallback: Use shape list
            shape_list = arcade.ShapeElementList()
            shape = arcade.create_outline_rect(center_x, center_y, width, height, color, border_width)
            shape_list.append(shape)
            shape_list.draw()

def safe_draw_text(text, start_x, start_y, color, font_size=12, width=0, align="left", 
                   font_name="Arial", bold=False, italic=False, anchor_x="left", anchor_y="baseline"):
    """Draw text with version compatibility"""
    try:
        arcade.draw_text(text, start_x, start_y, color, font_size, width, align, 
                        font_name, bold, italic, anchor_x, anchor_y)
    except AttributeError:
        try:
            arcade.draw.draw_text(text, start_x, start_y, color, font_size, width, align, 
                                font_name, bold, italic, anchor_x, anchor_y)
        except AttributeError:
            # Very basic fallback
            print(f"Text draw fallback: {text}")

def safe_draw_circle_filled(center_x, center_y, radius, color):
    """Draw filled circle with version compatibility"""
    try:
        arcade.draw_circle_filled(center_x, center_y, radius, color)
    except AttributeError:
        try:
            arcade.draw.draw_circle_filled(center_x, center_y, radius, color)
        except AttributeError:
            # Fallback: Use shape list
            shape_list = arcade.ShapeElementList()
            shape = arcade.create_filled_circle(center_x, center_y, radius, color)
            shape_list.append(shape)
            shape_list.draw()

def safe_draw_line(start_x, start_y, end_x, end_y, color, line_width=1):
    """Draw line with version compatibility"""
    try:
        arcade.draw_line(start_x, start_y, end_x, end_y, color, line_width)
    except AttributeError:
        try:
            arcade.draw.draw_line(start_x, start_y, end_x, end_y, color, line_width)
        except AttributeError:
            # Fallback: Use shape list
            shape_list = arcade.ShapeElementList()
            shape = arcade.create_line(start_x, start_y, end_x, end_y, color, line_width)
            shape_list.append(shape)
            shape_list.draw()

def safe_draw_triangle_filled(x1, y1, x2, y2, x3, y3, color):
    """Draw filled triangle with version compatibility"""
    try:
        arcade.draw_triangle_filled(x1, y1, x2, y2, x3, y3, color)
    except AttributeError:
        try:
            arcade.draw.draw_triangle_filled(x1, y1, x2, y2, x3, y3, color)
        except AttributeError:
            # Fallback: Use shape list
            shape_list = arcade.ShapeElementList()
            shape = arcade.create_filled_polygon([(x1, y1), (x2, y2), (x3, y3)], color)
            shape_list.append(shape)
            shape_list.draw()

def safe_draw_texture_rectangle(center_x, center_y, width, height, texture, angle=0, alpha=255):
    """Draw texture rectangle with version compatibility"""
    try:
        arcade.draw_texture_rectangle(center_x, center_y, width, height, texture, angle, alpha)
    except AttributeError:
        try:
            arcade.draw.draw_texture_rectangle(center_x, center_y, width, height, texture, angle, alpha)
        except AttributeError:
            # Basic fallback - just draw a colored rectangle
            safe_draw_rectangle_filled(center_x, center_y, width, height, arcade.color.GRAY)

# Check Arcade version and create aliases
def setup_arcade_compatibility():
    """Setup compatibility aliases based on Arcade version"""
    import arcade
    
    # Try to determine which drawing functions exist
    if hasattr(arcade, 'draw_rectangle_filled'):
        print("Using standard Arcade drawing functions")
        return 'standard'
    elif hasattr(arcade, 'draw') and hasattr(arcade.draw, 'draw_rectangle_filled'):
        print("Using Arcade.draw module functions")
        return 'draw_module'
    else:
        print("Using compatibility fallback functions")
        return 'fallback'

# Auto-setup on import
_arcade_version = setup_arcade_compatibility()