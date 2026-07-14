"""
Detects whether the plot popup's Water button is currently clickable
(red/active) or disabled (gray, already watered).

Unlike our other UI elements, this doesn't need template matching -- the
button's shape/position never changes, only its color, so we just sample
average saturation in a fixed region relative to the window origin and
threshold it. Much simpler and faster than a template match.

Calibrated at 1280x720, region relative to window origin:
    top-left     (429, 339)
    bottom-right (481, 347)

Calibrated samples (mean HSV saturation over the region):
    gray (disabled): ~4.4
    red  (active):   ~173.7
Threshold set at 50 -- comfortably between the two with plenty of margin.
"""
import cv2

OFFSET_X1, OFFSET_Y1 = 429, 339
OFFSET_X2, OFFSET_Y2 = 481, 347

SATURATION_THRESHOLD = 50.0


class WaterButtonDetector:
    def get_state(self, screenshot, origin) -> str:
        """Returns 'active' or 'disabled'."""
        x1, y1 = origin.x + OFFSET_X1, origin.y + OFFSET_Y1
        x2, y2 = origin.x + OFFSET_X2, origin.y + OFFSET_Y2
        region = screenshot[y1:y2, x1:x2]

        if region.size == 0:
            raise RuntimeError(
                "Water button region is out of screenshot bounds -- "
                "did the window move, resize, or is it partially off-screen?"
            )

        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        mean_saturation = hsv[:, :, 1].mean()
        return "active" if mean_saturation > SATURATION_THRESHOLD else "disabled"

    def is_active(self, screenshot, origin) -> bool:
        return self.get_state(screenshot, origin) == "active"

    def click_target(self, origin) -> tuple[int, int]:
        """Center of the button, in absolute screenshot coordinates."""
        cx = origin.x + (OFFSET_X1 + OFFSET_X2) // 2
        cy = origin.y + (OFFSET_Y1 + OFFSET_Y2) // 2
        return cx, cy
