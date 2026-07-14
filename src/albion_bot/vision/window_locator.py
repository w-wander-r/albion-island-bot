"""
Locates the Albion game window within a full-desktop screenshot by matching
a fixed HUD icon (the character portrait, top-left corner of the game's own
UI) rather than querying the window manager.

Why: under GNOME/Wayland, WM tools (xdotool/wmctrl) report window geometry
in a different, inconsistent pixel space than our screenshots (physical vs
logical, plus extra offset weirdness at non-zero positions), and can't be
used to move/resize windows at all (Mutter blocks that for foreign clients).
Anchor-icon matching sidesteps all of that: wherever the window is, the
portrait icon is always at the same fixed offset from its true top-left
corner, as long as the game is running at the calibrated resolution
(currently 1280x720 windowed -- see assets/templates/ui/window_anchor.png).

If you change the game's resolution, this template (and the popup template)
must be recaptured at the new resolution -- template matching is NOT
scale-invariant, confirmed during testing.
"""
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

_ASSETS_DIR = Path(__file__).resolve().parents[3] / "assets" / "templates" / "ui"

# Offset of the anchor icon's top-left corner from the window's true
# top-left corner, calibrated at 1280x720 windowed resolution. Measured
# as ~0 during testing (the crop was taken starting essentially at the
# window's real origin), but kept as an explicit constant in case future
# recalibration finds a small correction is needed.
ANCHOR_OFFSET_X = 0
ANCHOR_OFFSET_Y = 0


@dataclass
class WindowOrigin:
    x: int
    y: int
    score: float


class WindowLocator:
    def __init__(self, threshold: float = 0.90):
        template = cv2.imread(str(_ASSETS_DIR / "window_anchor.png"))
        if template is None:
            raise FileNotFoundError(f"Missing template: {_ASSETS_DIR / 'window_anchor.png'}")
        self._template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        self.h, self.w = self._template_gray.shape
        self.threshold = threshold

    def locate(self, screenshot: np.ndarray) -> WindowOrigin | None:
        """Find the single best-matching window (use when you know there's
        only one Albion window on screen)."""
        matches = self.locate_all(screenshot, max_windows=1)
        return matches[0] if matches else None

    def locate_all(self, screenshot: np.ndarray, max_windows: int = 4) -> list[WindowOrigin]:
        """Find all Albion windows on screen (for multi-instance setups)."""
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(screenshot_gray, self._template_gray, cv2.TM_CCOEFF_NORMED)

        locations = np.where(result >= self.threshold)
        candidates = [
            (x, y, result[y, x]) for y, x in zip(*locations)
        ]
        candidates.sort(key=lambda c: -c[2])

        kept: list[WindowOrigin] = []
        min_dist = max(self.w, self.h)
        for x, y, score in candidates:
            if len(kept) >= max_windows:
                break
            if all(abs(x - k.x) > min_dist or abs(y - k.y) > min_dist for k in kept):
                kept.append(WindowOrigin(
                    x=int(x - ANCHOR_OFFSET_X),
                    y=int(y - ANCHOR_OFFSET_Y),
                    score=float(score),
                ))
        return kept