"""Explain one round of a single-source ring run, prime by prime.

Usage: python -m smallworld.ring_explain results/e9b_ring_twist [--round 0]

On a ring with one source, a value reaches agent j along two paths:
clockwise (0→1→2→…→j) and counter-clockwise (0→6→5→…→j). Each path delivers
z in the source's frame plus the translations along it:

    via path P:  z + θ₀ + Σ g over P        (mod k)

and the agent's own-frame truth is z + θ_j. If the translations are a
coboundary (all start at 0, say), both paths deliver the same value and it
differs from the own-frame truth by a constant offset. If the ring has
holonomy H ≠ 0, the two paths deliver values that differ by H.

For every prime p dividing the modulus an agent claims, the report says which
of the three its residue mod p matches:
    O  own-frame truth      C  clockwise path      W  counter-clockwise path
A residue matching C on some primes and W on others is a class assembled
from two frames: right in neither.
"""
from __future__ import annotations

import argparse
import json
import os


def primes(n: int) -> list[int]:
    out, p = [], 2
    while p * p <= n:
        while n % p == 0:
            if p not in out:
                out.append(p)
            n //= p
        p += 1
    if n > 1:
        out.append(n)
    return out


def explain(run_dir: str, round: int = 0, source: int = 0) -> tuple[dict, list[dict]]:
    """Translations are taken from Setup and brought forward by replaying
    every named Objection up to the end of `round` (objector: g += δ for the
    writer; writer: g -= δ for the objector), so paths are as they stood when
    the round's estimates were made. Bare objections cannot be replayed."""
    setup, truth, est, objections = None, None, {}, 0
    replay: list[tuple[int, int, int]] = []
    with open(os.path.join(run_dir, "tape.jsonl"), encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            if e["type"] == "Setup":
                setup = e
            if e["type"] == "Objection" and e["round"] <= round:
                if e["delta"] is None:
                    raise ValueError("bare objections cannot be replayed")
                replay.append((e["src"], e["dst"], e["delta"]))
            if e["round"] == round:
                if e["type"] == "Truth":
                    truth = e["facts"]
                elif e["type"] == "Estimate":
                    est[e["agent"]] = (e["value"], e["modulus"])
                elif e["type"] == "Objection":
                    objections += 1
    with open(os.path.join(run_dir, "config.resolved.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    k = cfg["k"]
    n_agents = len(cfg["agents"])
    theta = {int(i): v for i, v in setup["gauges"].items()}
    g = {tuple(map(int, key.split(">"))): v for key, v in setup["translations"].items()}
    for objector, writer, delta in replay:
        g[(writer, objector)] = (g[(writer, objector)] + delta) % k
        g[(objector, writer)] = (g[(objector, writer)] - delta) % k
    z = truth[cfg["task"]["params"]["a"]]

    def deliver(path: list[int]) -> int:
        v = z + theta[path[0]]
        for a, b in zip(path, path[1:]):
            v += g[(a, b)]
        return v % k

    ring = list(range(n_agents))
    holonomy = sum(g[(a, b)] for a, b in zip(ring, ring[1:] + ring[:1])) % k
    rows = []
    for j in ring:
        cw = ring[: j + 1] if j else [source]
        ccw = [source] + ring[:j - 1:-1] if j else [source]
        value, modulus = est.get(j, (None, 0))
        own = (z + theta[j]) % k
        marks = {}
        if value is not None:
            for p in primes(modulus):
                r = value % p
                marks[p] = "".join(c for c, ref in (("O", own), ("C", deliver(cw)), ("W", deliver(ccw)))
                                   if ref % p == r) or "-"
        rows.append({"agent": j, "value": value, "modulus": modulus,
                     "own_right": value is not None and (value - own) % modulus == 0,
                     "offset": None if value is None else (value - own) % modulus,
                     "marks": marks})
    head = {"z": z, "holonomy": holonomy, "objections": objections,
            "theta": theta, "k": k}
    return head, rows


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("run_dir")
    p.add_argument("--round", type=int, default=0)
    a = p.parse_args()
    head, rows = explain(a.run_dir, a.round)
    print(f"round {a.round}: z = {head['z']}, ring holonomy H = {head['holonomy']} (mod {head['k']}), "
          f"objections this round = {head['objections']}")
    for r in rows:
        if r["value"] is None:
            print(f"  agent {r['agent']}: no estimate")
            continue
        marks = " ".join(f"{p}:{m}" for p, m in r["marks"].items())
        verdict = "right in own frame" if r["own_right"] else f"off by {r['offset']} in own frame"
        print(f"  agent {r['agent']}: mod {r['modulus']:>6}  {verdict:<28}  {marks}")


if __name__ == "__main__":
    main()
