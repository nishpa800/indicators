# Stage 3 — TradingView Verification (Anish-driven)

**Goal**: visually confirm every root in the Stage-2 test indicators fires when
expected. Outputs daily validation logs that update the bible.

## Preconditions

Before running Stage 3, the following must be in place:

### 1. PR #2 reviewed

The Stage-1 bible PR is open as draft. Review (or at least skim) the
following before validating roots, so you know what they should look like:

- `INDICATORS_INDEX.md` — entry point
- `docs/roots.md` — every root, by family
- `docs/composites.md` — every composite, by indicator + tier
- `docs/redundancy.md` — known drift candidates
- `docs/glossary.md` — definitions
- `docs/sop/root-validation.md` — the procedure you'll be running

### 2. Stage-2 test indicators loaded on TradingView

Open TradingView, log in, and add the four test indicators:

- `test-indicators/versions/ROOTS_VOLUME_TEST_v1.pine`
- `test-indicators/versions/ROOTS_HVGZIFVG_TEST_v1.pine`
- `test-indicators/versions/ROOTS_CANDLE_TEST_v1.pine`
- `test-indicators/versions/ROOTS_FAUNA_TEST_v1.pine`

For each, also load the corresponding canonical from `bible-input/MANIFEST.md`
on the same chart. Set them to the same colour scheme (so plots that should
align are visually obvious if they don't).

### 3. Reference symbols

Pick at least 3 reference symbols + timeframes for breadth:

| Symbol      | Timeframe | Purpose                                                        |
|-------------|-----------|----------------------------------------------------------------|
| ES1!        | 5m        | Liquid futures; lots of normalised-price spikes for RVOL roots |
| AAPL        | 15m       | Equity with PBJ-friendly Zoo MA pullbacks                      |
| BTCUSD      | 1h        | High-vol crypto; FVG / GZI / HV displacement events            |

Pick a 2-3 month historical window for each. Use TradingView's bar-replay if
you want to step through bar-by-bar.

### 4. TradingView MCP (optional but recommended)

If Anish has the TradingView MCP connected to this Claude Code session, the
test indicator plots can be queried programmatically. Otherwise, validation
is fully visual + manual.

## Procedure (per root family)

For each test indicator, work through the roots one at a time:

1. **Open the test indicator's source** (in this repo) and find the root's
   plotshape declaration. Note the canonical name and offset.
2. **Open the corresponding canonical's source** and find the original plot.
   Note any differences (shape, colour, location — the booleans should be
   identical per the verbatim-copy strategy).
3. **On the chart**, find 3 bars where the root SHOULD fire (per its
   plain-English definition in `docs/roots.md`):
   - One obvious case
   - One borderline case
   - One that should NOT fire (close to threshold but below)
4. **For each bar**, confirm:
   - Test plot's marker is on the expected bar (account for offset).
   - Canonical's marker is on the same bar.
   - Both appear simultaneously (they should — same boolean).
5. **Log the result** in `docs/validation-log/<YYYY-MM-DD>-roots.md` (one
   section per root).
6. **If drift found** (test fires but canonical doesn't, or vice versa),
   immediately drop into `docs/sop/drift-triage.md`.

## What to log per root

```markdown
### <provenance>::<root> — verified <YYYY-MM-DD>

- Symbol: <e.g. ES1!>  Timeframe: <e.g. 5m>
- Reference bars:
  - <YYYY-MM-DD HH:MM>: ✅ fired in test AND canonical (obvious case)
  - <YYYY-MM-DD HH:MM>: ✅ fired in both (borderline)
  - <YYYY-MM-DD HH:MM>: ✅ correctly NOT fired in either
- Alert: ✅ fired at correct bar close
- Cross-canonical parity: ✅ identical bar-for-bar across <N> reference bars
- Notes: <anything unusual>
```

## What to log per drift

If you find a root that fires in test but not canonical (or vice versa):

```markdown
### <provenance>::<root> — DRIFT FOUND <YYYY-MM-DD>

- Symbol/timeframe: <...>
- Affected bar(s): <timestamps>
- Test fired: <yes/no>
- Canonical fired: <yes/no>
- Hypothesis: <e.g. test indicator missed an internal helper assignment>
- Diff: <paste the differing Pine lines>
- Action: <update test indicator OR update YAML extraction>
```

Then update either `data/indicators.yaml` (if extraction was wrong) or the
test indicator (if copy was wrong), re-run generators, commit.

## Stage 3 success criteria

- Every root in the 4 test indicators has at least one validated entry in
  `docs/validation-log/`.
- Any drift found is logged + fixed (either in YAML or test indicator).
- The PR (currently draft #2) gets a follow-up commit with the validation
  logs and any corrective changes.

## Time budget

Per root: 5-10 minutes (3 reference bars + log).
Per test indicator: 30-90 minutes (depending on root count).
Full Stage 3 sweep: 4-6 hours.

## What Stage 3 enables

Once roots are validated, Stage 4 begins: confirm every top-level composite
in `docs/lineage/` fires when its inventory roots align. Stage 4 reuses the
same chart setup and the same symbols.

## Hand-off back to Claude

After validating each root family on TradingView, paste the validation log
text into this Claude Code session. Claude will:

1. Save the log to `docs/validation-log/<date>-<family>.md`
2. Update `data/indicators.yaml` to mark each root with its
   `verified_on:` field
3. Re-run generators (`tools/merge_extracts.py`, `tools/build_docs.py`,
   `tools/build_lineage_cards.py`)
4. Commit the updates
5. Move to the next root family or to Stage 4
