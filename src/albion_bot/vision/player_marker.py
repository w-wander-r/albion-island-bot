"""
Detects the player position arrow on the island map (opened with 'N') via
color-based blob detection rather than template matching.

Why color, not template matching: the arrow rotates continuously to show
facing direction, and a fixed template doesn't match well across arbitrary
rotation angles (same class of problem as the 3D-world icons that failed
earlier -- template matching wants a stable appearance, not variable one).
Since we only need the arrow's POSITION (not which way it's pointing --
the compass ring is fixed north-up, so we can compute bearings from map
coordinates alone), color segmentation sidesteps the rotation problem
entirely.

Calibrated signature (from a sample crop): yellow/orange, HSV hue ~39,
high saturation ~180+. Distinct from the map's blue water and green/tan
terrain.
"""
import cv2
import numpy as np

# Loose-ish bounds around the sampled hue/saturation; tune based on real
# in-game testing across different map zoom/lighting if needed.
LOWER_HSV = np.array([25, 120, 100])
UPPER_HSV = np.array([50, 255, 255])

MIN_BLOB_AREA = 5  # arrow is small; filter out single-pixel noise


class PlayerMarkerDetector:
    def find(self, map_screenshot) -> tuple[int, int] | None:
        """Returns (x, y) centroid of the player marker in the given map
        screenshot, or None if not found."""
        hsv = cv2.cvtColor(map_screenshot, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LOWER_HSV, UPPER_HSV)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) < MIN_BLOB_AREA:
            return None

        M = cv2.moments(largest)
        if M["m00"] == 0:
            return None

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        return cx, cy