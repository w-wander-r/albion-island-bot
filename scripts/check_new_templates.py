"""
Run from your project root, with Albion at 1280x720.

Test each state as you can reproduce it live:
  - take_btn: click a ready-to-harvest pot to open the "Congratulations!" popup
  - place_btn: press I to open inventory, click a seed item
  - cancel_btn: after clicking Place on a seed, you're in placement mode
  - seed_slot: with inventory open, any time (checks the seed icon position)

    python check_new_templates.py

Put all four template PNGs in the same folder as this script.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cv2
from albion_bot.platform.capture import get_capture_backend

HERE = Path(__file__).resolve().parent

TEMPLATES = {
    "take_btn": (HERE / "take_button.png", (0, 255, 0)),
    "place_btn": (HERE / "place_button_v2.png", (255, 0, 0)),
    "cancel_btn": (HERE / "cancel_button_v2.png", (0, 165, 255)),
    "seed_slot": (HERE / "inventory_seed_slot.png", (255, 0, 255)),
}

backend = get_capture_backend()
screenshot = backend.capture()
print(f"Captured {screenshot.shape[1]}x{screenshot.shape[0]}")
screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

out = screenshot.copy()

for name, (path, color) in TEMPLATES.items():
    template = cv2.imread(str(path))
    if template is None:
        print(f"[{name}] Could not load {path}")
        continue
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    h, w = template_gray.shape
    print(f"[{name}] score={max_val:.4f} at {max_loc}")
    cv2.rectangle(out, max_loc, (max_loc[0] + w, max_loc[1] + h), color, 2)
    cv2.putText(out, name, (max_loc[0], max(max_loc[1] - 8, 15)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

cv2.imwrite("new_templates_result.png", out)
print("Saved new_templates_result.png")