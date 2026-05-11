# SOP — Root Validation

**When to use**: every time a root is added, edited, or first imported into a
new chart. Goal: confirm the root fires when expected and ONLY when expected.

## Inputs

- A root canonical name, e.g. `heavy-pentagon::SAAB`.
- Its row in `docs/roots.md` (definition, parameters, defaults, source line range).
- The Pine source file the root lives in (per `bible-input/MANIFEST.md`).
- A test chart on TradingView with the indicator family loaded.
- The corresponding test indicator from Stage 2 (e.g. `ROOTS_VOLUME_TEST_v1.pine`)
  if the root has been included in the test rig.

## Procedure

### 1. Read the bible row

In `docs/roots.md`, find the row matching the canonical name. Note:
- **Family** (push, candle, rvol, fvg, hv, gzi, displacement, structural, oscillator, other)
- **Plain English** definition (one line)
- **Parameters & defaults** (e.g. `disp_strength=6.0`, `gziProximity=6`)
- **Offset** (commonly 0 or −1)
- **Pine source line range**

### 2. Open the canonical Pine source

Locate the line range cited. Confirm:
- The boolean assignment matches the plain-English definition.
- The parameter defaults match the `parameters:` section in the YAML.
- The plot/plotshape uses the offset cited.
- Any `barstate.isconfirmed` gate is present (every root must be `conf`-gated).

### 3. Load on chart

In TradingView, add the canonical indicator (or the Stage-2 test indicator that
includes this root). Confirm the plot title shows the canonical name:
`<provenance>::<root>`. If the test indicator uses a generic name, that's a bug
in the test indicator — fix Stage 2.

### 4. Pick three reference bars

Choose three historical bars where the root SHOULD fire (per its definition):
- One obvious case (clearly meets all criteria).
- One borderline case (meets thresholds by ~5%).
- One that should NOT fire (close to threshold but below).

For each: zoom to that bar, hover, confirm the plot's mark is present (or
absent) on the correct bar. Account for the offset:
- `offset=0` → mark on the bar that triggered.
- `offset=-1` → mark on the bar BEFORE the triggering bar.

### 5. Compare against alert

If the root has an `alertcondition()`, set up an alert. Wait for a fire (or
replay a historical bar with TradingView's bar-replay tool). Confirm the alert
fires at the close of the bar where the boolean evaluated true — regardless of
the plot's offset.

### 6. Cross-indicator parity

If the same root name appears in multiple indicators (per `docs/redundancy.md`),
load both indicators on the same chart. Confirm the plots fire on the same
bars. Any mismatch = drift; jump to `drift-triage.md`.

### 7. Log

Append to `docs/validation-log/<YYYY-MM-DD>-roots.md`:

```markdown
### <provenance>::<root> — verified <YYYY-MM-DD>

- Chart: <symbol> <timeframe>
- Reference bars: 
  - <bar 1 timestamp>: ✅ fired as expected
  - <bar 2 timestamp>: ✅ fired as expected (borderline)
  - <bar 3 timestamp>: ✅ correctly did NOT fire
- Alert: ✅ fired at correct bar close
- Cross-indicator parity (if applicable): ✅ <other-indicator>::<root> fires on same bars
- Notes: <anything unusual>
```

Then update the root's row in `data/indicators.yaml` with a `verified_on`
field and re-run the generators. Commit + push.

## Failure modes

| Symptom | Likely cause | Next SOP |
|---|---|---|
| Plot doesn't appear on expected bar | Boolean evaluates false → check parameters in YAML vs source. | This SOP, step 2-3 |
| Plot appears one bar earlier/later | Offset mismatch | `offset-triage.md` |
| Plot appears in canonical indicator but not test indicator | Test indicator copied threshold wrong | Fix Stage-2 test indicator |
| Plot in indicator A fires but not in indicator B | Internal-implementation drift | `drift-triage.md` |
| Alert doesn't fire | Missing `alertcondition()` or chart auto-saves disabled | Pine source check |

## Time budget

A focused root validation takes 5-10 minutes per root. Doing the entire
RVOL family (10 roots) in one sitting is realistic.

## Outputs

- One `docs/validation-log/<date>-roots.md` entry per root validated.
- (Optional) `verified_on:` field added to the root in `data/indicators.yaml`.
- A clean PR at the end of the day if any drift was found and fixed.
