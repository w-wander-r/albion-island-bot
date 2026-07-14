"""
Thin, reusable wrapper around cv2.matchTemplate.

We only use this for 2D UI elements (popups, panels, buttons, inventory
slots) -- NOT for anything rendered in the 3D world. Testing showed 3D-world
icons vary too much in scale/lighting/occlusion for template matching to be
reliable, while UI elements are pixel-stable across sessions.
"""
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class MatchResult:
    found: bool
    score: float
    x: int
    y: int
    w: int
    h: int

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)


class TemplateMatcher:
    def __init__(self, template_path: str, threshold: float = 0.90):
        self.template = cv2.imread(template_path)
        if self.template is None:
            raise FileNotFoundError(f"Could not load template: {template_path}")
        self.h, self.w = self.template.shape[:2]
        self.threshold = threshold
        self._template_gray = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)

    def find(self, screenshot: np.ndarray, threshold: float | None = None) -> MatchResult:
        threshold = threshold if threshold is not None else self.threshold
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(screenshot_gray, self._template_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        x, y = max_loc
        return MatchResult(
            found=max_val >= threshold,
            score=max_val,
            x=x, y=y, w=self.w, h=self.h,
        )
