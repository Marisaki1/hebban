import arcade
from typing import Any, Dict, List, Optional

class Scene:
    """Base scene class for all game scenes"""
    def __init__(self, director):
        self.director = director
        
    def on_enter(self):
        """Called when scene becomes active"""
        pass
        
    def on_exit(self):
        """Called when scene becomes inactive"""
        pass
        
    def on_pause(self):
        """Called when scene is paused"""
        pass
        
    def on_resume(self):
        """Called when scene is resumed"""
        pass
        
    def update(self, delta_time: float):
        """Update scene logic"""
        pass
        
    def draw(self):
        """Draw scene"""
        pass
        
    def on_key_press(self, key, modifiers):
        """Handle key press"""
        pass
        
    def on_key_release(self, key, modifiers):
        """Handle key release"""
        pass
        
    def on_mouse_motion(self, x, y, dx, dy):
        """Handle mouse motion"""
        pass
        
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse press"""
        pass

class Director:
    """Enhanced Director with system management and better scene handling"""
    def __init__(self):
        self.scene_stack: List[Scene] = []
        self.scenes: Dict[str, Scene] = {}
        self.systems: Dict[str, Any] = {}  # Store references to game systems
        self.fallback_scene = None  # Scene to fall back to if stack becomes empty
        
    def get_system(self, name: str) -> Any:
        """Get a system by name"""
        return self.systems.get(name)
        
    def register_scene(self, name: str, scene: Scene):
        """Register a scene with a name"""
        self.scenes[name] = scene
        
        # Set the first registered scene as fallback
        if self.fallback_scene is None:
            self.fallback_scene = name
            
    def set_fallback_scene(self, scene_name: str):
        """Set the fallback scene to use when stack is empty"""
        if scene_name in self.scenes:
            self.fallback_scene = scene_name
        
    def push_scene(self, scene_name: str):
        """Push a new scene onto the stack"""
        if scene_name not in self.scenes:
            raise ValueError(f"Scene '{scene_name}' not registered")
            
        print(f"Pushing scene: {scene_name}")
        
        # Pause current scene
        if self.scene_stack:
            current_scene = self.scene_stack[-1]
            current_scene.on_pause()
            print(f"Paused scene: {type(current_scene).__name__}")
            
        # Add new scene
        new_scene = self.scenes[scene_name]
        self.scene_stack.append(new_scene)
        new_scene.on_enter()
        print(f"Entered scene: {type(new_scene).__name__}")
        
    def pop_scene(self):
        """Pop the current scene from the stack"""
        if not self.scene_stack:
            print("Warning: Tried to pop from empty scene stack")
            return
            
        print(f"Popping scene, stack size: {len(self.scene_stack)}")
        
        # Exit current scene
        current_scene = self.scene_stack.pop()
        current_scene.on_exit()
        print(f"Exited scene: {type(current_scene).__name__}")
        
        # Resume previous scene or fall back to main menu
        if self.scene_stack:
            previous_scene = self.scene_stack[-1]
            previous_scene.on_resume()
            print(f"Resumed scene: {type(previous_scene).__name__}")
        else:
            print("Scene stack is empty, falling back to main menu")
            if self.fallback_scene and self.fallback_scene in self.scenes:
                self.push_scene(self.fallback_scene)
            else:
                print("Warning: No fallback scene available!")
                
    def change_scene(self, scene_name: str):
        """Change to a new scene (clear stack)"""
        print(f"Changing to scene: {scene_name}")
        
        # Exit all scenes
        while self.scene_stack:
            scene = self.scene_stack.pop()
            scene.on_exit()
            print(f"Exited scene during change: {type(scene).__name__}")
            
        # Push new scene
        self.push_scene(scene_name)
        
    def get_current_scene(self) -> Optional[Scene]:
        """Get the current active scene"""
        return self.scene_stack[-1] if self.scene_stack else None
        
    def get_scene_stack_info(self) -> str:
        """Get debug info about current scene stack"""
        if not self.scene_stack:
            return "Empty scene stack"
        
        info = f"Scene stack ({len(self.scene_stack)} scenes):\n"
        for i, scene in enumerate(self.scene_stack):
            info += f"  {i}: {type(scene).__name__}\n"
        return info
        
    def update(self, delta_time: float):
        """Update current scene"""
        current = self.get_current_scene()
        if current:
            current.update(delta_time)
        else:
            print("Warning: No current scene to update")
            
    def draw(self):
        """Draw current scene"""
        current = self.get_current_scene()
        if current:
            current.draw()
        else:
            # Draw a fallback screen if no scene is available
            arcade.start_render()
            arcade.draw_rectangle_filled(640, 360, 1280, 720, (20, 20, 20))
            arcade.draw_text(
                "No Scene Available",
                640, 360,
                arcade.color.WHITE,
                48,
                anchor_x="center",
                anchor_y="center"
            )
            print("Warning: No current scene to draw, showing fallback")