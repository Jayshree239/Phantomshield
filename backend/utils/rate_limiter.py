# d:/SPECTER/phantomshield/backend/utils/rate_limiter.py
import time
from collections import defaultdict


class InMemoryRateLimiter:
    """Fallback limiter used when Redis is unavailable."""

    def __init__(self):
        self._requests = defaultdict(list)

    def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.time()
        window_start = now - window_seconds
        self._requests[key] = [ts for ts in self._requests[key] if ts >= window_start]
        if len(self._requests[key]) >= limit:
            return False
        self._requests[key].append(now)
        return True
