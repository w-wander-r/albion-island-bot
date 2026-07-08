"""
Humanized mouse movement with multi-backend support.
Supports both X11 (pynput) and Wayland (uinput/evdev).
"""
import random
import time
import math
import os
import platform
import sys
from loguru import logger
from config.settings import (
    MOUSE_SPEED_MIN, MOUSE_SPEED_MAX,
    CLICK_OFFSET_MAX, DOUBLE_CLICK_CHANCE,
    DEBUG_MODE
)

class MouseBackend:
    """Abstract mouse backend interface."""
    def move(self, x, y):
        raise NotImplementedError
    
    def click(self, button='left'):
        raise NotImplementedError
    
    def position(self):
        raise NotImplementedError

class UInputBackend(MouseBackend):
    """Mouse backend using uinput (works on Wayland)."""
    
    def __init__(self):
        import uinput
        import evdev
        
        # Find mouse device
        self.device = self._find_mouse_device()
        
        # Create uinput device
        self.ui = uinput.Device([
            uinput.BTN_LEFT,
            uinput.BTN_RIGHT,
            uinput.REL_X,
            uinput.REL_Y,
            uinput.REL_WHEEL,
        ])
        
        self._x = 0
        self._y = 0
        logger.info("Using uinput backend for mouse control")
    
    def _find_mouse_device(self):
        """Find the first available mouse device."""
        import evdev
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if 'mouse' in device.name.lower():
                logger.debug(f"Found mouse device: {device.name}")
                return device.path
        # Fallback to any pointer device
        for device in devices:
            capabilities = device.capabilities()
            if evdev.ecodes.EV_REL in capabilities:
                logger.debug(f"Using pointer device: {device.name}")
                return device.path
        raise RuntimeError("No mouse device found")
    
    def move(self, x, y):
        """Move mouse relative to current position."""
        # Calculate relative movement
        dx = x - self._x
        dy = y - self._y
        
        # Move in small increments for smooth movement
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps):
            step_x = int(dx / steps)
            step_y = int(dy / steps)
            
            self.ui.emit(uinput.REL_X, step_x)
            self.ui.emit(uinput.REL_Y, step_y)
            time.sleep(0.001)  # Small delay for smooth movement
        
        self._x = x
        self._y = y
    
    def click(self, button='left'):
        """Emit mouse click."""
        btn = uinput.BTN_LEFT if button == 'left' else uinput.BTN_RIGHT
        self.ui.emit(btn, 1)  # Press
        time.sleep(0.05)
        self.ui.emit(btn, 0)  # Release
    
    def position(self):
        """Get current mouse position."""
        return (self._x, self._y)

class PyAutoGUIBackend(MouseBackend):
    """Mouse backend using pyautogui (works everywhere as fallback)."""
    
    def __init__(self):
        import pyautogui
        pyautogui.FAILSAFE = False  # Disable corner failsafe
        pyautogui.PAUSE = 0.05
        logger.info("Using pyautogui backend for mouse control")
    
    def move(self, x, y):
        import pyautogui
        pyautogui.moveTo(x, y)
    
    def click(self, button='left'):
        import pyautogui
        pyautogui.click(button=button)
    
    def position(self):
        import pyautogui
        return pyautogui.position()

class PynputBackend(MouseBackend):
    """Mouse backend using pynput (X11/Windows)."""
    
    def __init__(self):
        from pynput.mouse import Button, Controller
        self.controller = Controller()
        self.Button = Button
        logger.info("Using pynput backend for mouse control")
    
    def move(self, x, y):
        self.controller.position = (int(x), int(y))
    
    def click(self, button='left'):
        btn = self.Button.left if button == 'left' else self.Button.right
        self.controller.click(btn)
    
    def position(self):
        return self.controller.position

def get_mouse_backend():
    """Auto-detect best mouse backend for current system."""
    system = platform.system()
    
    if system == "Linux":
        session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        
        # Try backends in order of preference
        backends = []
        
        # Try pynput if we're on X11 or XWayland
        if session_type != 'wayland' or os.environ.get('WAYLAND_DISPLAY'):
            try:
                from pynput.mouse import Controller
                return PynputBackend()
            except ImportError:
                pass
        
        # Try uinput for Wayland
        try:
            import uinput
            return UInputBackend()
        except ImportError:
            pass
        
        # Fallback to pyautogui
        try:
            import pyautogui
            return PyAutoGUIBackend()
        except ImportError:
            raise RuntimeError(
                "No mouse backend available. Install one of:\n"
                "  pip install pynput    # For X11\n"
                "  pip install python-uinput  # For Wayland\n"
                "  pip install pyautogui  # Universal fallback"
            )
    
    else:  # Windows or Mac
        try:
            return PynputBackend()
        except ImportError:
            try:
                return PyAutoGUIBackend()
            except ImportError:
                raise RuntimeError("No mouse backend available for your platform")

class HumanizedMouse:
    """Mouse controller with human-like movement patterns."""
    
    def __init__(self):
        self.backend = get_mouse_backend()
        self.current_position = self.backend.position()
        self.movement_history = []
        logger.success(f"Mouse initialized with {self.backend.__class__.__name__}")
    
    def move_to(self, x, y, humanize=True):
        """
        Move mouse to coordinates with natural movement.
        
        Args:
            x, y: Target coordinates (absolute screen coordinates)
            humanize: Add randomness and natural curves
        """
        if humanize:
            # Add small random offset
            x += random.randint(-CLICK_OFFSET_MAX, CLICK_OFFSET_MAX)
            y += random.randint(-CLICK_OFFSET_MAX, CLICK_OFFSET_MAX)
        
        start = self.current_position
        end = (int(x), int(y))
        
        # Calculate distance
        distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        
        if distance < 10 or not humanize:
            # Very short movement - just move directly
            self.backend.move(int(x), int(y))
            self.current_position = end
            return
        
        # Generate waypoints for human-like movement
        waypoints = self._generate_waypoints(start, end, distance)
        
        # Execute movement with variable speed
        duration = self._calculate_movement_duration(distance)
        self._execute_waypoint_movement(waypoints, duration)
        
        self.current_position = end
        
        # Log movement for analysis
        self.movement_history.append({
            "start": start,
            "end": end,
            "duration": duration,
            "distance": distance
        })
        
        # Trim history
        if len(self.movement_history) > 100:
            self.movement_history = self.movement_history[-50:]
    
    def click(self, button="left", clicks=1, humanize=True):
        """
        Execute mouse click with human-like timing.
        """
        if humanize and random.random() < DOUBLE_CLICK_CHANCE:
            logger.debug("Simulating accidental extra click")
            self.backend.click(button)
            time.sleep(random.uniform(0.05, 0.1))
        
        for i in range(clicks):
            self.backend.click(button)
            if i < clicks - 1:
                time.sleep(random.uniform(0.05, 0.15))
        
        if humanize:
            time.sleep(random.uniform(0.02, 0.08))
    
    def _generate_waypoints(self, start, end, distance):
        """Generate intermediate waypoints for smooth movement."""
        waypoints = [start]
        
        # Number of intermediate points based on distance
        num_points = max(2, int(distance / 50))
        
        for i in range(1, num_points):
            t = i / num_points
            
            # Base position
            x = start[0] + (end[0] - start[0]) * t
            y = start[1] + (end[1] - start[1]) * t
            
            # Add curve (arc) to movement
            arc = math.sin(t * math.pi) * random.uniform(-50, 50)
            
            # Perpendicular offset
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            length = math.sqrt(dx**2 + dy**2)
            
            if length > 0:
                # Perpendicular direction
                perp_x = -dy / length * arc
                perp_y = dx / length * arc
                
                x += perp_x
                y += perp_y
            
            waypoints.append((int(x), int(y)))
        
        waypoints.append(end)
        return waypoints
    
    def _calculate_movement_duration(self, distance):
        """Calculate movement duration using Fitts's Law."""
        base_time = random.uniform(MOUSE_SPEED_MIN, MOUSE_SPEED_MAX)
        distance_factor = math.log2(distance + 1) * 0.05
        variation = random.uniform(-0.1, 0.1)
        
        return max(0.1, min(base_time + distance_factor + variation, 2.0))
    
    def _execute_waypoint_movement(self, waypoints, duration):
        """Move through waypoints with variable timing."""
        for i in range(1, len(waypoints)):
            point = waypoints[i]
            # Variable delay between waypoints
            delay = (duration / len(waypoints)) * random.uniform(0.7, 1.3)
            self.backend.move(point[0], point[1])
            time.sleep(delay)
    
    def get_position(self):
        """Get current mouse position."""
        return self.backend.position()