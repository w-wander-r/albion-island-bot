"""
Screen capture backend for GNOME/Wayland using the xdg-desktop-portal
Screenshot interface.

Note: this backend takes a fresh single screenshot per call (with a brief
screen flash each time) -- it is NOT a live/continuous capture. That's fine
for our click -> capture -> verify state loop, but too slow for anything
needing many frames per second. If we ever need continuous capture, the
correct upgrade path is the ScreenCast portal (PipeWire-based, supports a
persistent restore_token so consent is only granted once).
"""
import asyncio
import os
from urllib.parse import unquote, urlparse

import cv2
import numpy as np
from dbus_next.aio import MessageBus
from dbus_next import Variant

# Minimal hand-written introspection XML for just the interfaces we need.
# We deliberately avoid calling bus.introspect() on the portal root object:
# GNOME exposes a property named "power-saver-enabled" (hyphenated) on one
# of its interfaces, which crashes dbus-next's stricter name validator during
# full introspection. Skipping auto-introspection sidesteps that bug.
_SCREENSHOT_XML = """
<node>
  <interface name="org.freedesktop.portal.Screenshot">
    <method name="Screenshot">
      <arg type="s" name="parent_window" direction="in"/>
      <arg type="a{sv}" name="options" direction="in"/>
      <arg type="o" name="handle" direction="out"/>
    </method>
  </interface>
</node>
"""

_REQUEST_XML = """
<node>
  <interface name="org.freedesktop.portal.Request">
    <method name="Close"/>
    <signal name="Response">
      <arg type="u" name="response"/>
      <arg type="a{sv}" name="results"/>
    </signal>
  </interface>
</node>
"""


class WaylandPortalCapture:
    """Captures the screen via xdg-desktop-portal and returns an OpenCV
    (BGR numpy array) image, matching what cv2.imread would give us."""

    def __init__(self, cleanup_files: bool = True):
        self.cleanup_files = cleanup_files

    def capture(self) -> np.ndarray:
        path = asyncio.run(self._request_screenshot())
        img = cv2.imread(path)
        if img is None:
            raise RuntimeError(f"Portal reported success but image failed to load: {path}")
        if self.cleanup_files:
            try:
                os.remove(path)
            except OSError:
                pass
        return img

    async def _request_screenshot(self, timeout: int = 30) -> str:
        bus = await MessageBus().connect()

        proxy = bus.get_proxy_object(
            "org.freedesktop.portal.Desktop", "/org/freedesktop/portal/desktop", _SCREENSHOT_XML
        )
        screenshot_iface = proxy.get_interface("org.freedesktop.portal.Screenshot")

        request_path = await screenshot_iface.call_screenshot(
            "", {"interactive": Variant("b", False)}
        )

        request_obj = bus.get_proxy_object(
            "org.freedesktop.portal.Desktop", request_path, _REQUEST_XML
        )
        request_iface = request_obj.get_interface("org.freedesktop.portal.Request")

        done = asyncio.Event()
        outcome = {}

        def on_response(response_code, results):
            outcome["code"] = response_code
            outcome["results"] = results
            done.set()

        request_iface.on_response(on_response)

        try:
            await asyncio.wait_for(done.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError("Timed out waiting for portal screenshot response")

        if outcome["code"] != 0:
            raise RuntimeError(f"Portal screenshot failed with response code {outcome['code']}")

        uri = outcome["results"]["uri"].value
        return unquote(urlparse(uri).path)
