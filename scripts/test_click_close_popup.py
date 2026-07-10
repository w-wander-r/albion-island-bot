"""
Combined capture+input smoke test.

Run this while a plot popup is open on screen (same setup as before).
It will:
  1. Capture the screen and locate the popup close button via template match
  2. Click it using the input backend
  3. Re-capture and confirm the popup is now gone

This proves the full loop end-to-end: see something -> act on it -> verify
the action worked.

Run from the project root:
    python scripts/test_click_close_popup.py
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from albion_bot.platform.capture import get_capture_backend
from albion_bot.input.controller import get_input_backend
from albion_bot.vision.detector import PopupDetector


def main():
    time.sleep(1)  # give user a moment to alt-tab to game window
    capture = get_capture_backend()
    input_ctl = get_input_backend()
    detector = PopupDetector()

    print("Step 1: capturing screen, checking popup is open...")
    screenshot = capture.capture()
    match = detector.find_close_button(screenshot)
    print(f"  Popup open: {match.found} (score {match.score:.4f})")

    if not match.found:
        print("Popup not detected -- open a plot popup in-game and re-run.")
        return

    cx, cy = match.center
    print(f"Step 2: clicking close button at ({cx}, {cy})...")
    input_ctl.click(cx, cy)

    time.sleep(0.5)  # let the UI animation/close settle

    print("Step 3: re-capturing to confirm popup closed...")
    screenshot2 = capture.capture()
    match2 = detector.find_close_button(screenshot2)
    print(f"  Popup open now: {match2.found} (score {match2.score:.4f})")

    if not match2.found:
        print("SUCCESS: popup closed after click.")
    else:
        print("Popup still detected -- click may not have landed correctly.")


if __name__ == "__main__":
    main()
