"""
Run from your project root (needs the portal capture code):

    python check_window_geometry_overlay.py

Captures the full screen and draws both candidate window rectangles
(wmctrl's and xdotool's) on it, so we can see by eye which one actually
matches the real game window content area.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cv2
from albion_bot.platform.capture import get_capture_backend

# From your check_window_targeting.py output
WMCTRL_BOX = (1690, 926, 1280, 720)   # x, y, w, h
XDOTOOL_BOX = (1590, 678, 1380, 894)  # x, y, w, h

backend = get_capture_backend()
screenshot = backend.capture()
print(f"Full screenshot size: {screenshot.shape[1]}x{screenshot.shape[0]}")

out = screenshot.copy()

x, y, w, h = WMCTRL_BOX
cv2.rectangle(out, (x, y), (x + w, y + h), (0, 0, 255), 3)   # red = wmctrl
cv2.putText(out, "wmctrl", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

x, y, w, h = XDOTOOL_BOX
cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 3)   # green = xdotool
cv2.putText(out, "xdotool", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

cv2.imwrite("window_geometry_overlay.png", out)
print("Saved window_geometry_overlay.png -- check which box (red/wmctrl or")
print("green/xdotool) actually outlines the real game window content.")