"""Load a config, wire the components, run, write tape and measures.

Usage: python -m smallworld.run configs/e0.toml [--out results]
"""
from __future__ import annotations

import argparse
import csv
import importlib
import inspect
import os
import json
import random
import tomllib

from smallworld.core.tape import Tape
from smallworld.core.types import Arm, Check, Estimate, Expire, Fire, Message, Objection, Setup, Truth


def load_class(path: str):
    module, _, name = path.rpartition(".")
    return getattr(importlib.import_module(module), name)


def build(spec: dict, rng: random.Random, **inject):
    """Instantiate `spec["class"]` with `spec["params"]`. `rng` and any of
    `inject` are passed only if the constructor asks for them."""
    cls = load_class(spec["class"])
    params = dict(spec.get("params", {}))
    sig = inspect.signature(cls.__init__).parameters
    if "rng" in sig:
        params["rng"] = random.Random(rng.randrange(2**32))
    for name, value in inject.items():
        if name in sig and name not in params:
            params[name] = value
    return cls(**params)


def run(config: dict, out_dir: str | None = None) -> list[dict]:
    rng = random.Random(config.get("seed", 0))
    k = config["k"]

    world = build(config["world"], rng, k=k)
    disclosure = build(config["disclosure"], rng)
    task = build(config["task"], rng)
    topology = build(config["topology"], rng)
    scheduler = build(config["scheduler"], rng)
    runner_repair = build(config["repair"], rng)

    specs = config["agents"]
    groups = {a["id"]: a["group"] for a in specs}
    edges = topology.edges(groups)
    neighbours = {i: [] for i in groups}
    for a, b in edges:
        neighbours[a].append(b)
        neighbours[b].append(a)

    agents = {}
    for a in specs:
        gauge = a.get("gauge", "random")
        gauge = rng.randrange(k) if gauge == "random" else int(gauge)
        factor = build(config["factor"], rng, k=k, resolution=a["resolution"], gauge=gauge)
        agent_spec = {"class": a.get("class", config["agent"]["class"]),
                      "params": {**config["agent"].get("params", {}), **a.get("params", {})}}
        agents[a["id"]] = build(
            agent_spec, rng,
            id=a["id"], group=a["group"], factor=factor,
            watchdog=build(config["watchdog"], rng),
            repair=build(config["repair"], rng),
            task=task, k=k, neighbours=neighbours[a["id"]],
        )

    cut = {tuple(sorted(e)) for e in config.get("cut", [])}
    # Initial translations. "zero" (default): every agent assumes its
    # neighbours share its frame. "random_antisymmetric": each edge gets a
    # random g for one direction and its negative for the other, so the
    # edge is consistent but the cycle sums (holonomy) are arbitrary.
    init = config.get("translations", {}).get("init", "zero")
    if init == "random_antisymmetric":
        trng = random.Random(config.get("translations", {}).get("seed", 0))
        for a, b in edges:
            v = trng.randrange(k)
            agents[b].set_translation(a, v)
            agents[a].set_translation(b, -v)
    elif init != "zero":
        raise ValueError(f"unknown translations.init: {init}")

    observer = build(config["observer"], rng, agents=agents, edges=edges, k=k, cut=cut, task=task)

    tape = Tape()
    tape.append(Setup(
        round=-1,
        gauges={i: a.factor.ground_truth_gauge() for i, a in agents.items()},
        resolutions={i: a.factor.resolution for i, a in agents.items()},
        translations={f"{p}>{i}": a.translation(p) for i, a in agents.items() for p in neighbours[i]},
    ))
    measures = []
    for r in range(config["rounds"]):
        facts = world.draw(r)
        tape.append(Truth(round=r, facts=facts, target=task.truth(facts, k)))
        for a in agents.values():
            a.begin_round(r, disclosure.visible(a.id, a.group, facts))

        last_written = {i: -1 for i in agents}
        last_received = {i: -1 for i in agents}
        for src, dst in scheduler.exchanges(r, edges):
            gained = objected = False
            for out in agents[src].compose(dst):
                mseq = tape.append(Message(
                    round=r, src=src, dst=dst, kind=out.kind, value=out.value,
                    precision=out.precision, parents=(last_written[src], last_received[src]),
                ))
                last_written[src] = mseq
                last_received[dst] = mseq
                tape.append(Arm(round=r, writer=src, on=mseq))
                verdict = agents[dst].receive(src, out)
                gained = gained or verdict.gained
                objected = objected or (verdict.fired and verdict.object)
                if verdict.path_other is not None:
                    tape.append(Check(round=r, checker=dst, a=src, b=verdict.path_other, kind=out.kind))
                if verdict.fired:
                    fseq = tape.append(Fire(round=r, checker=dst, src=src, kind=out.kind,
                                            cause=verdict.cause, delta=verdict.delta, on=mseq))
                    if verdict.object:
                        sent = runner_repair.message(verdict.delta)
                        tape.append(Objection(round=r, src=dst, dst=src, delta=sent, on=fseq))
                        agents[dst].apply_objection(src, sent, as_objector=True)
                        agents[src].apply_objection(dst, sent, as_objector=False)
                else:
                    tape.append(Expire(round=r, writer=src, on=mseq))
            scheduler.delivered(src, dst, gained=gained, objected=objected)

        for a in agents.values():
            value, modulus = a.estimate()
            tape.append(Estimate(round=r, agent=a.id, value=value, modulus=modulus))
        measures.append(observer.end_round(r, tape))

    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        tape.dump(os.path.join(out_dir, "tape.jsonl"))
        with open(os.path.join(out_dir, "measures.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(measures[0]))
            w.writeheader()
            w.writerows(measures)
    return measures


def _merge(base: dict, over: dict) -> dict:
    out = dict(base)
    if "class" in over and over.get("class") != base.get("class"):
        # a different implementation: the base's parameters do not carry over
        out.pop("params", None)
    for key, value in over.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value  # lists (e.g. agents) are replaced, not merged
    return out


def load_config(path: str) -> dict:
    """Load a TOML config. A `base` key names another config (relative path)
    to start from; this file's tables are merged over it."""
    with open(path, "rb") as f:
        config = tomllib.load(f)
    if "base" in config:
        base = load_config(os.path.join(os.path.dirname(path), config.pop("base")))
        config = _merge(base, config)
    return config


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("config")
    p.add_argument("--out", default="results")
    args = p.parse_args()
    config = load_config(args.config)
    out = os.path.join(args.out, config.get("name", os.path.splitext(os.path.basename(args.config))[0]))
    measures = run(config, out)
    with open(os.path.join(out, "config.resolved.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    last = measures[-1]
    print(" ".join(f"{k}={v:.3g}" if isinstance(v, float) else f"{k}={v}" for k, v in last.items()))


if __name__ == "__main__":
    main()
