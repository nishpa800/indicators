# naga-disp — CHANGELOG

## NAGA DISP v1 — 2026-08-18
- **NEW STUDY PAIR (create lane).** `versions/NAGA_DISP_v1.pine` (TIME) + `tick_friendly/NAGA_DISP_TICKFRIENDLY_v1.pine` (TICK) — logic byte-identical below the indicator() line.
- Operator goal dictation 2026-08-18: Nagasaki + displacement on the SAME candle; 4K/3K/2K/1K high-volume + displacement; **FIRST BAR MASTER default ON** (VP + alert fire IFF the marked candle is the session's first bar); displacement sigma **default 9, editable**; volume lookbacks **editable**, defaults 1000/2000/3000/4000.
- Engines carried VERBATIM from the operator's sources: `50 to 4k with naga SINGLES.txt` (HV ladder `volume[1] == ta.highest(volume,N)[1]`, HEV/Nagasaki running max, nested-tier exclusivity) and `displacement times four.txt` (sigma-exceedance AND FVG, offset -1). Both sha256-pinned in the file header.
- 10 lanes (5 tiers x Bull/Bear), each a full sig_/fire_/alf_ chain: real plotshape VP + plot checkbox + input.color + 🔔 alert checkbox + alert() emission. Tiers EXCLUSIVE (highest tier prints); at most one marker + one alert line per candle.
- Alert grammar v1.3: `<SIDE>[ G>B<r>x] | [FIRST | ]<LANE>:HV<achieved depth>,D<achieved sigma>`; metadata on the log.info lane.
- Budget: 20/64 TV units (10 plotshapes x 2 with input.color); 0 plot(); 0 alertcondition; 0 graphic objects.
- Rigor R2: every numeric default is operator-dictated or carried verbatim from the pinned sources.

## NAGA DISP v2 — 2026-08-19
- **TWO SECTIONS (operator goal 2026-08-19).** SECTION 1 = the v1 ten same-candle lanes, with the 1K/2K/3K lanes now ALSO requiring, on the marked candle, RVOL 1x OR Grand Slam (bull) / RVOL 1x OR MOAB (bear) — KC COMBO SR v5.0 engine verbatim (rv_avgLen 30, rv_smaLen 20, th_1x/th_gs ladders, tick fallback tfSec=10). NAGA/4K lanes unchanged.
- **SECTION 2 = 10 RUN lanes** (NAGASAKI/4K/3K/2K/1K RUN x Bull/Bear): an unbroken chain of consecutive >=floor candles (floor = the 50-to-4k "500" VP `volume[1] == ta.highest(volume,500)[1]`, editable) that CONTAINS the anchor (MASTER ON: the session first bar carrying the displacement; OFF: any displaced candle); fires the moment the N-th candle (default 4, editable) closes with a >=1K candle inside the last-N window; the HIGHEST tier in the window prints (exclusive); counter restarts after each fire (rolling re-fire on the same chain); chain break resets. Marker on the completion candle (offset -1). Alert line `<SIDE> | <TIER> RUN:RUN<n>@FIRST-<bars back to anchor>`.
- Shared knobs: displacement sigma (9), lookbacks 1K/2K/3K/4K; new knobs: N in a row (4), floor (500). Nagasaki has no number.
- Budget 40/64 (20 plotshapes x 2); 0 plot(); 0 alertcondition; 0 graphic objects. Twins byte-identical below indicator().
- (same day) plotshape calls rewritten keyword-form (title=/style=/location=/color=) so visual_identity_gate measures the 4 location bands (D_vis 3 -> 0); logic byte-identical.
