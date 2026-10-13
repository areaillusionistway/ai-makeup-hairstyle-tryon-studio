"""Rolling FPS / latency meter used by the status bar."""
from __future__ import annotations

import time
from collections import deque


class RollingTimer:
    def __init__(self, window: int = 30) -> None:
        self._samples: deque[float] = deque(maxlen=window)

    def tick(self) -> None:
        self._samples.append(time.perf_counter())

    def fps(self) -> float:
        if len(self._samples) < 2:
            return 0.0
        span = self._samples[-1] - self._samples[0]
        return (len(self._samples) - 1) / span if span > 0 else 0.0