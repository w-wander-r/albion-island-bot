"""
End-to-end smoke test: capture the live screen and check whether the plot
info popup is open. Run this while Albion is open with a plot popup showing
(same as your test screenshots).

Run from the project root:
    python scripts/test_popup_detection.py
"""
import sys
from pathlib import Path

# Allow running this script directly without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cv2

from albion_bot.platform.capture import get_capture_backend
from albion_bot.vision.detector import PopupDetector


def main():
    print("Capturing live screenshot...")
    backend = get_capture_backend()
    screenshot = backend.capture()
    print(f"Captured {screenshot.shape[1]}x{screenshot.shape[0]}")

    detector = PopupDetector()
    match = detector.find_close_button(screenshot)

    print(f"Popup open: {match.found}")
    print(f"Match score: {match.score:.4f}")
    print(f"Close button location: ({match.x}, {match.y}), center: {match.center}")

    out = screenshot.copy()
    color = (0, 255, 0) if match.found else (0, 0, 255)
    cv2.rectangle(out, (match.x, match.y), (match.x + match.w, match.y + match.h), color, 3)
    out_path = "popup_detection_result.png"
    cv2.imwrite(out_path, out)
    print(f"Annotated result saved to {out_path}")


if __name__ == "__main__":
    main()
