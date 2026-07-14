"""
Run with the island map open ('N' key):

    python scripts/test_player_marker.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cv2

from albion_bot.game.window import GameWindow
from albion_bot.vision.player_marker import PlayerMarkerDetector


def main():
    window = GameWindow()
    screenshot = window.refresh()

    detector = PlayerMarkerDetector()
    pos = detector.find(screenshot)

    if pos is None:
        print("Player marker NOT found")
        return

    print(f"Player marker at: {pos}")

    out = screenshot.copy()
    cv2.circle(out, pos, 8, (0, 0, 255), 2)
    cv2.imwrite("player_marker_result.png", out)
    print("Saved player_marker_result.png")


if __name__ == "__main__":
    main()