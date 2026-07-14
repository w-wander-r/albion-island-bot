"""
Albion Online Farm Bot - Main Entry Point
"""
import sys
import time
from loguru import logger
from config.settings import EMERGENCY_STOP_KEY, PAUSE_RESUME_KEY, DEBUG_MODE
from utils.logger import log
from utils.window_manager import WindowManager
from vision.capturer import ScreenCapturer
from input.mouse import HumanizedMouse
from input.keyboard import KeyboardManager

class AlbionBot:
    """Main bot controller."""
    
    def __init__(self):
        logger.info("Initializing Albion Farm Bot components...")
        
        # Core systems
        self.window_manager = WindowManager()
        self.screen_capturer = None  # Will init after finding window
        self.mouse = HumanizedMouse()
        self.keyboard = KeyboardManager()
        
        # Bot state
        self.is_running = False
        self.current_island = None
        
    def initialize(self):
        """Initialize all bot systems."""
        # Find game window
        if not self.window_manager.find_window():
            logger.error("Could not find game window!")
            logger.info("Please make sure Albion Online is running")
            return False
        
        # Initialize screen capture
        self.screen_capturer = ScreenCapturer(self.window_manager)
        
        # Setup hotkeys
        self.keyboard.register_hotkey(EMERGENCY_STOP_KEY, self.emergency_stop)
        self.keyboard.register_hotkey(PAUSE_RESUME_KEY, self.toggle_pause)
        self.keyboard.start_listener()
        
        logger.success("Bot initialization complete!")
        return True
    
    def emergency_stop(self):
        """Emergency stop handler."""
        logger.warning("EMERGENCY STOP ACTIVATED!")
        self.shutdown()
        sys.exit(0)
    
    def toggle_pause(self):
        """Toggle pause state."""
        self.is_running = not self.is_running
        state = "PAUSED" if not self.is_running else "RESUMED"
        logger.info(f"Bot {state}")
    
    def shutdown(self):
        """Clean shutdown of all systems."""
        logger.info("Shutting down bot systems...")
        self.keyboard.stop_listener()
        # Add any cleanup here
    
    def run(self):
        """Main bot loop."""
        if not self.initialize():
            return
        
        logger.info("Bot is ready. Press F9 to start/pause, F8 to emergency stop")
        logger.info("Waiting for start signal...")
        
        # Wait for user to activate
        while not self.is_running and not self.keyboard.is_stopped():
            time.sleep(0.1)
        
        if self.keyboard.is_stopped():
            self.shutdown()
            return
        
        logger.info("Bot started! Beginning farming operations...")
        
        # Main loop
        try:
            while not self.keyboard.is_stopped():
                
                # Check if paused
                if self.keyboard.is_paused_bot():
                    time.sleep(0.5)
                    continue
                
                # Test screen capture
                if self.screen_capturer:
                    frame = self.screen_capturer.capture_game_window()
                    if frame is not None:
                        if DEBUG_MODE:
                            stats = self.screen_capturer.get_capture_stats()
                            logger.debug(f"Capture stats: {stats}")
                
                # Simulate bot working
                logger.info("Bot cycle running...")
                time.sleep(2)  # Placeholder for actual operations
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.exception(f"Unexpected error in main loop: {e}")
        finally:
            self.shutdown()

def main():
    """Main entry point."""
    bot = AlbionBot()
    bot.run()

if __name__ == "__main__":
    main()