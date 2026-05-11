# SOP — Phase M Runner (Historical Backfill + Detection Sampling)

When to use:
- After ports are added or modified, to refresh detection counts.
- Before Stage 4 (composite firing validation), to produce the
  Python-side detection corpus.
- When adding new tickers to broaden the per-composite sample.

## Tools

All in `~/code/anish/realtime-indicators/`:

| Step | Script | Input | Output |
|---|---|---|---|
| 1 | `download_bars.py` | Ticker + `--days N` | `~/data/massive/<TICKER>/<YYYY>/*.parquet` (1-second bars) |
| 2 | `aggregate_bars.py` | Ticker + `--tfs 45s 1m 2m 3m 4m 5m 10m 15m 30m 1h` | `~/data/massive/<TICKER>/_resampled/<TICKER>_<TF>.parquet` |
| 3 | `run_ports_against_bars.py` | Ticker + `--tfs ...` | `~/data/massive/_phase_m/<date>_detections.csv` |
| 4 | `tabulate_results.py` | `--csv <detections.csv>` | `..._fires_per_composite.csv`, `..._fires_top100.csv`, `..._fires_summary.md` |

## End-to-end one-liner

```bash
cd ~/code/anish/realtime-indicators
TICKER=SMR; DAYS=60; TFS="45s 1m 2m 3m 4m 5m 10m 15m 30m 1h"
uv run python download_bars.py $TICKER --days $DAYS && \
  uv run python aggregate_bars.py $TICKER --tfs $TFS && \
  uv run python run_ports_against_bars.py $TICKER --tfs $TFS && \
  uv run python tabulate_results.py
```

## Watchlist sweep (multi-ticker)

```bash
for t in $(cat watchlist.txt | grep -v '^#'); do
  TICKER=${t#*:}
  uv run python download_bars.py $TICKER --days 365 && \
    uv run python aggregate_bars.py $TICKER --tfs 1m 5m 15m 1h
done
uv run python run_ports_against_bars.py --watchlist watchlist.txt --tfs 1m 5m 15m 1h
uv run python tabulate_results.py
```

## Known caveats (see `docs/validation-log/2026-05-10-phase-m-smr60d.md`)

- **Stateful packs return very few fires** until the runner is updated to
  thread state objects across bars. Until then, `b2b_pup`,
  `hvd_pbj_ppd`, `fauna_shifu`, `tnt_od`, `heavy_combo`,
  `anish_stack`, `swings`, `ultra_combo`'s stateful composites mostly
  return zero on historical data. Stateless roots (`primitives`,
  `vob`, `disp`, `HV-ladder HEV`) work fine.
- For Stage 4 validation, use Path A TV loggers (label-based
  history) as the authoritative source. Phase M Python detections
  are a cross-check, not the primary reference.

## When Phase 2 of the runner lands (state threading)

The runner gets a per-(ticker, TF, pack) state pool and walks bars
linearly, calling `pack.detect_bar(state, bar, bars)` per bar. State
machines accumulate properly. Stateful composites start firing on
real data at expected rates. Replace this SOP's caveats section
with the updated coverage.
