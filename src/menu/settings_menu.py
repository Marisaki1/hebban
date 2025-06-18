# ============================================================================
# FILE: src/menu/settings_menu.py
# ============================================================================
class SettingsMenu(MenuState):
    """Game settings menu"""
    def __init__(self, director, input_manager):
        super().__init__(director, input_manager)
        self.title = "Settings"
        self.categories = ['Video', 'Audio', 'Controls', 'Game']
        self.current_category = 0
        self.settings_items = {
            'Video': [
                {'name': 'Resolution', 'type': 'choice', 'options': ['1280x720', '1920x1080', '2560x1440'], 'current': 0},
                {'name': 'Fullscreen', 'type': 'toggle', 'value': False},
                {'name': 'VSync', 'type': 'toggle', 'value': True},
                {'name': 'FPS Limit', 'type': 'choice', 'options': ['30', '60', '120', 'Unlimited'], 'current': 1}
            ],
            'Audio': [
                {'name': 'Master Volume', 'type': 'slider', 'value': 1.0, 'min': 0.0, 'max': 1.0},
                {'name': 'SFX Volume', 'type': 'slider', 'value': 1.0, 'min': 0.0, 'max': 1.0},
                {'name': 'Music Volume', 'type': 'slider', 'value': 0.8, 'min': 0.0, 'max': 1.0},
                {'name': 'Mute All', 'type': 'toggle', 'value': False}
            ],
            'Controls': [
                {'name': 'Jump', 'type': 'keybind', 'key': 'SPACE'},
                {'name': 'Move Left', 'type': 'keybind', 'key': 'A'},
                {'name': 'Move Right', 'type': 'keybind', 'key': 'D'},
                {'name': 'Action 1', 'type': 'keybind', 'key': 'Z'},
                {'name': 'Action 2', 'type': 'keybind', 'key': 'X'},
                {'name': 'Controller Vibration', 'type': 'toggle', 'value': True}
            ],
            'Game': [
                {'name': 'Difficulty', 'type': 'choice', 'options': ['Easy', 'Normal', 'Hard', 'Nightmare'], 'current': 1},
                {'name': 'Show FPS', 'type': 'toggle', 'value': False},
                {'name': 'Auto-Save', 'type': 'toggle', 'value': True},
                {'name': 'Language', 'type': 'choice', 'options': ['English', '日本語', '中文'], 'current': 0}
            ]
        }
        self.selected_setting = 0
        self.editing_keybind = False
        
    def draw_setting_item(self, item: dict, x: float, y: float, selected: bool):
        """Draw individual setting item"""
        # Background
        bg_color = arcade.color.DARK_RED if selected else arcade.color.DARK_GRAY
        arcade.draw_rectangle_filled(x, y, 600, 40, bg_color)
        
        # Setting name
        arcade.draw_text(
            item['name'],
            x - 280, y,
            arcade.color.WHITE,
            16,
            anchor_y="center"
        )
        
        # Setting value/control
        if item['type'] == 'toggle':
            value_text = "ON" if item['value'] else "OFF"
            value_color = arcade.color.GREEN if item['value'] else arcade.color.RED
        elif item['type'] == 'slider':
            # Draw slider bar
            bar_width = 200
            bar_x = x + 100
            arcade.draw_rectangle_filled(bar_x, y, bar_width, 4, arcade.color.GRAY)
            
            # Draw slider handle
            handle_x = bar_x - bar_width/2 + (item['value'] * bar_width)
            arcade.draw_circle_filled(handle_x, y, 8, arcade.color.WHITE)
            
            value_text = f"{int(item['value'] * 100)}%"
            value_color = arcade.color.WHITE
        elif item['type'] == 'choice':
            value_text = item['options'][item['current']]
            value_color = arcade.color.YELLOW
        elif item['type'] == 'keybind':
            if self.editing_keybind and selected:
                value_text = "Press any key..."
                value_color = arcade.color.ORANGE
            else:
                value_text = item['key']
                value_color = arcade.color.CYAN
                
        if item['type'] != 'slider':
            arcade.draw_text(
                value_text,
                x + 200, y,
                value_color,
                16,
                anchor_x="center",
                anchor_y="center"
            )
            
    def draw(self):
        """Draw settings menu"""
        arcade.start_render()
        
        # Background
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            (20, 20, 20)
        )
        
        # Title
        arcade.draw_text(
            self.title,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 60,
            arcade.color.CRIMSON,
            36,
            anchor_x="center",
            font_name="Arial",
            bold=True
        )
        
        # Category tabs
        tab_x = 200
        for i, category in enumerate(self.categories):
            color = arcade.color.CRIMSON if i == self.current_category else arcade.color.DARK_GRAY
            arcade.draw_rectangle_filled(tab_x + i * 150, SCREEN_HEIGHT - 120, 140, 40, color)
            arcade.draw_text(
                category,
                tab_x + i * 150, SCREEN_HEIGHT - 120,
                arcade.color.WHITE,
                18,
                anchor_x="center",
                anchor_y="center"
            )
            
        # Settings items
        settings = self.settings_items[self.categories[self.current_category]]
        start_y = SCREEN_HEIGHT - 200
        
        for i, item in enumerate(settings):
            self.draw_setting_item(
                item,
                SCREEN_WIDTH // 2,
                start_y - i * 60,
                i == self.selected_setting
            )
            
        # Instructions
        arcade.draw_text(
            "Use LEFT/RIGHT to change categories, UP/DOWN to select, ENTER to modify",
            SCREEN_WIDTH // 2,
            40,
            arcade.color.WHITE,
            14,
            anchor_x="center"
        )
        
    def navigate_up(self):
        """Navigate to previous setting"""
        current_settings = self.settings_items[self.categories[self.current_category]]
        self.selected_setting = (self.selected_setting - 1) % len(current_settings)
        
    def navigate_down(self):
        """Navigate to next setting"""
        current_settings = self.settings_items[self.categories[self.current_category]]
        self.selected_setting = (self.selected_setting + 1) % len(current_settings)
        
    def change_category(self, direction: int):
        """Change settings category"""
        self.current_category = (self.current_category + direction) % len(self.categories)
        self.selected_setting = 0
        
    def modify_setting(self, direction: int = 0):
        """Modify selected setting"""
        current_settings = self.settings_items[self.categories[self.current_category]]
        setting = current_settings[self.selected_setting]
        
        if setting['type'] == 'toggle':
            setting['value'] = not setting['value']
        elif setting['type'] == 'choice':
            setting['current'] = (setting['current'] + direction) % len(setting['options'])
        elif setting['type'] == 'slider':
            setting['value'] = max(setting['min'], min(setting['max'], setting['value'] + direction * 0.1))
        elif setting['type'] == 'keybind':
            self.editing_keybind = True
