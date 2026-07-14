"""
High-level actions composed from GameWindow + detectors + calibrated points.
"""
import time

from albion_bot.game.config import Point
from albion_bot.vision.detector import PopupDetector

# Fixed settle delay between placement clicks. Per-plot arrival/placement
# doesn't have an obvious visual "done" signal to poll for (unlike popups
# opening), so we use a flat delay here instead of wait_until(). 2s was
# specified as a safe starting point -- tune down later once we've seen
# it run reliably.
PLACEMENT_SETTLE_DELAY = 2.0


def place_seeds_on_yard(window, yard_zone_points: list[Point], popup_detector: PopupDetector = None):
    """
    yard_zone_points: the plot_1..plot_9 points from islands.json -- these
    ARE the 9 yard zones (not a separate location), each an independent
    spot that grows/holds one seed.

    Preconditions (caller's responsibility):
      - Inventory is open
      - A seed's info popup is showing (Place button visible)
      - There are enough seeds in the stack for len(yard_points) plots

    Flow:
      1. Click "Place" to enter placement mode
      2. Click each yard point in turn, waiting a fixed settle delay
         between clicks
      3. Press Escape to exit placement mode (this also closes inventory,
         which is fine -- simpler than moving the mouse to a close button)
    """
    popup_detector = popup_detector or PopupDetector()

    screenshot = window.refresh()
    place_match = popup_detector.find_place_button(screenshot)
    if not place_match.found:
        raise RuntimeError("Place button not detected -- is the seed info popup open?")

    window.click_absolute(*place_match.center)
    time.sleep(PLACEMENT_SETTLE_DELAY)

    for point in yard_zone_points:
        window.click_relative(point.rel_x, point.rel_y)
        time.sleep(PLACEMENT_SETTLE_DELAY)

    window.press_key("escape")
