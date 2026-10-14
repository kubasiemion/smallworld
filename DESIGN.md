# Design

Accepted 2026-10-14. Committed before any code. Changes after commit go to LOG.md
and an amended section here, never a silent rewrite.

## 0. Scope

Round-based simulation. Coefficients in ℤ_k. One task: the agents jointly
estimate a gauge-invariant difference of facts disclosed to different groups.
Everything in MISSION's non-goals stays out.

## 1. Components

Each component is an interface in `smallworld/core/` with its default
implementation in `smallworld/impl/`. A component is separate if we expect to
vary it independently in an experiment. No factories: a run config names the
implementation class and its parameters.

| Component | Responsibility | Default |
|---|---|---|
| **World** | Draws the facts for a round (x, y, z, …). Holds truth. | Uniform on ℤ_k, resampled every round. |
| **Disclosure** | Decides which agents see which facts. | Group X sees x, group Y sees y, everyone sees common-ground facts (§4). |
| **Task** | The target as a function of facts. | d = x − y. |
| **Factor** | How an agent reads a fact. Private to the agent. | Gauge θ ∈ ℤ_k, resolution m dividing k: reading = (v + θ) mod m. |
| **Agent** | Holds readings and its own translation table g (its W′ of each neighbour). Writes messages, checks continuations, applies repairs. | Relay agent (§3). |
| **Watchdog** | Decides whether to check an incoming continuation, and against what. | Default-accept; checks with probability ι; compares at gcd of the two resolutions. |
| **Repair** | What a fired watchdog sends, and how the receiver updates g. | Two variants: *bare* (only "wrong") and *named* (the discrepancy δ). |
| **Topology** | Who can talk to whom. Static graph. | Two groups, dense inside, a few cut edges. |
| **Scheduler** | Which exchanges happen in which order in a round. Generates the event DAG. | Random edge order; optional scheduled triads. |
| **Tape** | Append-only event log. The only shared state. | One implementation, not polymorphic. |
| **Observer** | The experimenter. Reads tape plus truth, computes measures. | §5. |

Isolation is physical. Agents receive only Messages and their own readings.
They never hold a reference to World, Observer, the Tape as a whole, or another
agent. The Observer is the only component that sees truth.

Bots, hubs and alternative heterogeneity are new Agent or Factor
implementations, not changes to the core.

## 2. Data

All plain immutable records in `core/types.py`.

- `Fact(name, value)`: truth, held by World and Observer only.
- `Reading(agent, fact, value, resolution)`.
- `Message(src, dst, kind, value, round, parents)`. `kind` ∈ {fact name, "d"}.
  `value` is in the sender's frame. `parents` are the event ids this message
  depends on (self-parent, last received), giving the DAG.
- `Fire(checker, src, round, delta | None)`.
- `Repair(src, dst, delta | None)`.
- `Event`: tagged union of the above, plus `Arm`, `Expire`, with a sequence id.

## 3. Round loop

1. World draws facts. Observer logs truth.
2. Disclosure hands each agent the facts it sees. Factor turns them into
   readings.
3. Scheduler yields exchanges (src → dst). For each:
   - src writes a Message with its current value for a kind, in its own frame,
     and arms a watchdog.
   - dst translates with g[src] and continues: updates its belief for that
     kind, or derives d once it holds both operands.
   - dst's watchdog, if it checks (probability ι) and dst holds its own reading
     of that kind, compares at gcd(m_src, m_dst). On mismatch: Fire, then Repair
     back to src, then both update g per the Repair variant.
   - Path consistency: if dst already holds a belief for that kind from a
     different path and the two differ at its resolution, that also fires.
4. Unfired watchdogs expire after horizon h.
5. Each agent emits its estimate of d. Observer records.

## 4. Correction found while designing

With x disclosed only to X and y only to Y, nothing on either side can
calibrate the cross-cut translation. A relative gauge offset between the
groups is a pure coboundary: every check passes, every agent agrees, and
everyone's d is off by the same constant. So the task as first stated is
uncomputable, and the failure it produces is H⁰-type (wrong global section),
not H¹.

To make calibration possible at all, Disclosure must provide common ground. The
options are configurable:

- **Shared fact** z, seen by everyone, giving cross-cut edges something to check.
- **Brokers**: agents in both groups, seeing x and y.

Then two failures are measurable and distinct:

- **Offset** (H⁰-type): consistent, wrong d across the cut. Expected when common
  ground is too coarse for the cut edges' resolutions.
- **Holonomy** (H¹-type): d depends on the path that carried the operand.

## 5. Observer measures

Per round and over time:

- Edge error e_ij = g_ij − (θ_j − θ_i) mod k, split into the part visible at
  gcd(m_i, m_j) and the invisible remainder.
- Holonomy Σ e around each cycle in a cycle basis. Filled cycles (triads that
  exchanged this round) are reported separately from unfilled ones.
- Offset: the coboundary part of e across the cut.
- Correctness: fraction of agents whose d equals truth; agreement: fraction
  agreeing with the modal d. Silent wrong consensus is high agreement with low
  correctness.
- Traffic: fires, repairs, mean |δ|.

## 6. Experiments

- **E0, degenerate limit.** All m = k, shared fact on, named repair. Expect
  e → 0, holonomy 0, correctness 1. Failure is a bug.
- **E1, heterogeneity.** Mixed resolutions on cut edges. Expect nonzero
  invisible e, holonomy on unfilled cut-crossing cycles, high agreement and low
  correctness.
- **E2, triads.** Schedule triads on chosen cycles. Expect holonomy to move from
  unfilled to filled and then get repaired.
- **E3, hub.** One full-resolution agent adjacent to all. Expect holonomy and
  offset to collapse.
- **E4, bare versus named repair.** Same as E1. Expect bare repair to converge
  slower or to the wrong class.

## 7. Layout

```
smallworld/
  core/    types.py tape.py world.py disclosure.py task.py factor.py
           agent.py watchdog.py repair.py topology.py scheduler.py observer.py
  impl/    zk_world.py split_disclosure.py diff_task.py resolution_factor.py
           relay_agent.py default_watchdog.py repairs.py topologies.py
           schedulers.py zk_observer.py
  run.py   loads a config, wires components, runs, writes tape and measures
configs/   e0.toml … e4.toml
results/   one folder per run: tape.jsonl, measures.csv, config copy
tests/     E0 as a test
```

Python 3, standard library plus networkx for cycle bases.
