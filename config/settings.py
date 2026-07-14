"""
Global bot settings and configuration.
Modify these values based on your setup and preferences.
"""
import json
from pathlib import Path

# Project paths
ROOT_DIR = Path(__file__).parent.parent
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"
TEMPLATES_DIR = ROOT_DIR / "vision" / "templates"
LOG_DIR = DATA_DIR / "logs"

# Window settings
GAME_WINDOW_TITLE = "Albion Online"  # Window title to find
WINDOW_SEARCH_TIMEOUT = 10  # Seconds to wait for window

# Timing settings (in seconds)
CLICK_DELAY_MIN = 0.1
CLICK_DELAY_MAX = 0.3
ACTION_DELAY_MIN = 0.5
ACTION_DELAY_MAX = 1.5
ISLAND_TRAVEL_DELAY = 3.0  # Wait after teleport

# Mouse humanization
MOUSE_SPEED_MIN = 0.5  # Movement duration range
MOUSE_SPEED_MAX = 1.5
CLICK_OFFSET_MAX = 3  # Pixel randomization on clicks
DOUBLE_CLICK_CHANCE = 0.02  # 2% chance to "miss" and re-click

# Vision settings
TEMPLATE_MATCH_THRESHOLD = 0.8  # Confidence for template matching
CROP_READY_COLOR = (120, 255, 0)  # HSV range for ready crops
SCREEN_CAPTURE_INTERVAL = 0.1  # How often to check screen

# Hotkeys
EMERGENCY_STOP_KEY = "f8"  # Press to emergency stop
PAUSE_RESUME_KEY = "f9"  # Toggle pause

# Debug
DEBUG_MODE = True  # Show visual overlay
SAVE_SCREENSHOTS = False  # Save captures for debugging

# Health monitoring
HEALTH_CHECK_ENABLED = True
HEALTH_CHECK_INTERVAL = 30  # Seconds between checks
MEMORY_THRESHOLD_MB = 500  # Warning if memory exceeds