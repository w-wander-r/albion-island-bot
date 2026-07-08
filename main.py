"""
Albion Online Farm Bot - Main Entry Point
"""
import sys
from loguru import logger
from config.settings import EMERGENCY_STOP_KEY, PAUSE_RESUME_KEY
from utils.logger import log

def emergency_stop_handler():
    """Handle emergency stop hotkey."""
    logger.warning("EMERGENCY STOP ACTIVATED!")
    sys.exit(0)

def pause_resume_handler():
    """Handle pause/resume functionality."""
    logger.info("Pause/Resume toggled")
    # TODO: Implement pause flag

def setup_hotkeys():
    """Register global hotkeys for control."""
    logger.info(f"Registering hotkeys: Emergency Stop [{EMERGENCY_STOP_KEY}], "
                f"Pause/Resume [{PAUSE_RESUME_KEY}]")
    # TODO: Implement global hotkeys with pynput

def main():
    """Main bot entry point."""
    logger.info("="*50)
    logger.info("Albion Online Farm Bot Starting")
    logger.info("="*50)
    
    # Setup emergency controls
    setup_hotkeys()
    
    # TODO: Initialize bot components
    # TODO: Load island configurations
    # TODO: Start main bot loop
    
    logger.info("Bot is ready. Waiting for start signal...")

if __name__ == "__main__":
    main()