"""
Picks the correct screen capture backend based on platform + session type.

Usage:
    from albion_bot.platform.capture import get_capture_backend
    backend = get_capture_backend()
    img = backend.capture()   # OpenCV BGR numpy array
"""
import os
import platform


def get_capture_backend():
    system = platform.system()

    if system == "Windows":
        from .capture_backends.windows_capture import WindowsCapture
        return WindowsCapture()

    if system == "Linux":
        session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
        if session_type == "wayland":
            from .capture_backends.wayland_capture import WaylandPortalCapture
            return WaylandPortalCapture()
        else:
            from .capture_backends.x11_capture import X11Capture
            return X11Capture()

    raise RuntimeError(f"Unsupported platform: {system}")
