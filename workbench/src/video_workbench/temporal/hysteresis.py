"""Timestamp-based causal categorical persistence with explicit missing evidence."""
from dataclasses import dataclass


@dataclass
class Hysteresis:
    persistence_us: int = 500_000
    max_gap_us: int = 750_000
    current: int = -1
    candidate: int = -1
    candidate_since: int | None = None
    last_us: int | None = None

    def __post_init__(self):
        if self.persistence_us < 0 or self.max_gap_us <= 0:
            raise ValueError("invalid persistence or gap")

    def update(self, event_us, label):
        """Return current label or -1. Startup also requires persistence.

        A missing label cancels history. After an excessive sampling gap,
        the current observation starts a fresh candidate without filling it.
        """
        if not isinstance(event_us, int) or event_us < 0:
            raise ValueError("integer nonnegative event timestamp required")
        if label is not None and (not isinstance(label, int) or label < 0):
            raise ValueError("label must be nonnegative integer or None")
        if self.last_us is not None and event_us <= self.last_us:
            raise ValueError("timestamps must strictly increase")
        gap = self.last_us is not None and event_us - self.last_us > self.max_gap_us
        self.last_us = event_us
        if gap or label is None:
            self.current = self.candidate = -1
            self.candidate_since = None
        if label is None:
            return -1
        if label == self.current:
            self.candidate = -1
            self.candidate_since = None
        else:
            if label != self.candidate:
                self.candidate, self.candidate_since = label, event_us
            if event_us - self.candidate_since >= self.persistence_us:
                self.current = label
                self.candidate = -1
                self.candidate_since = None
        return self.current
