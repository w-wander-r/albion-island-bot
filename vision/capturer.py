"""
Screen capture system with platform-specific optimizations.
Windows: DXcam (fastest, requires window to be visible)
Linux: MSS (reliable, works on X11/Wayland)
"""
import platform
import time
import numpy as np
from pathlib import Path
from loguru import logger
from config.settings import SCREEN_CAPTURE_INTERVAL, DEBUG_MODE, SAVE_SCREENSHOTS

class ScreenCapturer:
    """Cross-platform screen capture with window targeting."""
    
    def __init__(self, window_manager):
        self.window_manager = window_manager
        self.platform = platform.system()
        self.capture_method = None
        self.last_capture_time = 0
        self.frame_count = 0
        
        # Initialize platform-specific capturer
        self._init_capturer()
        
    def _init_capturer(self):
        """Initialize the appropriate capture method based on platform."""
        if self.platform == "Windows":
            self._init_dxcam()
        elif self.platform == "Linux":
            self._init_mss()
        else:
            logger.error(f"Unsupported platform: {self.platform}")
            raise OSError(f"Unsupported platform: {self.platform}")
    
    def _init_dxcam(self):
        """Initialize DXcam for Windows (high performance)."""
        try:
            import dxcam
            self.capture_method = dxcam.create(output_color="BGR")
            logger.info("DXcam initialized for Windows capture")
        except ImportError:
            logger.warning("DXcam not available, falling back to MSS")
            self._init_mss()
    
    def _init_mss(self):
        """Initialize MSS for Linux/Mac or Windows fallback."""
        import mss
        self.capture_method = mss.mss()
        logger.info("MSS initialized for screen capture")
    
    def capture_game_window(self):
        """
        Capture only the game window region.
        Returns numpy array (height, width, 3) in BGR format.
        """
        # Rate limiting for performance
        current_time = time.time()
        if current_time - self.last_capture_time < SCREEN_CAPTURE_INTERVAL:
            return None
        
        self.last_capture_time = current_time
        self.frame_count += 1
        
        # Get window region
        window_rect = self.window_manager.get_window_rect()
        if not window_rect:
            logger.error("Game window not found!")
            return None
        
        # Platform-specific capture
        if self.platform == "Windows" and hasattr(self.capture_method, 'grab'):
            return self._capture_dxcam(window_rect)
        else:
            return self._capture_mss(window_rect)
    
    def _capture_dxcam(self, window_rect):
        """DXcam capture for Windows."""
        left, top, width, height = window_rect
        region = (left, top, left + width, top + height)
        
        frame = self.capture_method.grab(region=region)
        
        if frame is not None:
            # DXcam returns numpy array already
            if DEBUG_MODE and SAVE_SCREENSHOTS and self.frame_count % 100 == 0:
                self._debug_save(frame, "dxcam")
            return frame
        
        return None
    
    def _capture_mss(self, window_rect):
        """MSS capture for Linux or Windows fallback."""
        left, top, width, height = window_rect
        
        # MSS uses different region format
        monitor = {
            "left": left,
            "top": top,
            "width": width,
            "height": height
        }
        
        # Capture screen
        screenshot = self.capture_method.grab(monitor)
        
        # Convert to numpy array (BGR format for OpenCV)
        frame = np.array(screenshot)
        frame = frame[:, :, :3]  # Remove alpha channel
        frame = frame[:, :, ::-1]  # RGB to BGR
        
        if DEBUG_MODE and SAVE_SCREENSHOTS and self.frame_count % 100 == 0:
            self._debug_save(frame, "mss")
        
        return frame
    
    def _debug_save(self, frame, method):
        """Save debug screenshots."""
        from datetime import datetime
        import cv2
        
        debug_dir = Path("data/debug_screenshots")
        debug_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = debug_dir / f"capture_{method}_{timestamp}_{self.frame_count}.png"
        cv2.imwrite(str(filename), frame)
        logger.debug(f"Debug screenshot saved: {filename}")
    
    def get_capture_stats(self):
        """Get capture performance statistics."""
        return {
            "method": type(self.capture_method).__name__,
            "platform": self.platform,
            "frame_count": self.frame_count,
            "fps": self.frame_count / max(time.time() - self.last_capture_time, 0.001)
        }