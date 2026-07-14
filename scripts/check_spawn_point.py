"""
Run this the moment you arrive on your island via Travel Planner, before
moving the character or touching the camera:

    python scripts/check_spawn_position.py

This just captures + locates the window and saves the raw screenshot, plus
a version with our calibrated plot/bank points overlaid, so we can see by
eye whether they land on the right spots straight off teleport.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cv2

from albion_bot.game.window import GameWindow

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "islands.json"


def main():
    window = GameWindow()
    screenshot = window.refresh()
    origin = window.origin
    print(f"Window origin: ({origin.x}, {origin.y}), score {origin.score:.4f}")

    cv2.imwrite("spawn_raw.png", screenshot)

    with open(CONFIG_PATH) as f:
        points = json.load(f)

    out = screenshot.copy()
    for name, p in points.items():
        x = origin.x + p["rel_x"]
        y = origin.y + p["rel_y"]
        cv2.circle(out, (x, y), 6, (0, 0, 255), -1)
        cv2.putText(out, name, (x + 8, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    cv2.imwrite("spawn_calibration_overlay.png", out)
    print("Saved spawn_raw.png and spawn_calibration_overlay.png")
    print("Check: do the red dots land on the right plots/bank without any movement?")


if __name__ == "__main__":
    main()