"""
Interactive template extraction tool.

Run with the relevant game UI already open/visible:

    python scripts/extract_template.py place_button_v2.png

Click the TOP-LEFT corner of the element you want, then its BOTTOM-RIGHT
corner. A green box previews the region; it auto-saves shortly after the
second click. Press 'r' to reset your two points if you misclick, or
'q'/ESC to cancel without saving.
"""
import sys
from pathlib import Path
from time import sleep, time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cv2

from albion_bot.platform.capture import get_capture_backend
from albion_bot.vision.window_locator import WindowLocator

if len(sys.argv) < 2:
    print("Usage: python extract_template.py <output_filename.png>")
    sys.exit(1)

output_path = Path(sys.argv[1])
points: list[tuple[int, int]] = []


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(points) < 2:
        points.append((x, y))


def main():
    sleep(1)  # give the user a moment to switch to the game window
    backend = get_capture_backend()
    screenshot = backend.capture()

    win = "Click TOP-LEFT then BOTTOM-RIGHT of the element (r=reset, q=cancel)"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(win, on_mouse)

    while True:
        frame = screenshot.copy()
        for p in points:
            cv2.circle(frame, p, 4, (0, 0, 255), -1)
        if len(points) == 2:
            cv2.rectangle(frame, points[0], points[1], (0, 255, 0), 2)

        cv2.imshow(win, frame)
        key = cv2.waitKey(20) & 0xFF

        if key == ord('r'):
            points.clear()
        elif key == ord('q') or key == 27:
            print("Cancelled, nothing saved.")
            cv2.destroyAllWindows()
            return
        elif len(points) == 2:
            cv2.waitKey(400)  # brief pause so you can see the final box
            break

    cv2.destroyAllWindows()

    (x1, y1), (x2, y2) = points
    x1, x2 = sorted((x1, x2))
    y1, y2 = sorted((y1, y2))
    crop = screenshot[y1:y2, x1:x2]

    if crop.size == 0:
        print("Empty crop -- your two points were identical or invalid. Try again.")
        return

    cv2.imwrite(str(output_path), crop)
    print(f"Saved {crop.shape[1]}x{crop.shape[0]} crop to {output_path}")
    print(f"Absolute screenshot coords: top-left=({x1},{y1}) bottom-right=({x2},{y2})")

    locator = WindowLocator()
    origin = locator.locate(screenshot)
    if origin:
        print(f"Window origin: ({origin.x}, {origin.y})")
        print(f"Offset from window origin: top-left=({x1 - origin.x},{y1 - origin.y}) "
              f"bottom-right=({x2 - origin.x},{y2 - origin.y})")
    else:
        print("(Could not locate window origin to compute a relative offset)")


if __name__ == "__main__":
    main()
