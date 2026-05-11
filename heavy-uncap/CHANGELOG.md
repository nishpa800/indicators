# Heavy Weapons Uncapped — CHANGELOG

## v1 — 2026-05-10

Initial drop. Pine v5, overlay.

`HEAVY_UNCAP_v1.pine` — comprehensive RVOL toolkit. 14 new roots + 12 new
composites added to the bible.

### New roots (14)

- **Hybrid Momentum (7)**: `LONG_1`, `SHORT_1`, `LONG_2`, `SHORT_2`, `LONG_3`,
  `LONG_4`, `LONG_5`. Each gates on bar-RVOL × session-RVOL × body-ratio. All
  IPSF (`hyb_addReg<n>`, `hyb_addCum<n>`, `hyb_bodyRat<n>`).
- **RVOL Sequences (6)**: `UU`, `UUU`, `UUUU`, `DD`, `DDD`, `DDDD`. 2/3/4
  consecutive bullish/bearish bars with per-pair IPSF bar-threshold + sequence-sum
  threshold.
- **Calendar (1)**: `HOT_SPOT`. Union of 6 calendar windows (OpEx,
  Quarter-End, Russell rebal, Tax-Loss, Jan Effect, HF Redemption).

### New composites (12)

- **Back-to-Back (6)**: `B2B_2X_SAAB`, `B2B_2X_KRATOS`, `B2B_2X_BULL_1X`,
  `B2B_2X_BEAR_1X`, `B2B_MID_BULL`, `B2B_MID_BEAR`.
- **Consec Displacement (4)**: `CONSEC_DISP_BULL_2`, `CONSEC_DISP_BEAR_2`,
  `CONSEC_DISP_BULL_3`, `CONSEC_DISP_BEAR_3`.
- **FAUNA label-based (2)**: `FAUNA_BULL`, `FAUNA_BEAR` (hierarchical label-text
  variant).

### Local re-implementations

The indicator re-implements every heavy-pentagon RVOL root + hvd-pbj-ppd's
Displacement locally. Threshold ladders verified byte-identical to
heavy-pentagon by source inspection — no drift today. Documented as
`local_reimplementation_of:` in the extract YAML so a future drift gets
flagged in `docs/redundancy.md`.

All signals gated by `barstate.isconfirmed`. Aggregated alert fires
`alert.freq_once_per_bar_close` with a single tier-ordered message
covering every active signal on the bar.
