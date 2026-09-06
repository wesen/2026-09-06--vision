"""Offline explicit-duration decoding adapted from the ticket sequence lab.

Durations count feature samples; use Sequence.segment_time for source coverage.
A maximum duration bounds each completed segment, including the final one.
"""
import numpy as np
from .hmm import _check


def hsmm_viterbi(log_e, log_a, log_pi, log_duration):
    """Offline explicit-duration decoder with completed final segment.

    duration[k, d-1] scores duration d. Adjacent segments cannot share a
    state: the duration distribution, not a self-transition, models dwell.
    Finite emissions are required for prefix sums. Durations are bounded.
    Returns half-open (start, end, state) segments and a total score.
    """
    e, a, pi = _check(log_e, log_a, log_pi)
    duration = np.asarray(log_duration, dtype=float)
    n, k = e.shape
    if (duration.ndim != 2 or duration.shape[0] != k
            or duration.shape[1] == 0):
        raise ValueError("Duration scores need shape [states, max_duration].")
    if (not np.isfinite(e).all() or np.isnan(duration).any()
            or np.isposinf(duration).any()):
        raise ValueError("Finite emissions and valid log durations required.")
    a = a.copy()
    np.fill_diagonal(a, -np.inf)
    prefix = np.vstack([np.zeros(k), np.cumsum(e, axis=0)])
    dp = np.full((n + 1, k), -np.inf)
    prev = np.full((n + 1, k), -1, dtype=int)
    lengths = np.zeros((n + 1, k), dtype=int)
    for end in range(1, n + 1):
        for state in range(k):
            for d in range(1, min(end, duration.shape[1]) + 1):
                start = end - d
                if start == 0:
                    base, parent = pi[state], -1
                else:
                    incoming = dp[start] + a[:, state]
                    parent = int(incoming.argmax())
                    base = incoming[parent]
                candidate = (base + duration[state, d - 1]
                             + prefix[end, state] - prefix[start, state])
                if candidate > dp[end, state]:
                    dp[end, state] = candidate
                    prev[end, state] = parent
                    lengths[end, state] = d
    state = int(dp[n].argmax())
    best = float(dp[n, state])
    if not np.isfinite(best):
        raise ValueError("No admissible duration-constrained path.")
    segments = []
    end = n
    while end:
        d = int(lengths[end, state])
        if d <= 0:
            raise RuntimeError("Invalid backpointer.")
        segments.append((end - d, end, state))
        parent = int(prev[end, state])
        end -= d
        state = parent
    return list(reversed(segments)), best
