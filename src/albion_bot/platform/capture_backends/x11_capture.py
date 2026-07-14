"""
Screen capture backend for X11 sessions, using mss.

Not yet tested -- we validated the Wayland/GNOME path first since that's
the primary dev environment. mss works natively against real X11 (unlike
XWayland, where it fails -- see WaylandPortalCapture's docstring).
"""
import numpy as np


class X11Capture:
    def __init__(self):
        import mss
        self._mss = mss.mss()

    def capture(self) -> np.ndarray:
        monitor = self._mss.monitors[1]  # primary monitor
        shot = self._mss.grab(monitor)
        img = np.array(shot)  # BGRA
        return img[:, :, :3]  # drop alpha, keep BGR order for OpenCV
