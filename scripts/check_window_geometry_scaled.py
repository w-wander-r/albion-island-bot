"""
Run from your project root:

    python check_window_geometry_scaled.py

Computes the display scale factor dynamically (physical resolution from
mss's monitor query, vs logical resolution from our portal screenshot),
applies it to the xdotool/wmctrl window geometry, and overlays the
corrected box so we can visually confirm it now lines up.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cv2
import mss
from albion_bot.platform.capture import get_capture_backend

# Raw (uncorrected) geometry from xdotool getwindowgeometry
RAW_X, RAW_Y, RAW_W, RAW_H = 1640, 776, 1380, 894

backend = get_capture_backend()
screenshot = backend.capture()
screenshot_w = screenshot.shape[1]
screenshot_h = screenshot.shape[0]
print(f"Portal screenshot (logical) size: {screenshot_w}x{screenshot_h}")

with mss.mss() as sct:
    monitor = sct.monitors[1]
    physical_w = monitor["width"]
    physical_h = monitor["height"]
print(f"mss reported physical size: {physical_w}x{physical_h}")

scale_x = physical_w / screenshot_w
scale_y = physical_h / screenshot_h
print(f"Computed scale factor: {scale_x:.3f} (x), {scale_y:.3f} (y)")

x = int(RAW_X / scale_x)
y = int(RAW_Y / scale_y)
w = int(RAW_W / scale_x)
h = int(RAW_H / scale_y)
print(f"Corrected window box (logical coords): x={x}, y={y}, w={w}, h={h}")

out = screenshot.copy()
cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 3)
cv2.putText(out, "scaled", (x, max(y - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
cv2.imwrite("window_geometry_scaled.png", out)
print("Saved window_geometry_scaled.png -- check if the box now lines up correctly.")