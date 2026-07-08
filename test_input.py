#!/usr/bin/env python3
"""Test input backends on Linux"""
import platform
import os

print(f"Platform: {platform.system()}")
print(f"Display: {os.environ.get('DISPLAY', 'Not set')}")
print(f"Session type: {os.environ.get('XDG_SESSION_TYPE', 'Unknown')}")

# Try different backends
print("\nTesting mouse backends:")

# Test 1: python-xlib
try:
    from Xlib.display import Display
    print("✓ python-xlib available")
except ImportError:
    print("✗ python-xlib not available")

# Test 2: pynput
try:
    from pynput.mouse import Controller
    print("✓ pynput mouse available")
except ImportError as e:
    print(f"✗ pynput mouse failed: {e}")

# Test 3: evdev
try:
    from evdev import UInput
    print("✓ evdev available")
except ImportError:
    print("✗ evdev not available")

# Test 4: pyautogui as alternative
try:
    import pyautogui
    print("✓ pyautogui available (alternative)")
except ImportError:
    print("✗ pyautogui not available")