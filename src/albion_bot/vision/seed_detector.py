"""
Detects which seed type(s) are visible (e.g. in an inventory slot) by
matching against every seed_*.png template in assets/templates/plots/.

Add a new seed type by dropping in a new seed_<name>.png file -- no code
changes needed here. Extract one with:

    python scripts/extract_template.py assets/templates/plots/seed_<name>.png
"""
from pathlib import Path

from .matcher import MatchResult, TemplateMatcher

_ASSETS_DIR = Path(__file__).resolve().parents[3] / "assets" / "templates" / "plots"


class SeedDetector:
    def __init__(self, threshold: float = 0.90):
        self.matchers: dict[str, TemplateMatcher] = {}
        for path in sorted(_ASSETS_DIR.glob("seed_*.png")):
            name = path.stem.removeprefix("seed_")
            self.matchers[name] = TemplateMatcher(str(path), threshold=threshold)

        if not self.matchers:
            raise FileNotFoundError(f"No seed_*.png templates found in {_ASSETS_DIR}")

    def find_all(self, screenshot) -> dict[str, MatchResult]:
        """Match result for every known seed type, found or not."""
        return {name: matcher.find(screenshot) for name, matcher in self.matchers.items()}

    def find_present(self, screenshot) -> dict[str, MatchResult]:
        """Only the seed types actually detected on screen right now."""
        return {name: m for name, m in self.find_all(screenshot).items() if m.found}
