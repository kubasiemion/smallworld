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

## 2026-10-14, first code

Implementation decisions not fixed by DESIGN:

**L7. Precision tag.** Messages carry the sender's resolution, so a watchdog
can compare at gcd(m_src, m_dst). Without it, a fine receiver would fire on
every coarse value.

**L8. Overconfident embedding.** A received value is lifted into the
receiver's ℤ_m as if exact (`ResolutionFactor.embed`). The agent keeps no
record of how precise a belief really is. This is the lossy factor of W-core
§1 and the full confidence of §7, and it is a choice: the alternative is
beliefs that carry their modulus (not built).

**L9. First come holds.** For a fact it does not see, an agent keeps the first
value received in a round and path-checks later arrivals against it. A path
check is logged as a `Check` event whether or not it fires; that is what
"filled triangle" means in the measures.

**L10. Path repairs are optional** (`path_repairs`). A path conflict cannot say
whether the upstream translation or upstream precision is at fault.

**L11. Configs inherit** via `base`. Tapes are not committed (size); measures
and resolved configs are.

Results, seed 1, 200 rounds (E0 60); seeds 2–4 checked for E1, E1b, E3 and
agree qualitatively. Numbers are means over rounds 100–199 unless noted.

**L12. E0 passes.** All edge errors and holonomy are 0 from round 2 on,
correct = agree = 1. Pinned as a test.

**L13. E0b confirms L3.** Without common ground: agree = 1, correct = 0, no
fires, every cut edge in error. A consistent, wrong answer with total silence.
Pinned as a test.

**L14. E1: heterogeneity alone produces wrong agreement, but not silently.**
Correct ≈ 0.38 against chance 0.22; wrong-agreeing pairs ≈ 0.12; silent
wrong (wrong, and not involved in any fire that round) ≈ 0.17. Repair traffic
never stops (≈ 7 reading and 6 path fires per round). Mechanism: path
conflicts caused by precision loss are repaired as translation errors, which
breaks calibrated edges, which reading checks then repair back. Churn, not
convergence.

**L15. E1b (no path repairs): calibration holds, the twist stays.** Visible
edge error ≈ 0.1, invisible ≈ 11 of 16 directed edges, silent wrong ≈ 0.38,
correctness unchanged. Path fires persist at ≈ 4 per round: the
path-dependence is detected, every round, and nothing can act on it. This is
the closest thing yet to the target failure.

**L16. E2: the triad exposes but does not repair.** Holonomy concentrates on
filled triangles (≈ 3 of 4 filled have nonzero holonomy), fires rise,
correctness ≈ 0.44. DESIGN §6's "then gets repaired" fails, for the L14
reason.

**L17. E3: the hub prediction fails.** A full-resolution hub seeing only z
does not collapse holonomy. It relays overconfident lifts to everyone, path
fires rise to ≈ 30 per round, silent wrong drops to ≈ 0.01, correctness does
not improve. The hub makes the error loud, not small. A hub without operand
readings is a relay, not a gauge.

**L18. E4 (bare repair)** roughly doubles reading fires against E1 with no
gain in correctness.

**L19. Open confound.** Wrong agreement in E1–E4 may come from the twist
(holonomy) or from the overconfident lift (L8), and the measures do not yet
separate them. The control is beliefs that carry their modulus. If errors
vanish under it, the twist in this model is an artefact of overconfidence; if
they persist, it is cohomological. This decides whether the stop rule's second
clause has been met.

**L20. Terminology repair: Objection vs Correction** (DESIGN A1). What the code
called `Repair` comes from the listener and goes back to the writer. In the
protocol, a repair comes from the original source after the listener's
continuation: message → continuation → correction. The implemented event is
renamed `Objection`; `Correction` and `Continuation` are reserved for the
writer-side protocol. Renamed alongside: `Agent.corrected` →
`apply_objection`, `Verdict.repair` → `object`, agent param `path_repairs` →
`path_objections`, measures `repairs`/`repair_size` →
`objections`/`objection_size`. All runs regenerated; only CSV headers
changed, values identical.

Consequence for reading L14–L18: every "repair" there is an objection. The
writer-side protocol has not been run at all.
