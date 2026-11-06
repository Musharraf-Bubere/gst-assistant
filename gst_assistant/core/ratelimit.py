"""A small in-memory request limiter."""
import threading
import time
from collections import deque


class RateLimiter:
    """Allow at most `limit` requests in any window of `window` seconds."""

    def __init__(self, limit, window):
        self.limit = limit
        self.window = window
        self.times = deque()
        self.lock = threading.Lock()

    def allow(self):
        now = time.monotonic()
        with self.lock:
            while self.times and now - self.times[0] > self.window:
                self.times.popleft()
            if len(self.times) >= self.limit:
                return False
            self.times.append(now)
            return True
