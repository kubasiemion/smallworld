# Log

Append-only. Decisions, repairs and dropped branches, each dated. Entries are
never edited; a later entry may supersede an earlier one by saying so.

## 2026-10-14

**L1. Mission committed.** Accepted without amendment.

**L2. Design accepted**, with the component split proposed in review:

- "Facts" split into World (draws, holds truth) and Disclosure (who sees what).
- "Predicates" split into Task (the target, x − y), Watchdog (agent-side check)
  and Repair (bare vs named).
- "Connections" split into Topology (who can talk) and Scheduler (order of
  exchanges; generates the event DAG and decides where triads fill).
- Factor separated from Agent, so heterogeneity varies independently of
  behaviour.
- Tape and Observer made explicit. Agents are physically isolated from both.

Each component is an interface in `core/` with its default in `impl/`. No
factories; the run config names the implementation.

**L3. Repair to the task (DESIGN §4).** With x disclosed only to X and y only to
Y, the cross-cut gauge cannot be calibrated. Result: consistent, wrong d,
off by a constant, every check passing. That is an H⁰-type failure (offset),
not holonomy. Disclosure must therefore supply common ground (a shared fact or
broker agents). Two failures are now measured separately: offset and holonomy.

**L4. Target is the gauge-invariant difference x − y**, not x + y. Invariance
holds per frame only; cross-frame operands still need the transition map.

**L5. No collision.** Truth is never revealed to agents. The experimenter alone
holds it.

**L6. Python**, standard library plus networkx.

**Dropped branches (for now, not refuted):** non-abelian coefficients
(discourse sheaves); references and nearest-key resolution; residue and decay;
endogenous stakes; partner-attached trust; directed-topology treatment of time
beyond triads forming and lapsing; bots (planned as an Agent implementation
after E0–E4).
