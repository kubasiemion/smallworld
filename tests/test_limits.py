"""MISSION commitment 6: the degenerate limit must reduce to consensus on the truth.
Also pins LOG L3: without common ground, agreement is total and correctness zero."""
import os
import unittest

from smallworld.run import load_config, run

CONFIGS = os.path.join(os.path.dirname(__file__), "..", "configs")


class Limits(unittest.TestCase):
    def test_e0_consensus(self):
        m = run(load_config(os.path.join(CONFIGS, "e0.toml")))
        for row in m[-10:]:
            self.assertEqual(row["correct"], 1.0)
            self.assertEqual(row["agree"], 1.0)
            self.assertEqual(row["edge_err_visible"] + row["edge_err_invisible"], 0)
            self.assertEqual(row["holonomy_cut_cycles"] + row["holonomy_inner_cycles"], 0)

    def test_e0b_offset_without_common_ground(self):
        m = run(load_config(os.path.join(CONFIGS, "e0b_no_common_ground.toml")))
        for row in m[-10:]:
            self.assertEqual(row["agree"], 1.0)
            self.assertEqual(row["correct"], 0.0)
            self.assertEqual(row["fires_reading"] + row["fires_path"], 0)


if __name__ == "__main__":
    unittest.main()
