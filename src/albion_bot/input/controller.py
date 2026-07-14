"""
Picks the correct input injection backend based on platform.

Usage:
    from albion_bot.input.controller import get_input_backend
    input_ctl = get_input_backend()
    input_ctl.click(500, 300)
"""
import platform


def get_input_backend():
    system = platform.system()

    if system == "Windows":
        from .backends.windows_input import WindowsInput
        return WindowsInput()

    if system == "Linux":
        from .backends.linux_input import YdotoolInput
        return YdotoolInput()

    raise RuntimeError(f"Unsupported platform: {system}")
