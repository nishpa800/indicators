# VOB GPS Four-Satellite Architecture

_Authored 2026-05-11. **Status: deferred future work** — flagged by Anish
2026-05-11 but not yet built. This doc captures the design so it isn't
lost between now and Stage 7+ when it gets built._

> Anish 2026-05-11: "We aren't there yet, but we do need to update the
> approach that we're taking on the VOB because I have a really good
> idea about that."

## The two VOB indicators we have

1. **`vob-single-sens`** — one VOB with a SINGULAR sensitivity setting,
   plus 3-buy + 3-sell companion detection plots. 6 companions total.
2. **`vob-asym`** — VOB with SIX sensitivity levels and 6 zones. The
   PBJ engine and TNT-OD are wrapped into this one (per the earlier
   bible).

## What was missing

> Anish: "One thing we did not do is we did not involve the HV+FVG GZ
> one original engine. The whole purpose of that was to determine when
> there's zones of, like, amazingness."

`hv-fvg-gz1-og` defines HV / FVG / GZI canonical roots and EMITS ZONES.
Those zones are the "amazingness zones" — areas of structurally elevated
probability for trade-relevant action. They were not previously connected
to the VOB layer.

## The GPS analogy

Anish:

> "I view those as, like, three to four, like, satellites... my thesis
> is very simple. If we can get really good at emitting that a zone or
> the lines, that the lines are being drawn, the better we get at that.
> Remember, we have four satellites for GPS, and they... they're all...
> if we can see them all, and we know what the speed of light is. And
> in this situation, the speed of light, in my opinion, is, like... it's
> not the same thing, but maybe there's a magic ratio or formula for
> those sensitivities. And if we can get those right and we can
> triangulate them..."

GPS needs 4 satellites to triangulate a position in 3D + time. This
architecture has 4 trading "satellites":

| Satellite | Source | Emits | Sensitivity tunable |
|---|---|---|---|
| Sat 1 | `hv-fvg-gz1-og` | "Amazingness" zones (HV+FVG+GZI confluence) | yes (lookbacks + thresholds) |
| Sat 2 | `vob-single-sens` | One VOB level + 3 buy + 3 sell companions | one sensitivity dial |
| Sat 3 | `vob-asym` at sensitivity threshold A | 6-layer VOB read at threshold A | tunable |
| Sat 4 | `vob-asym` at sensitivity threshold B | 6-layer VOB read at threshold B | tunable |

The "speed of light" in Anish's analogy is the magic ratio between
sensitivities. There is probably an optimal pair of (A, B) for sat 3+4
that maximizes triangulation quality. Empirical search required —
flagged as Stage 7 work.

## Triangulation = high conviction

When all 4 satellites agree on direction at the same bar, the
conviction is exceptional. Anish's worked example:

> "If you have a back-to-back napalm that's bearish and you had a
> HV+FVG GZ1 zone on top of another zone that's bearish, and then you
> had a PPD with an RVOL 1x and a PBJ that's bearish, and you had a
> Zone-F on both of your VOBs that's bearish — dude, that's a fucking
> buy-a-put-call, like, tomorrow."

Decoded:

- B2B Napalm bearish → primary detection plot
- HV+FVG GZ1 zone-on-zone bearish → Sat 1 confluence
- PPD + RVOL1x + PBJ bearish → primary detection plot stack
- Zone-F on both VOBs bearish → Sat 2 + Sat 3 + Sat 4 confluence (all
  three VOB views agree at "Zone F" sensitivity)

= 4-satellite convergence + 2 high-conviction primary plots = highest
conviction signal in the system.

## How the 4-satellite read enters the dialectic

When a Plot Owner runs a per-fire dialectic via `bull-bear-dialectic`,
the situational-context-share skill (TBD) injects the 4-satellite read
for the firing bar:

```
4-satellite snapshot at fire bar (TSLA 5m 2026-05-11T14:30):
  Sat 1 (HV+FVG GZ1): bear zone present, stacked on prior bear zone
  Sat 2 (vob-single-sens): Zone F bear (companion 4-of-6)
  Sat 3 (vob-asym sens A): Zone F bear at threshold A
  Sat 4 (vob-asym sens B): Zone F bear at threshold B
  Triangulation: 4/4 agree bear → high conviction
```

The bull-case agent reads this and must construct its case AGAINST the
4-satellite bear read (very hard but mandatory — the bear-case might
still be wrong; the dialectic must consider it). The bear-case agent
reads this and incorporates as supporting evidence.

## Why this is deferred

1. The two VOB indicators exist but the bible has not yet locked their
   canonical sensitivity threshold pair (A, B). That requires
   empirical research.
2. The HV+FVG GZ1 zone emission needs to be reformulated as a
   bar-tagged stream (not just a visual zone) so it can enter the
   dialectic's structured-context packet.
3. The triangulation skill itself (`four-satellite-triangulator`) is
   not yet authored. It belongs in the grunt-worker tier — a
   tabulation skill.
4. The per-fire dialectic doesn't yet have the
   situational-context-share infrastructure to consume the
   4-satellite snapshot.

All of these are pre-requisites; none ship today.

## What ships when this is built (Stage 7+)

| Artifact | Location |
|---|---|
| `four-satellite-triangulator` skill | `.claude/skills/four-satellite-triangulator/` |
| Sat-1 zone emission spec | `docs/agentic-os/satellites/sat1-hv-fvg-gz1.md` |
| Sat-2 emission spec | `docs/agentic-os/satellites/sat2-vob-single-sens.md` |
| Sat-3+4 emission specs | `docs/agentic-os/satellites/sat3-4-vob-asym-pair.md` |
| Empirically-tuned (A, B) sensitivity pair | `data/four-satellite-config.yaml` |
| Triangulation log per Plot Owner | `docs/agentic-os/triangulations/<plot>/<date>.md` |

## Stage-7 followups (deferred work, queued for after first Plot Owner ships)

- [ ] Empirical search for the optimal (sat-3-sensitivity, sat-4-sensitivity) pair
  that maximizes triangulation predictive value
- [ ] Reformulate `hv-fvg-gz1-og` zone emission as a bar-tagged boolean
  stream (currently visual-only)
- [ ] Author `four-satellite-triangulator` grunt-worker skill
- [ ] Wire `four-satellite-triangulator` into `situational-context-share`
- [ ] Backtest: 4/4 triangulation agreement vs 3/4 vs 2/4 — predictive
  value curve
- [ ] If predictive value scales with agreement count, add a
  "satellite-convergence" feature to the per-fire payload schema (SD-007
  successor)

## Why the GPS analogy is the right one

GPS works because the 4 satellites are INDEPENDENTLY-DERIVED estimates
of the same underlying truth (your position). When they agree, the
agreement is informative because the satellites have NO SHARED ERROR
SOURCES.

Same here: HV+FVG+GZ1, vob-single-sens, vob-asym at threshold A, vob-asym
at threshold B all read the same market bar but THROUGH DIFFERENT
LENSES (different volume metrics, different zone constructions, different
sensitivity thresholds). When they agree, the agreement is informative
because the lenses don't share error sources.

If two of them shared an error source — say sat-3 and sat-4 are the same
indicator at different sensitivities — they're partially correlated. The
"magic ratio" Anish refers to is the sensitivity gap (A vs B) at which
sat-3 and sat-4 are MAXIMALLY DECORRELATED while still both reading the
same market bar. That's the empirical search.
