"""
Run on Arch with Albion open (windowed mode is fine, that's what we're
testing):

    sudo pacman -S wmctrl   # if not already installed
    python check_window_targeting.py

We're checking whether window listing/geometry tools can see the Albion
window at all. This depends on whether it renders as an XWayland surface
(visible to X11 tools like xdotool/wmctrl) or a native Wayland surface
(much harder to query under GNOME's security model, no public API for
arbitrary window geometry).
"""
import subprocess
import shutil


def check_tool(name):
    path = shutil.which(name)
    print(f"{name:10s}: {'FOUND -> ' + path if path else 'not found'}")


def try_wmctrl():
    print("\n=== wmctrl -l (list all windows) ===")
    if not shutil.which("wmctrl"):
        print("wmctrl not installed")
        return
    result = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True)
    print(result.stdout or "(no output)")
    if result.stderr:
        print("stderr:", result.stderr)


def try_wmctrl_geometry():
    print("\n=== wmctrl -lG (list windows with geometry) ===")
    if not shutil.which("wmctrl"):
        return
    result = subprocess.run(["wmctrl", "-lG"], capture_output=True, text=True)
    print(result.stdout or "(no output)")


def try_xdotool():
    print("\n=== xdotool search --name Albion ===")
    if not shutil.which("xdotool"):
        print("xdotool not installed")
        return
    result = subprocess.run(
        ["xdotool", "search", "--name", "Albion"],
        capture_output=True, text=True
    )
    print("stdout:", result.stdout or "(no output)")
    print("stderr:", result.stderr or "(none)")

    window_ids = result.stdout.strip().split("\n") if result.stdout.strip() else []
    for wid in window_ids:
        geo = subprocess.run(
            ["xdotool", "getwindowgeometry", "--shell", wid],
            capture_output=True, text=True
        )
        print(f"\nWindow {wid} geometry:")
        print(geo.stdout)


if __name__ == "__main__":
    print("=== Tool availability ===")
    for t in ["wmctrl", "xdotool"]:
        check_tool(t)

    try_wmctrl()
    try_wmctrl_geometry()
    try_xdotool()

    print("\nPlease share the full output, especially whether any Albion")
    print("window shows up with a name, position (x,y) and size (WxH).")