"""
Input injection backend for Windows, using pyautogui.

Not yet implemented/tested -- placeholder so the facade doesn't break on
import. Windows has none of the Wayland-style synthetic-input restrictions,
so pyautogui should just work here (this is exactly the case it's designed
for) -- but we'll confirm once we're actually testing on Windows.
"""


class WindowsInput:
    def __init__(self):
        import pyautogui
        self._pyautogui = pyautogui

    def move_to(self, x: int, y: int):
        self._pyautogui.moveTo(x, y)

    def click(self, x: int | None = None, y: int | None = None, button: str = "left"):
        if x is not None and y is not None:
            self._pyautogui.click(x, y, button=button)
        else:
            self._pyautogui.click(button=button)

    def key(self, key_name: str):
        self._pyautogui.press(key_name)

    def press_key(self, name: str):
        """High-level: same named keys as the Linux backend use
        ('escape', 'i'), mapped to pyautogui's own key names."""
        mapping = {"escape": "esc", "i": "i"}
        key_name = mapping.get(name.lower(), name.lower())
        self._pyautogui.press(key_name)
