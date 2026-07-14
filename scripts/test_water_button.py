"""
Run with a plot popup open (Water button visible, any state):

    python scripts/test_water_button.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cv2

from albion_bot.game.window import GameWindow
from albion_bot.vision.water_button import WaterButtonDetector


def main():
    window = GameWindow()
    detector = WaterButtonDetector()

    screenshot = window.refresh()
    origin = window.origin
    print(f"Window origin: ({origin.x}, {origin.y}), score {origin.score:.4f}")

    state = detector.get_state(screenshot, origin)
    print(f"Water button state: {state}")

    target = detector.click_target(origin)
    print(f"Click target (absolute): {target}")

    out = screenshot.copy()
    cv2.circle(out, target, 6, (0, 255, 0) if state == "active" else (0, 0, 255), -1)
    cv2.imwrite("water_button_check_result.png", out)
    print("Saved water_button_check_result.png")


if __name__ == "__main__":
    main()
