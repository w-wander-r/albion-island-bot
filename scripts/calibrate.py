"""
Interactive calibration tool.

Run with Albion open, windowed, at 1280x720 (the resolution all our
templates are calibrated against):

    python scripts/calibrate.py

A window will open showing the current screenshot. Click points in this
order:
    1-12 : garden plots, in the order you want the bot to visit them
    13   : bank chest
    14   : yard (product pickup / seed drop-off spot)

Controls:
    u        undo last point
    q / ESC  finish and save

Coordinates are saved as offsets relative to the game window's anchor
icon, NOT raw screen coordinates -- so this calibration stays valid even
if the window moves to a different position on your desktop next time,
as long as the resolution stays 1280x720.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cv2

from albion_bot.platform.capture import get_capture_backend
from albion_bot.vision.window_locator import WindowLocator

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "config" / "islands.json"
WINDOW_NAME = "Calibration - click points, u=undo, q=finish"

POINT_LABELS = [f"plot_{i + 1}" for i in range(9)] + ["bank", "yard"]

clicks: list[tuple[int, int]] = []


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        clicks.append((x, y))
        label = POINT_LABELS[len(clicks) - 1] if len(clicks) <= len(POINT_LABELS) else "extra"
        print(f"Point {len(clicks)} [{label}]: ({x}, {y})")


def main():
    print("Capturing screenshot and locating game window...")
    backend = get_capture_backend()
    locator = WindowLocator()

    screenshot = backend.capture()
    origin = locator.locate(screenshot)
    if origin is None:
        print("Could not locate the game window (anchor icon not found).")
        print("Make sure Albion is open, visible, and running at 1280x720.")
        return
    print(f"Window origin: ({origin.x}, {origin.y}), match score {origin.score:.4f}")

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(WINDOW_NAME, on_mouse)

    while True:
        frame = screenshot.copy()
        for i, (x, y) in enumerate(clicks):
            cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
            label = POINT_LABELS[i] if i < len(POINT_LABELS) else str(i + 1)
            cv2.putText(frame, label, (x + 8, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        next_label = POINT_LABELS[len(clicks)] if len(clicks) < len(POINT_LABELS) else "(extra)"
        cv2.putText(frame, f"Next: {next_label}   (u=undo, q=finish)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow(WINDOW_NAME, frame)

        key = cv2.waitKey(20) & 0xFF
        if key == ord('u') and clicks:
            clicks.pop()
        elif key == ord('q') or key == 27:
            break

    cv2.destroyAllWindows()

    result = {}
    for i, (x, y) in enumerate(clicks):
        label = POINT_LABELS[i] if i < len(POINT_LABELS) else f"extra_{i}"
        result[label] = {"rel_x": int(x - origin.x), "rel_y": int(y - origin.y)}

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Saved {len(result)} points to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
