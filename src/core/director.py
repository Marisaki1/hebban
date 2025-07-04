"""
Scene management system for Arcade 3.0.0
"""

from typing import Any, Dict, List, Optional

class Scene:
    """Base scene class"""
    
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
    """Scene management system"""
    
    def __init__(self):
        self.scene_stack: List[Scene] = []
        self.scenes: Dict[str, Scene] = {}
        self.systems: Dict[str, Any] = {}
        self.fallback_scene = "main_menu"
        
    def get_system(self, name: str) -> Any:
        """Get a system by name"""
        return self.systems.get(name)
        
    def register_scene(self, name: str, scene: Scene):
        """Register a scene"""
        self.scenes[name] = scene
        
    def push_scene(self, scene_name: str):
        """Push a new scene onto the stack"""
        if scene_name not in self.scenes:
            raise ValueError(f"Scene '{scene_name}' not registered")
            
        # FIXED: Clear input callbacks before scene transition
        input_manager = self.systems.get('input_manager')
        if input_manager:
            input_manager.set_current_scene(scene_name)
            
        # Pause current scene
        if self.scene_stack:
            current_scene = self.scene_stack[-1]
            current_scene.on_pause()
            
        # Add new scene
        new_scene = self.scenes[scene_name]
        self.scene_stack.append(new_scene)
        new_scene.on_enter()
        
    def pop_scene(self):
        """Pop the current scene from the stack"""
        if not self.scene_stack:
            print("Warning: Trying to pop from empty scene stack")
            return
            
        # Exit current scene
        current_scene = self.scene_stack.pop()
        try:
            current_scene.on_exit()
        except Exception as e:
            print(f"Error exiting scene: {e}")
        
        # Resume previous scene or fall back
        if self.scene_stack:
            previous_scene = self.scene_stack[-1]
            print(f"Resuming scene: {previous_scene.__class__.__name__}")
            try:
                # Clear input manager and set to previous scene
                input_manager = self.systems.get('input_manager')
                if input_manager:
                    input_manager.clear_all_callbacks()
                    # Get scene name from class or fallback
                    scene_name = getattr(previous_scene, 'scene_name', 'unknown')
                    input_manager.set_current_scene(scene_name)
                
                # FIXED: Call on_enter() instead of on_resume() to ensure callbacks are registered
                previous_scene.on_enter()
            except Exception as e:
                print(f"Error resuming scene: {e}")
                # Force fallback to main menu
                self.change_scene('main_menu')
        else:
            # Stack is empty - fall back to main menu
            print("Scene stack empty, falling back to main menu")
            if self.fallback_scene in self.scenes:
                self.push_scene(self.fallback_scene)
            else:
                print("ERROR: No fallback scene available!")
                
    def change_scene(self, scene_name: str):
        """Change to a new scene (clear stack)"""
        if scene_name not in self.scenes:
            raise ValueError(f"Scene '{scene_name}' not registered")
        
        # FIXED: Clear input callbacks BEFORE scene changes
        input_manager = self.systems.get('input_manager')
        if input_manager:
            input_manager.clear_all_callbacks()
            input_manager.set_current_scene(scene_name)
        
        # Exit all scenes
        while self.scene_stack:
            scene = self.scene_stack.pop()
            try:
                scene.on_exit()
            except Exception as e:
                print(f"Error exiting scene: {e}")
        
        # Push new scene
        try:
            new_scene = self.scenes[scene_name]
            self.scene_stack.append(new_scene)
            new_scene.on_enter()
        except Exception as e:
            print(f"Error entering scene {scene_name}: {e}")
            # Fallback to main menu
            if scene_name != "main_menu" and "main_menu" in self.scenes:
                self.scene_stack.append(self.scenes["main_menu"])
                self.scenes["main_menu"].on_enter()
        
    def get_current_scene(self) -> Optional[Scene]:
        """Get the current active scene"""
        return self.scene_stack[-1] if self.scene_stack else None
        
    def update(self, delta_time: float):
        """Update current scene"""
        current = self.get_current_scene()
        if current:
            current.update(delta_time)
            
    def draw(self):
        """Draw current scene"""
        current = self.get_current_scene()
        if current:
            current.draw()