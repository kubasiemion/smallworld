"""Per-agent propagation report for a single-source run (E5).

Usage: python -m smallworld.propagation results/e5a_ring_coprime [--source 0]

For each agent: its resolution m, how often it holds an estimate, how often
the estimate is right at its own resolution (vs chance 1/m), and how often it
is right at the path ceiling: the gcd of the resolutions along the chain of
first-delivered messages back to the source, the most a relay can preserve.
"""
from __future__ import annotations

import argparse
import json
import os
from math import gcd


def report(run_dir: str, source: int = 0) -> list[dict]:
    with open(os.path.join(run_dir, "config.resolved.json"), encoding="utf-8") as f:
        res = {a["id"]: a["resolution"] for a in json.load(f)["agents"]}
    truth, rows = {}, {i: [0, 0, 0, 0] for i in res}  # rounds, have, own, shared
    first, ceiling = {}, {i: {} for i in res}  # this round's first sender to each agent
    with open(os.path.join(run_dir, "tape.jsonl"), encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            if e["type"] == "Truth":
                truth[e["round"]] = e["target"]
                first = {}
            elif e["type"] == "Message":
                if e["dst"] != source:
                    first.setdefault(e["dst"], e["src"])
            elif e["type"] == "Estimate":
                r = rows[e["agent"]]
                r[0] += 1
                if e["value"] is not None:
                    r[1] += 1
                    g, j = res[e["agent"]], e["agent"]
                    while j != source and j in first:
                        j = first[j]
                        g = gcd(g, res[j])
                    ceiling[e["agent"]][g] = ceiling[e["agent"]].get(g, 0) + 1
                    z, m = truth[e["round"]], e["modulus"]
                    r[2] += (e["value"] - z) % m == 0
                    r[3] += (e["value"] - z) % g == 0
    return [{"agent": i, "m": res[i], "have": h / n, "own": o / n, "chance": 1 / res[i],
             "shared_g": max(ceiling[i], key=ceiling[i].get, default=0), "shared": s / n}
            for i, (n, h, o, s) in sorted(rows.items())]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("run_dir")
    p.add_argument("--source", type=int, default=0)
    a = p.parse_args()
    print("agent   m  have   own  chance  path-ceiling  right-at-ceiling")
    for r in report(a.run_dir, a.source):
        print(f"{r['agent']:>5} {r['m']:>3} {r['have']:5.2f} {r['own']:5.2f} {r['chance']:7.3f} {r['shared_g']:>12} {r['shared']:13.2f}")


if __name__ == "__main__":
    main()
