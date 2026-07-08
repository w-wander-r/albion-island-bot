"""
Logging configuration with rotation and formatting.
"""
from loguru import logger
from pathlib import Path
import sys
from config.settings import LOG_DIR, DEBUG_MODE

def setup_logger():
    """Configure the logger with file and console output."""
    
    # Create log directory
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Remove default handler
    logger.remove()
    
    # Console handler
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="DEBUG" if DEBUG_MODE else "INFO"
    )
    
    # File handler with rotation
    logger.add(
        LOG_DIR / "bot_{time:YYYY-MM-DD}.log",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )
    
    return logger

# Create global logger instance
log = setup_logger()