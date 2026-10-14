"""E9 (LOG L34-L35): holonomy on a single-source ring."""
import json
import os
import tempfile
import unittest

from smallworld.ring_explain import explain
from smallworld.run import load_config, run

CONFIGS = os.path.join(os.path.dirname(__file__), "..", "configs")


def explained(name, round=0):
    with tempfile.TemporaryDirectory() as d:
        cfg = load_config(os.path.join(CONFIGS, f"{name}.toml"))
        run(cfg, d)
        with open(os.path.join(d, "config.resolved.json"), "w") as f:
            json.dump(cfg, f)
        return explain(d, round)


class RingTwist(unittest.TestCase):
    def test_coboundary_paths_agree(self):
        head, rows = explained("e9a_ring_gauge_offset")
        self.assertEqual(head["holonomy"], 0)
        for r in rows:
            self.assertTrue(all("C" in m and "W" in m for m in r["marks"].values()))

    def test_twist_assembles_two_frames_silently(self):
        head, rows = explained("e9b_ring_twist")
        self.assertNotEqual(head["holonomy"], 0)
        self.assertEqual(head["objections"], 0)
        marks = rows[4]["marks"].values()
        self.assertTrue(any("C" in m and "W" not in m for m in marks))
        self.assertTrue(any("W" in m and "C" not in m for m in marks))

    def test_common_factor_detects_and_flattens_twist(self):
        head, rows = explained("e9d_ring6_twist", round=50)
        self.assertEqual(head["holonomy"] % 6, 0)
        self.assertNotEqual(head["holonomy"], 0)


if __name__ == "__main__":
    unittest.main()
