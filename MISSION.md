# Mission

Committed 2026-10-14. This file is not edited. Changes are appended below as dated amendments.

## Aim

Build the smallest executable model in which communication is distributed
computation among heterogeneous finite agents, and show mechanistically where a
jointly computed answer goes wrong without any participant being able to see it.

## Commitments

1. **Agents are finite and different.** W ≠ W′, and stays so. Each agent acts on a
   lossy factor of what it reads, never on the thing itself.
2. **The conversation computes.** Shared state is an append-only tape. Agents
   are heads on it, not containers of the result.
3. **Installation is never confirmed.** After a write, the writer arms a
   default-accept watchdog on the other party's continuations. Repair is the
   only error-driven channel. Events: write, arm, fire → repair, expire.
4. **There is a world, and only the experimenter sees it.** The oracle discloses
   x to one group and y to another; the agents must jointly arrive at x − y.
   Truth is logged, never revealed to the agents.
5. **The target failure is edge-invisible.** Twist that every pairwise check
   passes (holonomy, H¹) is what we measure, separately from disagreement.
6. **Consensus is the degenerate limit.** With identical agents and exact
   references, the model must reduce to plain agreement on the truth. If it
   does not, the model is wrong, not interesting.

## Non-goals

- No claim about LLM internals. The architecture is a benchmark, not a subject.
- No hierarchy of predictive models. Watchdogs are predicates, not minds.
- No non-abelian coefficients, references, residues or stakes dynamics until the
  abelian model has produced a result.
- No polishing of W-core, the glossa or the fibre taxonomy here.

## Stop rule

The work proceeds while each step yields something buildable. It stops, as a
result rather than a failure, if either:

- the degenerate limit cannot be made to pass, or
- heterogeneity of resolution does not produce silent wrong agreement on
  cycles that cross the disclosure cut, and no small change to the model
  makes the difference between that and ordinary disagreement observable.

## Discipline

MISSION is frozen. DESIGN is written and committed before code. LOG is
append-only: decisions, repairs and dropped branches, each dated.

---

## Amendments

(none)
