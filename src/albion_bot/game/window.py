"""
Combines capture + window location + input into one object, so higher-level
actions don't need to juggle three separate backends and remember to
convert between absolute screenshot coordinates and window-relative ones.
"""
import json
from pathlib import Path

from albion_bot.platform.capture import get_capture_backend
from albion_bot.input.controller import get_input_backend
from albion_bot.vision.window_locator import WindowLocator, WindowOrigin

_ORIGIN_CACHE_PATH = Path(__file__).resolve().parents[3] / ".window_origin_cache.json"


class GameWindow:
    def __init__(self):
        self._capture = get_capture_backend()
        self._input = get_input_backend()
        self._locator = WindowLocator()
        self._screenshot = None
        self._origin = self._load_cached_origin()

    @staticmethod
    def _load_cached_origin() -> WindowOrigin | None:
        if not _ORIGIN_CACHE_PATH.exists():
            return None
        try:
            data = json.loads(_ORIGIN_CACHE_PATH.read_text())
            return WindowOrigin(x=data["x"], y=data["y"], score=data.get("score", 0.0))
        except (json.JSONDecodeError, KeyError):
            return None

    @staticmethod
    def _save_cached_origin(origin: WindowOrigin):
        _ORIGIN_CACHE_PATH.write_text(json.dumps({
            "x": int(origin.x), "y": int(origin.y), "score": float(origin.score)
        }))

    def refresh(self, allow_stale_origin: bool = True):
        """Capture a fresh screenshot and relocate the window. Returns the
        screenshot (also cached for origin/click use until next refresh).

        If the anchor icon can't be found (e.g. a full-screen overlay like
        the island map is covering the top-left portrait), we fall back to
        a previously known origin -- either from this process (in-memory)
        or a prior run (disk cache) -- since the window doesn't move once
        positioned (confirmed: Wayland doesn't allow programmatic or even
        most manual repositioning of foreign windows here).
        """
        screenshot = self._capture.capture()
        origin = self._locator.locate(screenshot)

        if origin is None:
            if allow_stale_origin and self._origin is not None:
                self._screenshot = screenshot
                return screenshot
            raise RuntimeError(
                "Game window not found -- is Albion open, visible, at 1280x720? "
                "The anchor icon must be visible on screen at least once, ever "
                "(this run or a prior one) -- e.g. close any full-screen overlay "
                "like the map first, run any capture, then reopen the overlay."
            )

        self._screenshot = screenshot
        self._origin = origin
        self._save_cached_origin(origin)
        return screenshot

    @property
    def screenshot(self):
        if self._screenshot is None:
            self.refresh()
        return self._screenshot

    @property
    def origin(self):
        if self._origin is None:
            self.refresh()
        return self._origin

    def click_absolute(self, x: int, y: int):
        """Click a raw screenshot-space coordinate (e.g. a detector's
        match.center), no offset applied."""
        self._input.click(x, y)

    def click_relative(self, rel_x: int, rel_y: int):
        """Click a point defined as an offset from the window's origin
        (e.g. calibrated plot/bank/yard coordinates from islands.json)."""
        origin = self.origin
        self.click_absolute(origin.x + rel_x, origin.y + rel_y)

    def press_key(self, name: str):
        self._input.press_key(name)