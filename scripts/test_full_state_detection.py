"""
One-shot check of everything we've built: window location, all popup
states, and any known seeds visible. Useful any time something seems off --
run it in whatever state the game is currently in and see what the bot
would "see".

    python scripts/test_full_state_detection.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from albion_bot.platform.capture import get_capture_backend
from albion_bot.vision.window_locator import WindowLocator
from albion_bot.vision.detector import PopupDetector
from albion_bot.vision.seed_detector import SeedDetector


def main():
    backend = get_capture_backend()
    locator = WindowLocator()
    popup_detector = PopupDetector()
    seed_detector = SeedDetector()

    screenshot = backend.capture()
    print(f"Captured {screenshot.shape[1]}x{screenshot.shape[0]}")

    origin = locator.locate(screenshot)
    if origin:
        print(f"Window origin: ({origin.x}, {origin.y}), score {origin.score:.4f}")
    else:
        print("Window NOT found")

    print(f"Popup open (growing/ready info): {popup_detector.is_popup_open(screenshot)}")
    print(f"Ready to harvest (Take button):  {popup_detector.is_ready_to_harvest(screenshot)}")
    print(f"Seed info open (Place button):   {popup_detector.is_seed_info_open(screenshot)}")
    print(f"In placement mode (Cancel):      {popup_detector.is_in_placement_mode(screenshot)}")

    present_seeds = seed_detector.find_present(screenshot)
    if present_seeds:
        print("Seeds visible:")
        for name, match in present_seeds.items():
            print(f"  {name}: score={match.score:.4f} at {match.center}")
    else:
        print("No known seeds visible")


if __name__ == "__main__":
    main()
