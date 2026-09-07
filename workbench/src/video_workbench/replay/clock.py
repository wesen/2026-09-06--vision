"""Source/run mapping; deadlines use wall time independently of replay speed."""
import math
import time


class ReplayClock:
    def __init__(self, speed=1.0, *, monotonic=time.monotonic):
        if not math.isfinite(speed) or not 0 < speed <= 100:
            raise ValueError('replay speed must be finite and in (0, 100]')
        self.speed = speed
        self.monotonic = monotonic
        self.started = monotonic()
        self.last_us = 0

    def now_us(self):
        now = int((self.monotonic() - self.started) * self.speed * 1_000_000)
        if now < self.last_us:
            raise ValueError('monotonic clock moved backwards')
        self.last_us = now
        return now

    @staticmethod
    def source_time(pts_us, cycle, duration_us):
        if any(type(v) is not int for v in (pts_us, cycle, duration_us)):
            raise ValueError('integer source clocks required')
        if cycle < 0 or not 0 <= pts_us < duration_us:
            raise ValueError('invalid cycle or source timestamp')
        return cycle * duration_us + pts_us
