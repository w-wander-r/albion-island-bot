import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from albion_bot.platform.capture import get_capture_backend
from albion_bot.vision.window_locator import WindowLocator


def main():
    backend = get_capture_backend()
    locator = WindowLocator()

    screenshot = backend.capture()
    windows = locator.locate_all(screenshot, max_windows=4)

    if not windows:
        print("No game window found.")
        return

    print(f"Found {len(windows)} window(s):")
    for w in windows:
        print(f"  origin=({w.x}, {w.y}) score={w.score:.4f}")


if __name__ == "__main__":
    main()
