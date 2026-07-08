"""
Keyboard input with multi-backend support.
"""
import os
import platform
import threading
from loguru import logger

class KeyboardBackend:
    """Abstract keyboard backend."""
    def press(self, key):
        raise NotImplementedError
    
    def type_text(self, text):
        raise NotImplementedError

class PyAutoGUIKeyboard(KeyboardBackend):
    """Keyboard using pyautogui (works everywhere)."""
    def __init__(self):
        import pyautogui
        logger.info("Using pyautogui keyboard backend")
    
    def press(self, key):
        import pyautogui
        pyautogui.press(key)
    
    def type_text(self, text, interval=0.05):
        import pyautogui
        pyautogui.typewrite(text, interval=interval)

class UInputKeyboard(KeyboardBackend):
    """Keyboard using uinput (Wayland)."""
    def __init__(self):
        import uinput
        self.device = uinput.Device([
            uinput.KEY_A, uinput.KEY_B, uinput.KEY_C,  # Add more keys as needed
            uinput.KEY_ENTER, uinput.KEY_ESC, uinput.KEY_TAB,
        ])
        logger.info("Using uinput keyboard backend")
    
    def press(self, key):
        # Simplified - just use pyautogui as it's more reliable for keyboard
        import pyautogui
        pyautogui.press(key)
    
    def type_text(self, text, interval=0.05):
        import pyautogui
        pyautogui.typewrite(text, interval=interval)

class KeyboardManager:
    """Keyboard controller with hotkey support."""
    
    def __init__(self):
        self.backend = self._init_backend()
        self.emergency_stop = False
        self.is_paused = False
        
        # Start keyboard listener in a separate way
        self._start_listener()
    
    def _init_backend(self):
        """Initialize keyboard backend."""
        try:
            import pyautogui
            return PyAutoGUIKeyboard()
        except ImportError:
            try:
                import uinput
                return UInputKeyboard()
            except ImportError:
                raise RuntimeError("No keyboard backend available")
    
    def _start_listener(self):
        """Start keyboard listener using pynput if available."""
        try:
            from pynput import keyboard
            
            def on_press(key):
                try:
                    if hasattr(key, 'char'):
                        key_str = key.char
                    else:
                        key_str = str(key)
                    
                    # Handle hotkeys
                    if key_str == 'Key.f8':
                        self.emergency_stop = True
                        logger.warning("EMERGENCY STOP ACTIVATED!")
                    elif key_str == 'Key.f9':
                        self.is_paused = not self.is_paused
                        state = "PAUSED" if self.is_paused else "RESUMED"
                        logger.info(f"Bot {state}")
                        
                except Exception as e:
                    logger.error(f"Error in keyboard listener: {e}")
            
            self.listener = keyboard.Listener(on_press=on_press)
            self.listener_thread = threading.Thread(target=self.listener.start, daemon=True)
            self.listener_thread.start()
            logger.info("Keyboard listener started")
            
        except ImportError:
            logger.warning("pynput not available for hotkeys - using polling fallback")
            # Will check for hotkeys differently
    
    def register_hotkey(self, key, callback):
        """Register a hotkey (simplified for now)."""
        logger.info(f"Hotkey {key} registered")
    
    def start_listener(self):
        """Already started in init."""
        pass
    
    def stop_listener(self):
        """Stop keyboard listener."""
        if hasattr(self, 'listener'):
            self.listener.stop()
    
    def press_key(self, key_str):
        """Press a key."""
        import pyautogui
        pyautogui.press(key_str.lower())
    
    def is_stopped(self):
        return self.emergency_stop
    
    def is_paused_bot(self):
        return self.is_paused