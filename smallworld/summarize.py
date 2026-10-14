"""Windowed means of a run's measures.

Usage: python -m smallworld.summarize results/e1 [--window 50] [--keys a,b,c]
"""
from __future__ import annotations

import argparse
import csv
import os

DEFAULT_KEYS = ["correct", "correct_chance", "agree", "wrong_agree", "silent_wrong",
                "fires_reading", "fires_path", "edge_err_visible", "edge_err_invisible",
                "holonomy_cut_cycles", "holonomy_inner_cycles"]


def summarize(run_dir: str, window: int = 50, keys: list[str] | None = None) -> list[dict]:
    keys = keys or DEFAULT_KEYS
    with open(os.path.join(run_dir, "measures.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = []
    for lo in range(0, len(rows), window):
        w = rows[lo:lo + window]
        out.append({"from": lo, **{k: sum(float(r[k]) for r in w) / len(w) for k in keys}})
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("run_dir")
    p.add_argument("--window", type=int, default=50)
    p.add_argument("--keys", default="")
    a = p.parse_args()
    keys = a.keys.split(",") if a.keys else None
    for row in summarize(a.run_dir, a.window, keys):
        print(" ".join(f"{k}={v:.2f}" if isinstance(v, float) else f"{k}={v}" for k, v in row.items()))


if __name__ == "__main__":
    main()
