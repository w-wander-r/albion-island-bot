"""
Generic "wait until this becomes true" helper, used throughout the bot loop
instead of guessing fixed sleep durations. Since character travel time to a
clicked point varies (distance-dependent) and we can't know it in advance,
we poll the actual game state instead -- e.g. "wait until the plot popup
appears" rather than "sleep 3 seconds and hope we arrived."
"""
import time
from typing import Callable


def wait_until(condition_fn: Callable[[], bool], timeout: float = 10.0,
                poll_interval: float = 0.3) -> bool:
    """
    condition_fn: zero-arg callable that captures/checks game state itself
                  and returns True once the awaited condition is met.
    Returns True if the condition became true within timeout, False if it
    timed out (caller should decide how to handle a timeout -- retry,
    skip this plot, log and raise, etc.)
    """
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        if condition_fn():
            return True
        time.sleep(poll_interval)
    return False
