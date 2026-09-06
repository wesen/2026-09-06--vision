"""Log-space scored HMM inference adapted from the ticket sequence lab.

Filter is prefix-causal; smooth and Viterbi consume the supplied full sequence.
Callers must split missing-evidence runs rather than publish imputed labels.
Discriminative emissions yield scored potentials, not calibrated probabilities.
"""
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



def filter(log_e, log_a, log_pi):
    """Normalized prefix messages; reject any impossible prefix."""
    alpha, _ = forward(log_e, log_a, log_pi)
    normalizers = logsumexp(alpha, axis=1)
    if not np.isfinite(normalizers).all():
        raise ValueError("No admissible prefix.")
    return np.exp(alpha - normalizers[:, None])
