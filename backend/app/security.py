from __future__ import annotations

import secrets
import time
from collections import defaultdict, deque
from threading import Lock


class CsrfManager:
    def __init__(self, ttl_seconds: int = 600) -> None:
        self.ttl_seconds = ttl_seconds
        self._tokens: dict[str, float] = {}
        self._lock = Lock()

    def issue(self) -> tuple[str, int]:
        token = secrets.token_urlsafe(32)
        expires = time.time() + self.ttl_seconds
        with self._lock:
            self._tokens[token] = expires
        return token, self.ttl_seconds

    def validate(self, token: str) -> bool:
        now = time.time()
        with self._lock:
            expires = self._tokens.get(token)
            if not expires:
                return False
            if expires < now:
                self._tokens.pop(token, None)
                return False
            return True


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> tuple[bool, int]:
        now = time.time()
        with self._lock:
            q = self._hits[key]
            while q and q[0] <= now - self.window_seconds:
                q.popleft()

            if len(q) >= self.max_requests:
                retry_after = int((q[0] + self.window_seconds) - now) + 1
                return False, max(retry_after, 1)

            q.append(now)
            remaining = self.max_requests - len(q)
            return True, remaining
