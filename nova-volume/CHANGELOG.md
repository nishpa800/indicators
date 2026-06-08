# NOVA VOLUME — Changelog

## v1 (2026-06-08)
- First release. Tick-based multi-horizon volume anomaly engine.
- Robust-sigma tiers (σ3/σ5/σ8/σ12) via median + percentile spread (heavy-tail safe).
- Ratio-to-median tiers (X2/X4/X8/X16).
- Horizon-extreme percentile tiers (MONTH/QUARTER/YEAR) — fire even when NOT all-time.
- SLEEPER: year-extreme volume that is NOT all-time-high (the exact HV/HEV/Nagasaki miss).
- Dollar-volume track for small-cap -> large-cap normalization.
- Numeric magnitude exports (robust_z, ratio_to_median, pct_rank_*, dollar_vol_z) for the offline fire matrix.
- Tick-safe by construction: no tv_ta/relativeVolume, no timeframe.in_seconds, no request.security.
- NRA non-repaint ([1] + offset=-1). Legacy HV indicator left untouched.
- Proven live on NASDAQ:CLSK @ 100T. Passed NINE NINES 78/78 action gate.

## v1.1 (2026-06-08)
- Raised default thresholds to cut signal count (sigma 4/6/10/16, ratio 3/6/12/24, pct 99.5/99.8/99.95, DV 10/99.8). ALL adjustable inputs.
- Added 3 streak detection plots (base = ANY NOVA tier): STREAK2 (2 in a row), STREAK3 (3 in a row), STREAK ROLLING (>=N fires within W bars; defaults 3-in-7, adjustable).
- roll_cnt numeric export added. Recompiled clean on CLSK 100T.
