# VOB BB — Birth Bar Study CHANGELOG

## v1.2 (2026-07-26) — TV-COMPILE FIX (operator paste found 9 problems in v1.1)
- CE10123 x7: user-function bank resolution returned series int into ta.ema's simple
  length. Root law learned: Pine user-function returns are ALWAYS series — never route
  input constants through a helper when a built-in needs simple. Fix: inline ternaries.
- CW10002 x2: ta.crossover/crossunder hoisted out of conditional expressions.
- v1/v1.1 carry the landmine; v1.2 = first paste-valid build. Twins same wave.

## v1.1 (2026-07-26) — GRADED BIRTHS (default-forward wave, no operator trigger)
- THE FORMATION GRADE: five birth-bar features (displacement/trend/volatility/depth/cycle)
  scored 0-20 vs corpus-calibrated quintile boundaries (173,301 births; out-of-sample:
  Grade A >=18 -> 77.5% hold (n=4,161) · Grade B >=14 -> 71.7% · base 62.4%).
  Constants: derived/birthbar_calibration_v2/formation_score_constants.json.
- New side-typed A-BIRTH Bull/Bear dp:vp:alert lanes (labelup/labeldown, size normal) —
  "print the lines that will hold" made real; every birth alert now carries SCORE+GRADE.
- Budget 20/64. Twins same wave.

## v1 (2026-07-26) — birth of the study class
- NEW STUDY: 8 side-typed dp:vp:alert lanes — Birth/Survivor/Elder/Return × Bull/Bear.
- Impetus: the birth-bar zero-label diagnosis (operator report, VSAT 180m) + the
  1,831,429-birth full-corpus calibration. Docs: 2026-07-26_TV-TickBar-RE_
  BirthBarZeroLabel-DiagnosisAndSurvivorDesign_v1.0–v1.3; cert derived/birthbar_calibration_v2/.
- Earliest-entry law: BIRTH fires at the EMA-crossover confirmation bar — the first
  bar a birth is knowable; nothing earlier exists without repainting. Cooldown default 0.
- The survival law A*(s)=s·max(0.6, 3.949−0.416·ln s) (R²=0.976), ×0.62 on 2D+ charts;
  ELDER at 3·A*; lineage-age inheritance on DEDUP (34.5% of deaths are administrative).
- Two-Concepts Law: ORIGIN lanes ≠ RETURN lane (ATR-band retest, explicitly NOT a birth).
- SENSITIVITY BANKS (operator-dictated 2026-07-26, mid-wave): 7 slots per study + Bank
  dropdown — B1 25/38/50/62/75/88/100 (quarter-steps, very-high-TF; 37.5/87.5 rounded to
  int) · B2 100–700 · B3 800–1400 · B4 1500–2100 · B5 2200–2800 · B6 2900–3000 (3k cap,
  2 live rungs) · CUSTOM. Stack copies, one bank each, to cover 25→3000.
- Twins: VOB_BB_v1.pine (time) + tick_friendly/VOB_BB_TICKFRIENDLY_v1.pine (same wave).
- 16/64 TV units; real-plot VPs only; 2 line.new sites (zone level lines, disclosed).
