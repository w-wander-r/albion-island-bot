"""
Window management utilities for finding and monitoring the game window.
Platform-specific implementations for Windows and Linux.
"""
import time
import platform
from loguru import logger

class WindowManager:
    """Handles finding and monitoring the game window."""
    
    def __init__(self, window_title="Albion Online"):
        self.window_title = window_title
        self.window_handle = None
        self.window_rect = None  # (left, top, width, height)
        self.platform = platform.system()
        self._init_platform_specific()
        
    def _init_platform_specific(self):
        """Initialize platform-specific window handling."""
        if self.platform == "Linux":
            self._init_linux()
        elif self.platform == "Windows":
            self._init_windows()
    
    def _init_linux(self):
        """Initialize Linux-specific window handling using X11."""
        try:
            import subprocess
            # Check if xdotool is available
            result = subprocess.run(['which', 'xdotool'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Using xdotool for Linux window management")
            else:
                logger.warning("xdotool not found. Install it: sudo pacman -S xdotool")
        except Exception:
            logger.warning("Could not check for xdotool")
    
    def _init_windows(self):
        """Initialize Windows-specific window handling using win32gui."""
        try:
            import win32gui
            import win32con
            logger.info("Using win32gui for Windows window management")
        except ImportError:
            logger.error("win32gui not installed. Install: pip install pywin32")
    
    def find_window(self):
        """
        Find the game window by title.
        Updates window_handle and window_rect on success.
        """
        logger.info(f"Searching for window: '{self.window_title}'")
        
        if self.platform == "Linux":
            return self._find_window_linux()
        elif self.platform == "Windows":
            return self._find_window_windows()
        
        return False
    
    def _find_window_linux(self):
        """Find window on Linux using xdotool."""
        import subprocess
        
        try:
            # Search for window by title
            result = subprocess.run(
                ['xdotool', 'search', '--name', self.window_title],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                window_ids = result.stdout.strip().split('\n')
                self.window_handle = window_ids[0]  # Use first match
                
                # Get window geometry
                geo_result = subprocess.run(
                    ['xdotool', 'getwindowgeometry', self.window_handle],
                    capture_output=True,
                    text=True
                )
                
                if geo_result.returncode == 0:
                    # Parse geometry output
                    # Format: "Window 12345\n  Position: 100,200 (screen: 0)\n  Geometry: 800x600"
                    lines = geo_result.stdout.split('\n')
                    for line in lines:
                        if 'Position:' in line:
                            pos = line.split(':')[1].strip().split('(')[0]
                            x, y = map(int, pos.split(','))
                        if 'Geometry:' in line:
                            size = line.split(':')[1].strip()
                            w, h = map(int, size.split('x'))
                    
                    self.window_rect = (x, y, w, h)
                    logger.info(f"Found window at {x},{y} size {w}x{h}")
                    return True
                    
            logger.error(f"Window '{self.window_title}' not found")
            return False
            
        except subprocess.TimeoutExpired:
            logger.error("Window search timed out")
            return False
        except Exception as e:
            logger.error(f"Error finding window on Linux: {e}")
            return False
    
    def _find_window_windows(self):
        """Find window on Windows using win32gui."""
        try:
            import win32gui
            
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if self.window_title.lower() in title.lower():
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(callback, windows)
            
            if windows:
                self.window_handle = windows[0]
                
                # Get window rectangle
                rect = win32gui.GetWindowRect(self.window_handle)
                x, y, x2, y2 = rect
                self.window_rect = (x, y, x2 - x, y2 - y)
                
                logger.info(f"Found window at {x},{y} size {x2-x}x{y2-y}")
                return True
            
            logger.error(f"Window '{self.window_title}' not found")
            return False
            
        except Exception as e:
            logger.error(f"Error finding window on Windows: {e}")
            return False
    
    def get_window_rect(self):
        """Get current window position and dimensions."""
        if not self.window_rect:
            self.find_window()
        return self.window_rect
    
    def is_window_focused(self):
        """Check if game window is currently focused."""
        if self.platform == "Linux":
            return self._is_focused_linux()
        elif self.platform == "Windows":
            return self._is_focused_windows()
        return False
    
    def _is_focused_linux(self):
        """Check window focus on Linux."""
        import subprocess
        try:
            result = subprocess.run(
                ['xdotool', 'getactivewindow'],
                capture_output=True,
                text=True
            )
            return result.stdout.strip() == str(self.window_handle)
        except:
            return False
    
    def _is_focused_windows(self):
        """Check window focus on Windows."""
        try:
            import win32gui
            return self.window_handle == win32gui.GetForegroundWindow()
        except:
            return False
    
    def focus_window(self):
        """Bring game window to foreground."""
        if self.platform == "Linux":
            import subprocess
            subprocess.run(['xdotool', 'windowactivate', str(self.window_handle)])
        elif self.platform == "Windows":
            import win32gui
            win32gui.SetForegroundWindow(self.window_handle)