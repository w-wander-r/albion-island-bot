"""
Screen capture backend for Windows, using mss.

Not yet implemented/tested -- placeholder so the platform facade doesn't
break on import. mss works reliably on Windows (no Wayland-style
restrictions), so this should be close to a drop-in once we get there.
"""
import numpy as np


class WindowsCapture:
    def __init__(self):
        import mss
        self._mss = mss.mss()

    def capture(self) -> np.ndarray:
        monitor = self._mss.monitors[1]
        shot = self._mss.grab(monitor)
        img = np.array(shot)
        return img[:, :, :3]
