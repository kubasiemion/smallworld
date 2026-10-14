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

**L21. Open: repairs are symmetric, real ones are not.** With named
objections the objector does g += δ and the writer g −= δ, so g_ij + g_ji ≡ 0
for ever: every edge is antisymmetric by construction, which is HodgeRank's
assumption and the one we meant to break. Only E4 (bare: independent
re-guesses) is asymmetric, and nobody measured it. Real asymmetry needs
per-side state, not just a different update formula: the corrected party
must guess *where* the correction lands, uptake can fail, residue sits on
one side. Quine's point applies: a recalcitrant verdict underdetermines
which belief to revise, and weights (entrenchment) decide. So an asymmetric
policy is a weighted distribution of δ over the corrected party's adjustable
state, not a sign flip. First step when we get there: an antisymmetry-defect
measure e_ij + e_ji in the Observer.

## 2026-10-14, E5 ring

**L22. E5: one fact on a ring of seven.** Only agent 0 sees z; the wave runs
outward both ways in a fixed order (new `Fixed` scheduler, `Identity` task).
All gauges 0 and translations start correct, so precision is the only thing in
play. k = 510510. A: resolutions are distinct primes (2,3,5,7,11,13,17), gcd 1
on every edge. B: multiples of 6 (6,30,42,66,78,102,210), gcd 6 on every edge.
Note "not prime" is not enough: neighbours sharing *different* factors lose
the information after two hops, since the next hop keeps only the gcd of that
edge. B shares one factor along the whole ring on purpose.

Result (200 rounds, `python -m smallworld.propagation results/e5*`):
- Fires 0, objections 0 in both arms. Checks compare at gcd; in A that is 1,
  in B the paths agree mod 6 by construction. Nothing is detected, nothing is
  repaired.
- Right at own resolution: A is at chance (1/m) for every agent. B is at ≈ m₀/m
  (0.23 … 0.04), well above chance 1/m but still mostly wrong, and it falls
  with m, not with hop distance (agent 6 is one hop out and the worst).
  This is the overconfident lift (L8): a value v ∈ [0, m₀) is read as exact
  in ℤ_m, so it is right only when z mod m happens to be < m₀.
- Right at gcd(m, m₀): 1.00 for everyone in B (z mod 6 reaches all seven).
  In A the gcd is 1, so the invariant is empty.
- So the ring carries exactly the common factor and nothing more, in both
  arms, and no agent can tell how much that is. Silent wrong stays at 0.7–0.9.

**L23. E5c: complement resolutions.** Same ring, agent i has m_i = k / p_i, so
it resolves every prime of k except its own. Neighbours share k/(p_i p_j).
`propagation` now reports the *path ceiling*, the gcd of resolutions along the
first-delivered chain back to the source (L22's per-source gcd was too generous
for multi-hop). Ceilings: 85085, 17017, 2431 going one way (agents 1–3); 15015,
1155, 105 the other (6, 5, 4). Agents are right at their ceiling 100% of the
time, and at their own resolution 0.48, 0.32, 0.20 / 0.48, 0.04, 0.04. Each
hop costs one prime; the ring carries k / (product of primes on the path).
First case with fires: a path check at the meeting point (agent 4 against 3)
fires in ~90% of rounds, delta ~3000 and different each round. It is a
precision conflict (two paths with different missing primes), but it is
objected to as a translation error (L10, L14), so g(3,4) is moved by a
different amount every round and keeps two visible edge errors alive for all
200 rounds. The ceilings stay intact, but the ring never converges: churn.

**L24. E5d: chord 2–5 added to E5c.** Path ceilings, own-resolution accuracy
and correctness are identical to E5c (0.36). The chord changes nothing about
what agents know, because first come holds (L9): the second arrival is only
path-checked, never merged. What it adds is a second churn site: agent 5
against 2 fires in 177/200 rounds, next to 4 against 3 (179/200). Visible edge
errors 3.6 (was 1.9), cycles with holonomy 2 (was 1). More paths with
different missing primes means more conflicts, and the agent has nothing to
do with them but misattribute them. A relay cannot gain from redundancy;
combining beliefs (gcd/CRT-style) would be a different Agent.

## 2026-10-14, merge

**L25. MergeAgent** (`impl/merge_agent.py`). Beliefs are congruence classes
with an honest modulus. An arrival (w mod n), translated, becomes a class mod
gcd(n, m); it is merged with what is held by CRT when the two agree on their
common modulus (giving the lcm), and fires only when they disagree there,
which is then a real conflict, not precision loss. Messages carry the true
modulus as `precision`, so nothing is laundered. This is the L19 control and
the merge suggested after E5. Configs `e6*` are earlier configs with the agent
class swapped.

**L26. E6a–d: the ring under merge.** No fires anywhere. Coprime ring (E6a):
only the source has an estimate; the others honestly hold nothing. Common
factor (E6b): everyone holds z mod 6, right every round. Complement ring
(E6c): the meeting point triangulates as predicted, agent 4 at 23205 (relay:
105, a 221-fold gain) and agent 3, getting it back, at 36465 (relay: 2431).
Every estimate right at its claimed modulus. The conflict that churned in E5c
was the information.

**L27. One bridge completes the ring.** E6d adds the chord 2–5. Agents 2 and 5
go from 17017 and 1155 to 51051 and 19635, and now every agent holds exactly
gcd(m_j, m_0), the most it can know about the source's reading. Under the
relay (E5d) the same chord only added a second churn site. Same edge, opposite
effect, decided by whether arrivals are merged or checked.

**L28. L19 answered: the twist is real and harmless; overconfidence is what
makes it wrong.** E1, E1b, E2, E3 rerun with MergeAgent:

| | relay correct | merge correct | merge silent wrong | merge fires (r100+) | merge invisible edge err | merge holonomy (cut / inner) |
|---|---|---|---|---|---|---|
| E1 | 0.39 | 1.00 | 0 | 0 | 10 | 0 / 1 |
| E2 | 0.44 | 1.00 | 0 | 0 | 14 | 2 / 2 |
| E3 | 0.34 | 1.00 | 0 | 0 | 12 | 1 / 3 |

Holonomy persists, at the same level as under the relay, but no estimate is
ever wrong, because every translation error is a multiple of what the two
ends can jointly resolve and honest classes are reduced to exactly that. The
H¹ class lives entirely in the part nobody claims to know. Cost: coverage
falls to 0.67 in E1/E2 (agents behind gcd-1 edges honestly hold nothing).
E3 reverses L17: with honest moduli the hub raises coverage to 1.0. A hub that
does not launder precision is a gauge after all.

Together with L23 (E5c), overconfidence does two things: it *activates* a
twist that is otherwise harmless (L28), and, through objections to precision
conflicts, it *manufactures* twist where there was none (L23).

**Bearing on MISSION's stop rule.** The second clause asks whether
heterogeneity of resolution produces silent wrong agreement on cut-crossing
cycles. Under honest moduli it does not, at all. Under overconfident lifting
it does. So heterogeneity alone is not sufficient; heterogeneity plus
overconfidence is. Whether that meets or triggers the stop rule is a call for
the next entry, not this one.

## 2026-10-14, waves

**L29. Flood scheduler.** An informed node informs every neighbour except the
one that informed it; newly informed neighbours join the frontier; each node
takes one turn per round; already informed neighbours still receive (that is
where fronts meet and cross). `mode` is "queue" (breadth-first waves) or
"stack" (depth-first). On the ring from agent 0 the queue flood derives E5's
hand-written order exactly: E7a reproduces E5c bit for bit (pinned as a test).

Config inheritance repaired alongside: when a table names a different `class`
than its base, the base's `params` no longer carry over (they belong to the
other implementation). This silently changed one committed run, e6_e1b_merge,
which had relied on inheriting `path_objections = false`; the config now says
it explicitly and reproduces its committed results again. No other run changed.

**L30. Wave shape decides who triangulates.** MergeAgent, complement ring,
claimed modulus per agent (ceiling for each is gcd(m_j, m₀)):

| agent | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| ceiling | 85085 | 51051 | 36465 | 23205 | 19635 | 15015 |
| queue, ring (E6c) | 85085 | 17017 | 36465 | 23205 | 1155 | 15015 |
| queue, chord (E7b) | 85085 | 51051 | 36465 | 23205 | 19635 | 15015 |
| stack, ring (E7d) | 85085 | 51051 | 15 | 105 | 1155 | 15015 |
| stack, chord (E7c) | 85085 | 51051 | 165 | 105 | 1155 | 15015 |

Breadth-first: two fronts with short paths meet at the antipode, and the
meeting point triangulates. Depth-first: one front runs the long way round
(0-6-5-4-3-2), each hop costs a prime, and the fronts meet next to the source
(at 1-2), so only agent 2 gains; agent 3 drops from 36465 to 15. The chord that
completes the ring under a breadth-first wave barely helps a depth-first one
(agent 3: 15 → 165). Same graph, same agents, same bridge: the order of
telling decides what is known.
