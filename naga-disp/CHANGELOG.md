# naga-disp — CHANGELOG

## NAGA DISP v1 — 2026-08-18
- **NEW STUDY PAIR (create lane).** `versions/NAGA_DISP_v1.pine` (TIME) + `tick_friendly/NAGA_DISP_TICKFRIENDLY_v1.pine` (TICK) — logic byte-identical below the indicator() line.
- Operator goal dictation 2026-08-18: Nagasaki + displacement on the SAME candle; 4K/3K/2K/1K high-volume + displacement; **FIRST BAR MASTER default ON** (VP + alert fire IFF the marked candle is the session's first bar); displacement sigma **default 9, editable**; volume lookbacks **editable**, defaults 1000/2000/3000/4000.
- Engines carried VERBATIM from the operator's sources: `50 to 4k with naga SINGLES.txt` (HV ladder `volume[1] == ta.highest(volume,N)[1]`, HEV/Nagasaki running max, nested-tier exclusivity) and `displacement times four.txt` (sigma-exceedance AND FVG, offset -1). Both sha256-pinned in the file header.
- 10 lanes (5 tiers x Bull/Bear), each a full sig_/fire_/alf_ chain: real plotshape VP + plot checkbox + input.color + 🔔 alert checkbox + alert() emission. Tiers EXCLUSIVE (highest tier prints); at most one marker + one alert line per candle.
- Alert grammar v1.3: `<SIDE>[ G>B<r>x] | [FIRST | ]<LANE>:HV<achieved depth>,D<achieved sigma>`; metadata on the log.info lane.
- Budget: 20/64 TV units (10 plotshapes x 2 with input.color); 0 plot(); 0 alertcondition; 0 graphic objects.
- Rigor R2: every numeric default is operator-dictated or carried verbatim from the pinned sources.
