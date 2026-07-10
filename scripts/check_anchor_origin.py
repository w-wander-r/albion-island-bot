"""
Run from your project root, with Albion open in windowed mode:

    python check_anchor_origin.py

Instead of asking the window manager where the game window is (blocked/
unreliable under Wayland, as we just confirmed), we template-match a fixed
in-game HUD icon (the character portrait frame, always at the same offset
from the window's own top-left corner). Its detected position tells us the
window's effective origin directly in screenshot coordinate space --
no WM queries, no scale-factor math needed.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cv2
from albion_bot.platform.capture import get_capture_backend

# Where the anchor icon sits relative to the window's true top-left corner,
# calibrated from the original fullscreen reference screenshot.
ANCHOR_OFFSET_X, ANCHOR_OFFSET_Y = 5, 5

backend = get_capture_backend()
screenshot = backend.capture()
print(f"Captured {screenshot.shape[1]}x{screenshot.shape[0]}")

template = cv2.imread("anchor_template.png")
screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
_, max_val, _, max_loc = cv2.minMaxLoc(result)

print(f"Anchor match score: {max_val:.4f} at {max_loc}")

window_origin_x = max_loc[0] - ANCHOR_OFFSET_X
window_origin_y = max_loc[1] - ANCHOR_OFFSET_Y
print(f"Inferred window origin (screenshot space): ({window_origin_x}, {window_origin_y})")

out = screenshot.copy()
h, w = template_gray.shape
cv2.rectangle(out, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 255, 0), 3)
cv2.circle(out, (window_origin_x, window_origin_y), 6, (0, 0, 255), -1)
cv2.imwrite("anchor_origin_result.png", out)
print("Saved anchor_origin_result.png -- green box = matched icon, red dot = inferred window origin")