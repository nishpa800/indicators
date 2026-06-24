# HV ROLLING CLUSTERS NRA — Changelog

## v1 (2026-06-23)
First release. Rebuild of `HV(50/150/250/500/1K/HEV/HS) NRA` that REPLACES the
per-tier single-bar markers and per-tier alerts with **10 rolling-window cluster
detectors**. The individual volume tiers are still computed (they are the raw
material the windows count) but no longer have their own visual plots or alerts.

### The 10 rolling windows
Each window fires when at least `COUNT` events of its class land within the last
`BARS` bars. Both `COUNT` and `BARS` are user inputs on every window.

| # | Window | Class counted | Event expression |
|---|--------|---------------|------------------|
| W1 | Nagasaki | all-time-high volume (= HEV) | `isHEV` |
| W2 | 1000+ | 1000-bar high or rarer | `is1000Bar` |
| W3 | 500 or greater | 500 / 1000 / all-time | `is500Bar` |
| W4 | 500 only | 500-bar high, not 1000+ | `is500Bar and not is1000Bar` |
| W5 | 250 or 500 | exactly 250 or 500 | `is250Bar and not is1000Bar` |
| W6 | 250 only | 250-bar high, not 500+ | `is250Bar and not is500Bar` |
| W7 | 150 or 250 | exactly 150 or 250 | `is150Bar and not is500Bar` |
| W8 | 150 only | 150-bar high, not 250+ | `is150Bar and not is250Bar` |
| W9 | 50 or above | any HV tier | `is50Bar` |
| W10 | 50 only | 50-bar high, not 150+ | `is50Bar and not is150Bar` |

Nesting (`isHEV -> is1000Bar -> is500Bar -> is250Bar -> is150Bar -> is50Bar`) is
why "or greater" uses the raw tier flag and "only" / "A or B" subtract the higher
tier — the exact priority logic of the original.

### Nagasaki definition
Nagasaki = the Heavy Weapons "Nagasaki" signal = all-time-high volume, the
identical running-max test as the HV indicator's HEV. Confirmed against
`heavy-weapons-nra/versions/HEAVY_WEAPONS_NRA_v1_2026-06-04.pine` and
`nova-volume/DEFINITIONS_HV_NAGASAKI.md` ("Nagasaki ≡ HEV").

### Architecture
- **Constitutional rolling windows:** each window is a true SLIDING trailing-N
  count via the canonical `f_sum_true()` helper, base event gated on
  `barstate.isconfirmed`. No anchored "wait N bars" windows (passes
  `check_no_fixed_windows.sh`).
- **Leading-edge fire:** `cond and not cond[1]` — fires once when the cluster
  completes, then re-arms automatically.
- **NRA non-repaint:** tiers compare the prior closed bar
  (`volume[1] == ta.highest(volume,N)[1]`); markers plot with `offset=-1`.
- **1:1 plot/alert parity:** every plot and its alertcondition share one boolean.
- **Alerts:** 10 per-window alertconditions + 1 "ANY" alertcondition + 1 `alert()`
  function call (the "any-call") so a single TradingView alert set to
  "Any alert() function call" catches every window, with a payload naming which
  windows fired.
- **Exactly 10 plots, nothing else:** only the 10 detection `plotshape()` markers.
  NO numeric/count/debug `plot()` lines (they clutter the Style tab). Internal
  aggregates (`n1..n10`, `activeWindows`) are UNPLOTTED export variables only.
- **Tick-safe by construction:** no `tv_ta`/`relativeVolume`, no
  `timeframe.in_seconds`, so no RE10023 risk. Pure ASCII source.

### Default thresholds (starting points — tune per symbol/timeframe)
W1 2/200 · W2 2/150 · W3 2/100 · W4 2/100 · W5 2/75 · W6 3/75 · W7 3/50 ·
W8 3/50 · W9 4/30 · W10 4/30  (COUNT / BARS).
