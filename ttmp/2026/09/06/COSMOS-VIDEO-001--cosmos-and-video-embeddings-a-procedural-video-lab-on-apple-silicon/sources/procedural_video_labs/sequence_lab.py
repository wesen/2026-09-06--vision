"""Inspectable temporal-inference examples; not a production monitor.

Run: python sequence_lab.py
Requires NumPy. All demo inputs are synthetic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
import json
import math
import numpy as np


def log_prob(p: np.ndarray) -> np.ndarray:
    """Map nonnegative probabilities to logs, preserving impossible events."""
    p = np.asarray(p, dtype=float)
    if np.any(~np.isfinite(p)) or np.any(p < 0) or np.any(p > 1):
        raise ValueError("Probabilities must be finite and in [0, 1].")
    out = np.full_like(p, -np.inf)
    np.log(p, out=out, where=p > 0)
    return out


def logsumexp(a: np.ndarray, axis: int | None = None) -> np.ndarray:
    """Stable log sum, including an all-impossible slice."""
    a = np.asarray(a, dtype=float)
    m = np.max(a, axis=axis, keepdims=True)
    safe_m = np.where(np.isfinite(m), m, 0.0)
    total = np.exp(a - safe_m).sum(axis=axis, keepdims=True)
    out = np.full_like(total, -np.inf)
    np.log(total, out=out, where=total > 0)
    out = out + safe_m
    return np.squeeze(out, axis=axis) if axis is not None else out.squeeze()


def _check(log_e, log_a, log_pi):
    e = np.asarray(log_e, dtype=float)
    a = np.asarray(log_a, dtype=float)
    pi = np.asarray(log_pi, dtype=float)
    if e.ndim != 2 or min(e.shape) == 0:
        raise ValueError("Evidence must have nonempty shape [time, states].")
    k = e.shape[1]
    if a.shape != (k, k) or pi.shape != (k,):
        raise ValueError("Transition or initial-state shape mismatch.")
    for x in (e, a, pi):
        if np.isnan(x).any() or np.isposinf(x).any():
            raise ValueError("Scores may be finite or -inf, never NaN/+inf.")
    return e, a, pi


def forward(log_e, log_a, log_pi):
    """Return log forward messages and total log likelihood/potential sum."""
    e, a, pi = _check(log_e, log_a, log_pi)
    alpha = np.empty_like(e)
    alpha[0] = pi + e[0]
    for t in range(1, len(e)):
        alpha[t] = e[t] + logsumexp(alpha[t - 1, :, None] + a, axis=0)
    return alpha, float(logsumexp(alpha[-1]))


def smooth(log_e, log_a, log_pi):
    """Offline state marginals. Reject a sequence with zero total support."""
    e, a, pi = _check(log_e, log_a, log_pi)
    alpha, log_z = forward(e, a, pi)
    if not np.isfinite(log_z):
        raise ValueError("No admissible path.")
    beta = np.zeros_like(e)
    for t in range(len(e) - 2, -1, -1):
        beta[t] = logsumexp(a + e[t + 1] + beta[t + 1], axis=1)
    return np.exp(alpha + beta - log_z), log_z


def viterbi(log_e, log_a, log_pi):
    """Most likely complete path; ties choose the first state index."""
    e, a, pi = _check(log_e, log_a, log_pi)
    score = np.empty_like(e)
    back = np.full(e.shape, -1, dtype=int)
    score[0] = pi + e[0]
    for t in range(1, len(e)):
        candidates = score[t - 1, :, None] + a
        back[t] = candidates.argmax(axis=0)
        score[t] = candidates.max(axis=0) + e[t]
    state = int(score[-1].argmax())
    best = float(score[-1, state])
    if not np.isfinite(best):
        raise ValueError("No admissible path.")
    path = np.empty(len(e), dtype=int)
    path[-1] = state
    for t in range(len(e) - 1, 0, -1):
        path[t - 1] = back[t, path[t]]
    return path, best


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


def collapse(labels):
    """Convert dense labels to half-open segments."""
    values = list(labels)
    if not values:
        return []
    out, start = [], 0
    for t in range(1, len(values) + 1):
        if t == len(values) or values[t] != values[start]:
            out.append((start, t, values[start]))
            start = t
    return out


def temporal_iou(p, g):
    if p[1] <= p[0] or g[1] <= g[0]:
        raise ValueError("Intervals must have positive length.")
    intersection = max(0.0, min(p[1], g[1]) - max(p[0], g[0]))
    union = (p[1] - p[0]) + (g[1] - g[0]) - intersection
    return intersection / union


def edit_score(prediction, truth):
    """Normalized Levenshtein similarity of collapsed label sequences."""
    p = [s[2] for s in collapse(prediction)]
    g = [s[2] for s in collapse(truth)]
    previous = list(range(len(g) + 1))
    for i, label in enumerate(p, 1):
        current = [i]
        for j, target in enumerate(g, 1):
            current.append(min(current[-1] + 1, previous[j] + 1,
                               previous[j - 1] + (label != target)))
        previous = current
    return 100.0 * (1 - previous[-1] / max(len(p), len(g), 1))


@dataclass
class PrerequisiteMonitor:
    """Minimal monotone procedure; rework invalidation is not modeled."""
    prerequisites: dict[str, set[str]]
    completed: set[str] = field(default_factory=set)
    coverage_complete: bool = True

    def gap(self):
        self.coverage_complete = False

    def observe(self, step: str, postcondition: bool | None):
        if step not in self.prerequisites:
            raise ValueError(f"Unknown step: {step}")
        missing = self.prerequisites[step] - self.completed
        status = "supported"
        if missing:
            status = "wrong_order" if self.coverage_complete else "uncertain"
        result = {"observed_step": step, "status": status,
                  "unmet_prerequisites": sorted(missing)}
        if postcondition is True:
            self.completed.add(step)
        return result


@dataclass
class PersistenceGate:
    """One incident per episode. A missing sample cancels persistence.

    The caller must route observation_gap to its own health/review path.
    This small example does not implement incident reconciliation.
    """
    high: float = 0.8
    low: float = 0.3
    persistence_s: float = 1.0
    max_gap_s: float = 0.75
    start: float | None = None
    last: float | None = None
    active: bool = False

    def __post_init__(self):
        if not (0 <= self.low < self.high <= 1):
            raise ValueError("Require 0 <= low < high <= 1.")
        if self.persistence_s < 0 or self.max_gap_s <= 0:
            raise ValueError("Invalid time parameters.")

    def update(self, time_s: float, score: float | None):
        if not math.isfinite(time_s):
            raise ValueError("Timestamp must be finite.")
        if self.last is not None and time_s <= self.last:
            raise ValueError("Timestamps must strictly increase.")
        if score is not None and (not math.isfinite(score) or not 0 <= score <= 1):
            raise ValueError("Score must be in [0, 1], or None.")
        gap = self.last is not None and time_s - self.last > self.max_gap_s
        self.last = time_s
        if score is None or gap:
            self.start, self.active = None, False
            return "observation_gap"
        if score < self.low:
            self.start, self.active = None, False
            return "normal"
        if self.start is None and score >= self.high:
            self.start = time_s
        if self.start is not None and not self.active:
            if time_s - self.start >= self.persistence_s:
                self.active = True
                return "incident"
        return "active" if self.active else ("possible" if self.start is not None else "normal")


def demo():
    # Two-state generative HMM with abstract states A (0), B (1).
    a = np.array([[0.7, 0.3], [0.1, 0.9]])
    pi = np.array([0.9, 0.1])
    e = np.array([[0.6, 0.1], [0.3, 0.4], [0.1, 0.5]])
    logs = [log_prob(x) for x in (e, a, pi)]
    alpha, log_z = forward(*logs)
    marginals, _ = smooth(*logs)
    path, score = viterbi(*logs)
    # Independent exhaustive check, only for this tiny example.
    paths = list(product(range(2), repeat=3))
    probabilities = []
    for p in paths:
        prob = pi[p[0]] * e[0, p[0]]
        for t in range(1, 3):
            prob *= a[p[t - 1], p[t]] * e[t, p[t]]
        probabilities.append(prob)
    assert np.isclose(np.exp(log_z), sum(probabilities))
    assert np.isclose(np.exp(score), max(probabilities))
    assert tuple(path) == paths[int(np.argmax(probabilities))]
    assert np.allclose(marginals.sum(axis=1), 1)
    assert float(logsumexp(np.array([-np.inf, -np.inf]))) == -np.inf
    # Explicit-duration A -> B, each duration 1 or 2.
    he = log_prob(np.array([[0.9, 0.1], [0.8, 0.2],
                           [0.2, 0.8], [0.1, 0.9]]))
    ha = log_prob(np.array([[0.0, 1.0], [1.0, 0.0]]))
    hp = log_prob(np.array([1.0, 0.0]))
    hd = log_prob(np.array([[0.2, 0.8], [0.2, 0.8]]))
    segments, hs = hsmm_viterbi(he, ha, hp, hd)
    assert segments == [(0, 2, 0), (2, 4, 1)]
    assert np.isclose(np.exp(hs), 0.331776)
    prereq = {"align": set(), "insert": {"align"},
              "tighten": {"insert"}}
    monitor = PrerequisiteMonitor(prereq)
    monitor.observe("align", True)
    violation = monitor.observe("tighten", True)
    assert violation["status"] == "wrong_order"
    uncertain = PrerequisiteMonitor(prereq)
    uncertain.observe("align", True)
    uncertain.gap()
    assert uncertain.observe("tighten", True)["status"] == "uncertain"
    gate = PersistenceGate()
    gate_output = [gate.update(t, s) for t, s in
                   [(0, .1), (.5, .85), (1, .9), (1.5, .88), (2, .2)]]
    assert gate_output == ["normal", "possible", "possible", "incident", "normal"]
    assert np.isclose(temporal_iou((2, 6), (3, 7)), .6)
    assert edit_score("AAAABBBBCCCC", "AAAABBBBCCCC") == 100
    return {
        "hmm_forward_probability": round(float(np.exp(log_z)), 6),
        "hmm_forward_rows": np.exp(alpha).round(6).tolist(),
        "hmm_smoothed_marginals": marginals.round(6).tolist(),
        "hmm_best_path": path.tolist(),
        "hmm_best_path_probability": round(float(np.exp(score)), 6),
        "hsmm_segments": segments,
        "hsmm_path_weight": round(float(np.exp(hs)), 6),
        "procedure_violation": violation,
        "persistence_trace": gate_output,
        "temporal_iou": temporal_iou((2, 6), (3, 7)),
        "tests": "passed"
    }


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2))
