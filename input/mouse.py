"""
Humanized mouse movement using bezier curves.
Mimics natural human hand movement with micro-adjustments.
"""
import random
import time
import numpy as np
from bezier import Curve
from loguru import logger
from config.settings import (
    MOUSE_SPEED_MIN, MOUSE_SPEED_MAX,
    CLICK_OFFSET_MAX, DOUBLE_CLICK_CHANCE
)

class HumanizedMouse:
    """Mouse controller with human-like movement patterns."""
    
    def __init__(self):
        self.current_position = (0, 0)
        # We'll initialize the actual mouse controller later (pynput)
        self.controller = None
    
    def _generate_control_points(self, start, end):
        """
        Generate bezier curve control points with natural arc.
        Humans don't move mouse in straight lines - they curve slightly.
        """
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        
        # Add slight offset to create natural arc
        arc_offset = random.randint(-50, 50)
        control_point = (mid_x + arc_offset, mid_y + arc_offset)
        
        return [start, control_point, end]
    
    def move_to(self, x, y, humanize=True):
        """
        Move mouse to coordinates with natural movement.
        
        Args:
            x, y: Target coordinates
            humanize: Add randomness and natural curves
        """
        if humanize:
            # Add small random offset to avoid pixel-perfect positioning
            x += random.randint(-CLICK_OFFSET_MAX, CLICK_OFFSET_MAX)
            y += random.randint(-CLICK_OFFSET_MAX, CLICK_OFFSET_MAX)
        
        start = self.current_position
        end = (x, y)
        
        if not humanize:
            # Direct movement (for emergency situations)
            self._direct_move(end)
            return
        
        # Generate natural movement path
        control_points = self._generate_control_points(start, end)
        
        # Calculate movement duration
        distance = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        duration = random.uniform(MOUSE_SPEED_MIN, MOUSE_SPEED_MAX)
        
        # Execute movement with slight speed variations
        self._execute_bezier_movement(control_points, duration)
        
        self.current_position = end
        
        # Occasionally simulate micro-adjustment
        if random.random() < 0.1:  # 10% chance
            self._micro_adjustment(end)
    
    def click(self, button="left", humanize=True):
        """Execute mouse click with human-like timing."""
        if humanize and random.random() < DOUBLE_CLICK_CHANCE:
            # Simulate accidental double-click
            logger.debug("Simulating accidental double-click")
            self._execute_click(button)
            time.sleep(random.uniform(0.05, 0.1))
        
        self._execute_click(button)
        time.sleep(random.uniform(0.05, 0.15))
    
    def _micro_adjustment(self, target):
        """Tiny movement adjustment after reaching target."""
        offset_x = random.randint(-2, 2)
        offset_y = random.randint(-2, 2)
        self._direct_move((target[0] + offset_x, target[1] + offset_y))
        time.sleep(random.uniform(0.01, 0.03))
    
    def _direct_move(self, position):
        """Direct mouse movement (no humanization)."""
        # TODO: Implement with pynput
        pass
    
    def _execute_bezier_movement(self, control_points, duration):
        """Execute movement along bezier curve with variable speed."""
        # TODO: Implement bezier curve movement
        pass
    
    def _execute_click(self, button):
        """Execute mouse click."""
        # TODO: Implement with pynput
        pass