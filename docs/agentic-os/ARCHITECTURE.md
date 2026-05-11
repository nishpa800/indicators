# Agentic Operating System — Architecture

_Authored 2026-05-11. Foundational doc; supersedes ad-hoc agent dispatch._

This is the operating system for how Claude Code agents are dispatched, owned,
and coordinated for the indicators bible. It replaces "spin up an agent when I
need one" with a durable ownership model where every important signal has a
dedicated agent (chat thread) responsible for it.

---

## North star — Anish's vision, in his own words

> "I wanna have an agentic operating system, and I basically want us to hire
> an agent who's responsible for each indicator study and potentially just
> responsible for one detection plot if it's important. Unified combo is so
> important to our strategy that we want an agent that is dedicated full time
> to unified combo."

> "We probably wanna have somebody — an agent who's responsible for back to
> back PUP. And PPD. These things really go hand in hand."

> "I want us to have an agent who's responsible for bullish and an agent who's
> responsible for bearish. Anytime that we get data coming in about a bullish
> unified combination, the bearish unified combination is going to basically
> try to make the devil's advocate case that it's really not an angel. It's
> not bullish. It is really led the devil's spawn."

> "It'll be great if we could have both of the sort of good and evil debating.
> And then at the end of the day, in real time, we should be getting scores
> on this — how sure are we that this bearish is bearish? How sure are we
> that this bearish is bullish? It's just a matrix of four squares in every
> single detection plot."

> "Recognizing when a bearish unified combo is actually the order block, and
> it is the incarnate from God who came to us to send us higher, is almost
> the most magical trait you'll ever have in your life."

---

## Three roles (the operating system's primitives)

| Role | Who they own | How many | Lifetime |
|---|---|---|---|
| **Indicator Owner** | One indicator study (Pine file family) | 2 per family (bull + bear) | Long-lived chat thread |
| **Plot Owner** | One especially-important detection plot | 1 per special plot (handles bull + bear internally) | Long-lived chat thread |
| **Task Worker** | One bounded task (audit, port, drift triage, TV firing) | Many, short-lived | Per-task subagent dispatch |

Indicator Owners and Plot Owners are PERSISTENT — a chat thread that the
human (or a parent agent) returns to whenever that indicator/plot has news.
Task Workers are EPHEMERAL — spawned for one job, return a report, die.

A Plot Owner outranks an Indicator Owner when their scopes overlap. Example:
Unified Combo lives inside Squarify + HVDPBJPPD + others; its Plot Owner
overrides individual Indicator Owners' opinions when canonical questions
about Unified Combo come up.

---

## Tier-A — Indicator Owners (every indicator study)

**Rule**: every indicator family gets 2 dedicated Indicator Owners — one
bullish, one bearish. They are split so each can specialize on the
direction-specific operands (PBJ vs PB, FAUNA bull vs bear, RVOL1x bull
vs MOAB, etc.) and so the bull-vs-bear debate is built into the org chart
by construction.

**Roster (first wave)** — 12 indicator families × 2 = 24 Indicator Owners:

| Indicator family | Bull Owner | Bear Owner |
|---|---|---|
| squarify | `IO::squarify::bull` | `IO::squarify::bear` |
| hvd-pbj-ppd | `IO::hvd-pbj-ppd::bull` | `IO::hvd-pbj-ppd::bear` |
| b2b-pup | `IO::b2b-pup::bull` | `IO::b2b-pup::bear` |
| tnt-od | `IO::tnt-od::bull` | `IO::tnt-od::bear` |
| ultra-combo | `IO::ultra-combo::bull` | `IO::ultra-combo::bear` |
| heavy-pentagon | `IO::heavy-pentagon::bull` | `IO::heavy-pentagon::bear` |
| heavy-combo-toggles | `IO::heavy-combo-toggles::bull` | `IO::heavy-combo-toggles::bear` |
| hv-fvg-gz1-og | `IO::hv-fvg-gz1-og::bull` | `IO::hv-fvg-gz1-og::bear` |
| proximity-gzi-hv | `IO::proximity-gzi-hv::bull` | `IO::proximity-gzi-hv::bear` |
| anish-50-1st-combo | `IO::anish-50-1st-combo::bull` | `IO::anish-50-1st-combo::bear` |
| vob-asym | `IO::vob-asym::bull` | `IO::vob-asym::bear` |
| vob-ladder-watch | `IO::vob-ladder-watch::bull` | `IO::vob-ladder-watch::bear` |

(Newer families like fauna-shifu, e3-f2-cluster, hv-ladder, heavy-uncap,
heavy-weapons, anish-tb-foster, disp-4x, pb-pbj, vob-single-sens, yin-yang
get added in wave 2.)

### What an Indicator Owner owns

- The Pine source for their indicator family (read-only — they don't edit;
  they request edits via Task Workers)
- The bible YAML extract for that family (`bible-input/extract-<family>.yaml`)
- The drift findings for that family (`docs/redundancy.md` rows tagged for
  this family)
- The validation reports for that family (`docs/validation/*-<family>.md`)
- The Python port for that family (`python_ports/<family>/*.py`)
- The lineage cards rooted in this family's plots (`docs/lineage/`)
- A persistent memory note: `docs/agentic-os/memory/IO__<family>__<dir>.md`

### What an Indicator Owner does

1. **Triage**: when news arrives (drift report, TV firing result, port update,
   bug suspicion), classify it: is it about a root, a composite, an internal
   helper, an offset, an IPSF default? Route appropriately.
2. **Direction-specific scrutiny**: as the bull owner, you scrutinize every
   bull-fire from your family. As the bear owner, you scrutinize every
   bear-fire. You also play devil's advocate on the OPPOSITE direction —
   when a bull-fire comes through, the bear owner asks "is this actually a
   bull trap?"
3. **Hand off cross-family questions**: a Plot Owner exists for a reason. If
   the question is "is csNew3 same-bar AND or lagged AND across all
   families?", hand to `PO::unified-combo::*`.
4. **Author drift entries**: when you find drift inside your family's history,
   author the row in `docs/redundancy.md`.
5. **Maintain the family-level confidence calibration**: track over time how
   often this family's bull-fires actually predict bull moves (and same for
   bear). Output: `docs/agentic-os/calibration/<family>.md`.

---

## Tier-B — Plot Owners (special, cross-family detection plots)

**Rule**: a Plot Owner is hired for any detection plot that (a) appears in
multiple indicator families, (b) is load-bearing for trading strategy, or
(c) has been the subject of a drift finding that revealed >1 distinct
semantic group across files.

**First-wave hires** (the only ones approved today):

| Plot Owner | Scope | Why hired |
|---|---|---|
| `PO::unified-combo` | csNew3_Bull + csNew3_Bear across all families | Anish: "so important to our strategy"; 7-vs-1 semantic drift found in validation |
| `PO::b2b-pup` | det_b2bPUP + det_b2bPPD across all families | Anish: "these things really go hand in hand"; feeds 20+ S-plots |
| `PO::fvg-combo` | csNew2_Bull + csNew2_Bear across all families | Constituent of unified-combo; carries CS1-CS4 sub-tree |
| `PO::matrix-combo` | csNew1_Bull + csNew1_Bear across all families | Constituent of unified-combo; Trinity-vs-Neo ambiguity still open |

(Future Plot Owners: SUPER family, Combo Chain, FLOOR/2F/ROOF/PENT, ALPHA STRIKE,
NAGASAKI PLUS, Heavy Combos — each only after a drift finding justifies dedicated
ownership.)

### Why Plot Owners own BOTH bull and bear (not split)

For Indicator Owners we split bull/bear into two separate chat threads
because the indicator family is large enough that the operand surface area
is direction-specific and the threads can each go deep.

For Plot Owners we DO NOT split. The reason: the bull-vs-bear debate for
a single plot is the central activity of a Plot Owner. Putting both sides
into the same chat thread means the debate can happen WITHIN ONE CONTEXT
— the agent literally writes the angel argument and the devil argument in
the same response and computes the 4-square confidence matrix in one
operation.

A split Plot Owner would force a cross-thread protocol for every debate —
slow and stateful. A unified Plot Owner debates internally on demand.

### What a Plot Owner owns

- The canonical definition of their plot (per the `docs/agentic-os/canonical/` directory)
- The list of every Pine file where their plot is defined (with line numbers)
- The 2×2 confidence matrix for every fire (see "Heaven vs Hell" below)
- A persistent memory note: `docs/agentic-os/memory/PO__<plot>.md`
- A debate log: `docs/agentic-os/debates/<plot>/<date>-<fire-id>.md`

### What a Plot Owner does

1. **Canonical curation**: own and update the canonical definition of the plot.
   "Canonical" means: the definition we will use in our Python ports and the
   one we will reconcile every Pine variant against.
2. **Inclusion-decision authority**: when a definition variant adds or removes
   an operand (e.g. Pentagon-included vs Pentagon-excluded), the Plot Owner
   decides whether canonical = include or exclude. Today's standing decision:
   **always include Pentagon** (see `STANDING_DECISIONS.md`).
3. **Debate orchestration**: when a fire comes through the system, run the
   Heaven-vs-Hell debate (next section) and emit the 4-square matrix.
4. **Predictive-value tracking**: keep a rolling record of fire → outcome,
   sliced by bull-fire-then-actual-bull, bull-fire-then-actual-bear, etc.
   This feeds the long-run calibration of the matrix.
5. **Drift escalation**: when a new drift instance is found by an Indicator
   Owner, the Plot Owner either canonicalizes the new variant (writes a new
   versioned Python port) or rules it noise (documents and ignores).

---

## The Heaven-vs-Hell debate protocol

> Anish: "I want for every single detection plot that we deem extremely
> important. … recognizing when a bearish unified combo is actually the
> order block, and it is the incarnate from God who came to us to send us
> higher, is almost the most magical trait you'll ever have in your life."

The debate is the central activity of a Plot Owner. It runs whenever a
fire of the owned plot occurs (real-time stream) or whenever a historical
fire is re-evaluated (back-test).

### The 4-square confidence matrix

|                   | ACTUAL DIRECTION = BULL | ACTUAL DIRECTION = BEAR |
|-------------------|---|---|
| **PLOT FIRED BULL** | `P(true_angel)` — bull-fire that's really bullish | `P(devil_dressed_as_angel)` — bull-fire that's a trap |
| **PLOT FIRED BEAR** | `P(angel_dressed_as_devil)` — bear-fire that's the divine reversal | `P(true_devil)` — bear-fire that's really bearish |

Every fire receives 4 probabilities summing to 1.0 (within row — i.e. the
two cells of the firing row, conditioned on the firing direction).

**Per-fire payload** (what the Plot Owner outputs):

```yaml
fire_id: <symbol>-<tf>-<bar_ts>-<plot>-<direction>
plot: csNew3
direction_fired: bull
context:
  symbol: <ticker>
  tf: <timeframe>
  bar_ts: <iso>
  preceding_5_bars: [...]
  concurrent_plots_firing: [<list>]
debate:
  angel_case:
    summary: <one paragraph>
    supporting_facts: [<list>]
    confidence: 0.72
  devil_case:
    summary: <one paragraph>  # the bear/devil side's case that this bull-fire is a trap
    supporting_facts: [<list>]
    confidence: 0.28
matrix:
  P_true_angel: 0.72
  P_devil_dressed_as_angel: 0.28
  P_angel_dressed_as_devil: null   # null because this fire was bull, not bear
  P_true_devil: null
notes: <free-form one paragraph from the Plot Owner>
```

Note: when the fire is bull, only the top row of the matrix is populated.
When bear, only the bottom row. The MATRIX BUILDS UP over many fires —
across all fires it converges to the 4-square long-run calibration table.

### Debate procedure (Plot Owner runs this on every fire)

1. **Collect evidence**: pull the bar context, preceding 5 bars, concurrent
   plot fires, the operands' raw values (per IPSF settings currently
   active).
2. **Angel case (direction-of-fire)**: write the case that the fire is
   "true". Cite supporting facts: which operands aligned, how strongly, what
   confluence is present, what historical analogues exist.
3. **Devil case (opposite-of-fire)**: write the case that the fire is a
   trap. Cite supporting facts: which contradicting plots are also firing,
   what historical examples of this exact pattern produced the opposite
   outcome, what hidden gates would have suppressed this fire if active.
4. **Adjudicate**: score angel-confidence and devil-confidence in [0, 1]
   summing to 1.0 within the row. Use prior calibration if available.
5. **Emit the payload** above.
6. **Append to debate log**: `docs/agentic-os/debates/<plot>/<date>-<fire-id>.md`.

### What "magical" looks like (Anish's term)

When `P_angel_dressed_as_devil` is high for a bear-fire — that's the case
where the Plot Owner is calling "this bear-fire is actually a divine
reversal; ignore the bear signal and lean bull". Conversely, high
`P_devil_dressed_as_angel` for a bull-fire = "bull trap; don't take it".

The long-run goal: a calibration table where high values in the
off-diagonal cells (`P_devil_dressed_as_angel`, `P_angel_dressed_as_devil`)
are RARE — most fires are true to direction — but when they DO score high,
they're correct. That's the "magical trait" Anish describes.

### Devil's-advocate independence (critical)

For Indicator Owners (Tier A), the bull and bear are SEPARATE agents in
SEPARATE chat threads. This means when `IO::squarify::bull` sees a bull-fire
and the question "is this a trap?" arises, the answer comes from
`IO::squarify::bear` — a different agent with its own reasoning context,
not a self-debate inside the bull agent's head. This is the structural
guarantee that the devil's advocate isn't just rubber-stamping the angel.

For Plot Owners (Tier B), the bull-and-bear-in-one-context model works
because the agent is forced to write BOTH cases explicitly in the same
response. The discipline is enforced by the debate-procedure schema (steps
2 and 3 above are non-optional).

---

## Standing decisions (canonical rules)

These are the canonical decisions that ALL agents inherit. New decisions
are added to `STANDING_DECISIONS.md`; they NEVER overwrite — only append.

### SD-001: Always include Pentagon

Per Anish 2026-05-11: when a detection plot has an inclusion variant for
Pentagon (i.e. one Pine file's definition includes the Pentagon operand
and another's excludes), the canonical definition is the INCLUDES variant.
This applies to the FVG Combo and Matrix Combo families and any other
plot where Pentagon could be an operand.

Acknowledgment: we acknowledge other variants exist and we do NOT modify
them in their original Pine files. The canonical Python port reflects
INCLUDE. The variant-without-Pentagon stays in the Pine source as-is for
historical traceability.

### SD-002: Never modify, always new-version

Per Anish (standing): when updating a Python port to reflect a canonical
decision or new finding, we do NOT modify the existing port file. We
create a new versioned file with a clear name (e.g.
`python_ports/squarify/squarify_46_v2_canonical_pentagon_included.py`)
and update a `LATEST.txt` pointer.

### SD-003: IPSF defaults do not matter

Per Anish (standing): `input.int/float/bool/string` default differences
across .pine files are NOT drift. They are user-tunable. Do NOT flag them
in audits, drift tables, or Plot Owner debates. ONLY flag values that are
HARDCODED in the .pine source (e.g. `>= 6.0` baked into the math).

### SD-004: No file deletion ever

Per Anish (standing): the only hard restriction across the entire
agentic-OS is "no DELETE files." Renames, moves, overwrites with new
content — all also forbidden. Every change is a new versioned file.

---

## Skills that codify the OS

### `.claude/skills/bull-vs-bear-debate/`

Generic skill that any Plot Owner invokes to run the Heaven-vs-Hell
debate on a single fire. Takes plot id + fire context + IPSF setting
snapshot; emits the 4-square payload. Codifies steps 1-6 above as
mechanical procedure.

### `.claude/skills/detection-plot-validation/`

(Already exists.) Owns the bible's Stage 4 validation — used by Indicator
Owners when a drift report comes in.

### `.claude/skills/detection-plot-tv-firing/`

(Already exists.) Owns Path A (chart-side) TV firing — used by Plot
Owners when they need fire-bar truth for calibration.

### Future skills (deferred — not built today)

- `.claude/skills/plot-owner-onboarding/` — when a new Plot Owner is hired,
  this skill auto-generates the memory file, debate log directory, canonical
  doc skeleton.
- `.claude/skills/indicator-owner-handoff/` — for cross-thread handoffs
  between bull and bear Indicator Owners.
- `.claude/skills/calibration-rollup/` — runs nightly, aggregates per-fire
  debate logs into the long-run calibration table per Plot Owner.

---

## How agents are invoked in practice

Anish runs Claude Code on his Mac. A "chat thread" maps to a
`/conversation` or a session in Claude Code. The Indicator Owners and
Plot Owners aren't OS processes — they're CONVERSATIONAL THREADS the
human (or the parent coordinating agent) returns to.

Practical invocation:

- **Open an existing thread**: `claude` with `--session <thread-id>` (or
  click the saved conversation). The agent's memory loads from
  `docs/agentic-os/memory/<role>__<name>.md`; the thread's context is
  whatever Claude Code preserves.
- **Hire a new agent**: spawn a new Claude Code thread with a system
  prompt scaffold from `docs/agentic-os/templates/<role>-system-prompt.md`
  (TBD — to be authored when first agent is hired).
- **Cross-thread protocol**: agents leave messages for each other by
  writing to `docs/agentic-os/messages/<from>__to__<to>__<ts>.md`. The
  recipient's next invocation picks up its inbox via skill
  `agentic-os-inbox-check` (TBD).

The simpler interim: today's parent agent (the one you're talking to)
dispatches Task Workers via the `Agent` tool for bounded jobs. Indicator
Owner / Plot Owner threads are spun up explicitly by Anish or by the
parent agent when needed, with the system-prompt scaffold from the
templates directory.

---

## First-wave hiring plan (what to spin up next)

Priority order — Anish to confirm which to spin up first:

1. `PO::unified-combo` — hire FIRST. Anish: "agent that is dedicated full
   time to unified combo".
2. `PO::b2b-pup` — hire SECOND. Anish: "we probably wanna have somebody, an
   agent who's responsible for back to back PUP".
3. `IO::hvd-pbj-ppd::bull` + `IO::hvd-pbj-ppd::bear` — hire THIRD (the
   4-agent audit currently running in the background outputs the
   onboarding material for these two).
4. `PO::fvg-combo` + `PO::matrix-combo` — hire FOURTH (the enumeration
   agent currently running outputs their canonical doc).
5. `IO::squarify::bull` + `IO::squarify::bear` — hire FIFTH (Squarify is
   the largest indicator and the most cross-referenced).

(The remaining 18 Indicator Owners get queued for wave 2 after the first 5
prove the model.)

---

## What's NOT in scope today

- Building the cross-thread messaging system (TBD)
- The nightly calibration rollup skill (TBD)
- The Plot Owner onboarding skill (TBD)
- Memory file templates for each role (TBD)
- Auto-discovery of new fires from the Path M pipeline (TBD)
- Wiring debate-log emission into the realtime pipeline (TBD)

These are the agentic-OS's eventual production form. Today's deliverables
are the ARCHITECTURE doc (this file), the bull-vs-bear-debate SKILL
scaffold, and the canonical inclusion decision (SD-001: always include
Pentagon).
