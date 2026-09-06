"""Regression tests for the textbook's teaching implementations.
Run: python -m unittest -v test_labs.py
"""
import itertools
import unittest
import numpy as np
from sequence_lab import (
    PrerequisiteMonitor, PersistenceGate, collapse, edit_score,
    forward, hsmm_viterbi, log_prob, logsumexp, smooth, temporal_iou,
    viterbi, demo,
)


class SequenceTests(unittest.TestCase):
    def test_demo(self):
        self.assertEqual(demo()["tests"], "passed")

    def test_log_zero(self):
        self.assertTrue(np.isneginf(log_prob(np.array([0.0]))[0]))

    def test_invalid_probability(self):
        with self.assertRaises(ValueError):
            log_prob(np.array([-0.1]))

    def test_logsumexp_impossible(self):
        x = np.array([[-np.inf, -np.inf], [0.0, 0.0]])
        y = logsumexp(x, axis=1)
        self.assertTrue(np.isneginf(y[0]))
        self.assertAlmostEqual(y[1], np.log(2))

    def test_viterbi_brute_force(self):
        rng = np.random.default_rng(14)
        for _ in range(12):
            a = rng.dirichlet(np.ones(3), size=3)
            pi = rng.dirichlet(np.ones(3))
            e = rng.uniform(.01, 1.0, size=(4, 3))
            le, la, lp = (log_prob(x) for x in (e, a, pi))
            path, value = viterbi(le, la, lp)
            brute = []
            for p in itertools.product(range(3), repeat=4):
                score = lp[p[0]] + le[0, p[0]]
                score += sum(la[p[t - 1], p[t]] + le[t, p[t]]
                             for t in range(1, 4))
                brute.append((score, p))
            best = max(brute)
            self.assertAlmostEqual(value, best[0])
            self.assertEqual(tuple(path), best[1])
            _, total = forward(le, la, lp)
            self.assertAlmostEqual(total, float(logsumexp(np.array([b[0] for b in brute]))))

    def test_smoothing_normalized(self):
        marginals, _ = smooth(np.zeros((5, 2)), np.log(np.full((2, 2), .5)),
                              np.log(np.array([.5, .5])))
        self.assertTrue(np.allclose(marginals, .5))

    def test_impossible_path(self):
        e = np.zeros((2, 2))
        a = np.full((2, 2), -np.inf)
        pi = np.array([0.0, -np.inf])
        with self.assertRaises(ValueError):
            viterbi(e, a, pi)
        with self.assertRaises(ValueError):
            smooth(e, a, pi)

    def test_empty_input(self):
        with self.assertRaises(ValueError):
            viterbi(np.empty((0, 2)), np.zeros((2, 2)), np.zeros(2))

    def test_hsmm_brute_force(self):
        rng = np.random.default_rng(15)
        for _ in range(10):
            n, k, dmax = 5, 2, 3
            e = np.log(rng.uniform(.05, 1, (n, k)))
            a = np.array([[-np.inf, 0.0], [0.0, -np.inf]])
            pi = np.log(np.array([.7, .3]))
            dur = np.log(rng.dirichlet(np.ones(dmax), size=k))
            candidates = []
            def visit(start, previous, score, segments):
                if start == n:
                    candidates.append((score, segments))
                    return
                for state in range(k):
                    if state == previous:
                        continue
                    base = pi[state] if previous is None else a[previous, state]
                    for d in range(1, min(dmax, n - start) + 1):
                        end = start + d
                        value = score + base + dur[state, d - 1] + e[start:end, state].sum()
                        visit(end, state, value, segments + [(start, end, state)])
            visit(0, None, 0.0, [])
            expected = max(candidates, key=lambda x: x[0])
            segments, score = hsmm_viterbi(e, a, pi, dur)
            self.assertAlmostEqual(score, expected[0])
            self.assertEqual(segments, expected[1])

    def test_hsmm_impossible_duration(self):
        with self.assertRaises(ValueError):
            hsmm_viterbi(np.zeros((2, 1)), np.zeros((1, 1)),
                         np.zeros(1), np.zeros((1, 1)))

    def test_collapse_empty(self):
        self.assertEqual(collapse([]), [])

    def test_collapse_bounds(self):
        self.assertEqual(collapse("AABB"), [(0, 2, "A"), (2, 4, "B")])

    def test_iou(self):
        self.assertEqual(temporal_iou((0, 1), (2, 3)), 0)
        self.assertEqual(temporal_iou((0, 1), (0, 1)), 1)

    def test_iou_invalid(self):
        with self.assertRaises(ValueError):
            temporal_iou((0, 0), (0, 1))

    def test_edit(self):
        self.assertEqual(edit_score([], []), 100)
        self.assertEqual(edit_score("AAAA", []), 0)
        self.assertAlmostEqual(edit_score("AABBAACC", "AABBCC"), 75)

    def test_prerequisites(self):
        m = PrerequisiteMonitor({"A": set(), "B": {"A"}})
        self.assertEqual(m.observe("B", None)["status"], "wrong_order")
        m.gap()
        self.assertEqual(m.observe("B", None)["status"], "uncertain")
        m.observe("A", True)
        self.assertEqual(m.observe("B", True)["status"], "supported")

    def test_unknown_step(self):
        with self.assertRaises(ValueError):
            PrerequisiteMonitor({}).observe("missing", None)

    def test_gate_hysteresis(self):
        g = PersistenceGate()
        self.assertEqual(g.update(0, .85), "possible")
        self.assertEqual(g.update(.5, .55), "possible")
        self.assertEqual(g.update(1.0, .60), "incident")
        self.assertEqual(g.update(1.5, .65), "active")
        self.assertEqual(g.update(2, .20), "normal")

    def test_gap_breaks_persistence(self):
        g = PersistenceGate()
        g.update(0, .9)
        self.assertEqual(g.update(.5, None), "observation_gap")
        self.assertEqual(g.update(1, .9), "possible")

    def test_timestamp_validation(self):
        g = PersistenceGate()
        g.update(0, .5)
        with self.assertRaises(ValueError):
            g.update(0, .5)


if __name__ == "__main__":
    unittest.main()
