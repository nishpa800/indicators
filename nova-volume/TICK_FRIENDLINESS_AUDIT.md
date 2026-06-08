# Tick-friendliness audit — June 7 indicator folder (2026-06-08)

Method (heuristic static scan; acceptance test = live compile on a tick chart):
- **Risk calls:** `tv_ta` / `relativeVolume` (RE10023 on ticks), `timeframe.in_seconds()` (na on ticks), `request.security`.
- **Guards present:** `tick_assumed` / `tfSec` / `TICK_FALLBACK` / `reg_anchorSafe` / `na(...in_seconds)`.
- A file is **tick-safe** if it has either (a) zero risk calls, or (b) every risk call paired with a guard. **No look-ahead** is assumed verified separately (all suite plots are `[1]`/`barstate.isconfirmed`-gated).

| File | relVol/tv_ta | in_seconds | guards | req.sec | Verdict |
|---|---:|---:|---:|---:|---|
| 1st pup fauna.txt | 2 | 1 | 9 | 0 | GUARDED — tick-safe |
| b2b pup_06_07_124pm.txt | 4 | 1 | 5 | 0 | GUARDED — tick-safe |
| f2 e3_06_07_124pm.txt | 0 | 0 | 0 | 0 | NO-RISK — tick-safe |
| fauna dual mode__06_07_124pm.txt | 0 | 0 | 0 | 0 | NO-RISK — tick-safe |
| heavy weapons v3.txt | 5 | 1 | 16 | 0 | GUARDED — tick-safe |
| heavy weapons with 4 fvg 4 matrix.txt | 3 | 1 | 7 | 0 | GUARDED — tick-safe |
| heavy with 2x detection plots.txt | 4 | 1 | 16 | 0 | GUARDED — tick-safe |
| hub 2011.txt | 0 | 0 | 0 | 0 | NO-RISK + header tick-friendly |
| hv to 1k_06_07_124pm.txt | 0 | 0 | 0 | 0 | NO-RISK — tick-safe |
| hvd pbj ppd bear.txt | 4 | 1 | 7 | 0 | GUARDED — tick-safe |
| hvd pbj pup bull.txt | 4 | 1 | 7 | 0 | GUARDED — tick-safe |
| pbj only 4 signals.txt | 0 | 0 | 0 | 0 | NO-RISK — tick-safe |
| tnt od v3.txt | 3 | 1 | 9 | 0 | GUARDED — tick-safe |
| ultra 57__06_07_124pm.txt | 2 | 2 | 11 | 0 | GUARDED — tick-safe |
| vob 11.txt | 5 | 5 | 20 | 0 | GUARDED + header tick-friendly |
| vob v10.txt | 0 | 0 | 0 | 0 | NO-RISK — tick-safe |

## Findings
- **0 files are RED** (no file has a risk call without a guard).
- **6 NO-RISK** files (no tv_ta / in_seconds / request.security): f2 e3, fauna dual mode, hub 2011, hv to 1k, pbj only 4 signals, vob v10 — inherently tick-safe.
- **10 GUARDED** files carry the RE10023 anchor fix + tfSec fallback. Highest guard density in heavy weapons v3 (16), heavy with 2x (16), vob 11 (20).
- Only `hub 2011` and `vob 11` declare tick-friendly in the header; the rest are tick-safe by construction or by guards but lack the header marker.

## Caveat / acceptance test
This is a static heuristic. The **authoritative** check is to compile each on a real tick chart (e.g., 100T) via the TradingView bridge and confirm no RE10023 / no `na` tfSec crash on bar 0. NOVA_VOLUME_v1 was compiled live on NASDAQ:CLSK @ 100T on 2026-06-08 with zero errors (only the v5→v6 deprecation notice, which is intentional per the Pine-v5-only mandate).
