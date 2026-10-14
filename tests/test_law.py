"""E10 (DESIGN A2, LOG L37-L39): a law of nature on the ring."""
import os
import unittest

from smallworld.run import load_config, run

CONFIGS = os.path.join(os.path.dirname(__file__), "..", "configs")


class Law(unittest.TestCase):
    def test_law_without_twist_gives_full_knowledge(self):
        m = run(load_config(os.path.join(CONFIGS, "e10a_law_ring.toml")))
        for row in m[-20:]:
            self.assertEqual(row["knowledge"], 1.0)
            self.assertEqual(row["fact_right"], 1.0)
            self.assertEqual(row["disputes"], 0)

    def test_twist_makes_observers_dissent(self):
        m = run(load_config(os.path.join(CONFIGS, "e10b_law_ring_twist.toml")))
        for row in m[-20:]:
            self.assertEqual(row["dissidents"], 4)
            self.assertEqual(row["silent_wrong_facts"], 9)


if __name__ == "__main__":
    unittest.main()
