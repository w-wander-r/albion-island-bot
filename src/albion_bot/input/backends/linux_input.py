"""
Input injection backend for Linux using ydotool.

Requires:
  - ydotoold running as a background service (see project README for the
    systemd unit), listening on a known socket path.
  - YDOTOOL_SOCKET env var set to that same socket path (ydotool the CLI
    reads this to know where to connect).

We deliberately do NOT use pyautogui on Linux -- confirmed dead under
GNOME/Wayland during testing: it reports success and even reports a
"moved" cursor position, but nothing actually moves on screen. ydotool
works because it injects events at the kernel uinput level rather than
asking the compositor, which Wayland's security model otherwise blocks.
"""
import subprocess
import time

# ydotool's button codes for click(): press+release in one call.
# 0xC0 = left button down+up combined.
LEFT_CLICK = "0xC0"
RIGHT_CLICK = "0xC1"

# evdev keycodes for named keys the bot uses. Add more here as needed --
# find codes via `sudo libinput debug-events` or /usr/include/linux/input-event-codes.h
_KEYCODES = {
    "escape": 1,
    "i": 23,
}


class YdotoolInput:
    def __init__(self):
        self._check_available()

    def _check_available(self):
        result = subprocess.run(
            ["ydotool", "mousemove", "--help"],
            capture_output=True, text=True
        )
        if result.returncode != 0 and "No such file or directory" in result.stderr:
            raise RuntimeError(
                "ydotoold does not appear to be reachable. Make sure the "
                "daemon is running and YDOTOOL_SOCKET is set correctly."
            )

    def move_to(self, x: int, y: int):
        subprocess.run(["ydotool", "mousemove", "--absolute", str(x), str(y)], check=True)

    def click(self, x: int | None = None, y: int | None = None, button: str = LEFT_CLICK):
        if x is not None and y is not None:
            self.move_to(x, y)
            time.sleep(0.05)  # tiny settle delay before the click registers
        subprocess.run(["ydotool", "click", button], check=True)

    def key(self, key_sequence: str):
        """Low-level: raw ydotool key syntax, e.g. '1:1 1:0' for a
        keydown+keyup of keycode 1 (Escape)."""
        subprocess.run(["ydotool", "key", key_sequence], check=True)

    def press_key(self, name: str):
        """High-level: press a named key by its evdev keycode."""
        code = _KEYCODES.get(name.lower())
        if code is None:
            raise ValueError(f"Unknown key '{name}' -- add its evdev keycode to _KEYCODES")
        self.key(f"{code}:1 {code}:0")
