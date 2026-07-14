"""
Detects the various fixed 2D UI panels the bot needs to react to: the plot
info popup (growing/ready), the seed placement popup, and the placement-mode
banner. All matched the same way -- template matching against a stable UI
element that's always at the same appearance/position regardless of which
plot/seed triggered it.
"""
from pathlib import Path

from .matcher import MatchResult, TemplateMatcher

_ASSETS_DIR = Path(__file__).resolve().parents[3] / "assets" / "templates" / "ui"


class PopupDetector:
    def __init__(self):
        self._close_button = TemplateMatcher(str(_ASSETS_DIR / "popup_close_button.png"), threshold=0.90)
        self._take_button = TemplateMatcher(str(_ASSETS_DIR / "take_button.png"), threshold=0.90)
        self._place_button = TemplateMatcher(str(_ASSETS_DIR / "place_button.png"), threshold=0.90)
        self._cancel_button = TemplateMatcher(str(_ASSETS_DIR / "placement_cancel_button.png"), threshold=0.90)

    def find_close_button(self, screenshot) -> MatchResult:
        return self._close_button.find(screenshot)

    def find_take_button(self, screenshot) -> MatchResult:
        return self._take_button.find(screenshot)

    def find_place_button(self, screenshot) -> MatchResult:
        return self._place_button.find(screenshot)

    def find_cancel_button(self, screenshot) -> MatchResult:
        return self._cancel_button.find(screenshot)

    def is_popup_open(self, screenshot) -> bool:
        """Any plot info popup (growing or ready) is showing."""
        return self.find_close_button(screenshot).found

    def is_ready_to_harvest(self, screenshot) -> bool:
        return self.find_take_button(screenshot).found

    def is_seed_info_open(self, screenshot) -> bool:
        return self.find_place_button(screenshot).found

    def is_in_placement_mode(self, screenshot) -> bool:
        return self.find_cancel_button(screenshot).found
