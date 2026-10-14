"""MergeAgent (honest moduli, CRT merge): LOG L25-L28."""
import os
import tempfile
import unittest

from smallworld.propagation import report
from smallworld.run import load_config, run

CONFIGS = os.path.join(os.path.dirname(__file__), "..", "configs")


def claimed(name):
    with tempfile.TemporaryDirectory() as d:
        cfg = load_config(os.path.join(CONFIGS, f"{name}.toml"))
        run(cfg, d)
        import json
        with open(os.path.join(d, "config.resolved.json"), "w") as f:
            json.dump(cfg, f)
        return {r["agent"]: (r["claimed"], r["own"]) for r in report(d)}


class Merge(unittest.TestCase):
    def test_meeting_point_triangulates(self):
        c = claimed("e6c_merge_complement")
        self.assertEqual(c[4][0], 23205)  # lcm of the two fronts, within agent 4
        self.assertTrue(all(own == 1.0 for _, own in c.values()))

    def test_bridge_reaches_ceiling(self):
        c = claimed("e6d_merge_chord")
        best = [255255, 85085, 51051, 36465, 23205, 19635, 15015]  # gcd(m_j, m_0)
        self.assertEqual([c[i][0] for i in range(7)], best)

    def test_honest_moduli_remove_wrong_agreement(self):
        m = run(load_config(os.path.join(CONFIGS, "e6_e1_merge.toml")))
        for row in m[-50:]:
            self.assertEqual(row["correct"], 1.0)
            self.assertEqual(row["silent_wrong"], 0.0)


if __name__ == "__main__":
    unittest.main()


class FloodScheduler(unittest.TestCase):
    def test_queue_flood_derives_the_e5_order(self):
        from smallworld.impl.schedulers import Flood
        ring = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (0, 6)]
        self.assertEqual(list(Flood(sources=[0]).exchanges(0, ring)),
                         [(0, 1), (0, 6), (1, 2), (6, 5), (2, 3), (5, 4), (3, 4), (4, 3)])
