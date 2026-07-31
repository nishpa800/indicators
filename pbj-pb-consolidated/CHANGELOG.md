# CHANGELOG — PBJ PB Consolidated

## 2026-07-23 — v1 (initial)

`versions/PBJ_PB_CONSOLIDATED_v1.pine` — ONE Pine v5 study merging four sources:

| # | Source | What was taken | Defaults |
|---|---|---|---|
| Base | PB & PBJ — 4 Signals (`pbj_pb_4_signals_SERIOUS`) | Entire engine (OKEH Zoo + PB&J Filter + Supertrend + level management) and all 4 signals (Bull/Bear PB, Bull/Bear PBJ) | Preserved verbatim (VWMA 5, PB&J 20/14/25/3.0/20/0.1, ST 10/2.0) |
| Add 1 | KC Rev 8 (`kc_rev_8`) | ONLY the four re-entry signals: Bull/Bear Re-entry Cross, Bull/Bear Re-entry Slope. No KC band plots, no volatility/cluster signals | Preserved verbatim (EMA 20, mult 2.0, ATR 10, slope lookback 3, thresholds 0.05) |
| Add 2 | Anish 50% 1st Combo (`anish_50_1st_combo`, v6) | ONLY PUP (Pocket Pivot Bull) and PPD (Pocket Pivot Bear). Ported v6 → v5, logic identical, conf-gated as in source | Preserved verbatim (barsize 3.0%, lookback 10) |
| Add 3 | Displacement 4x (`displacement_4`) | ONE displacement engine (not four). FVG-confirmation logic identical, offset −1 plotting on the displaced candle | Std Dev Multiplier input field **default 4.5** (source instances were 6.5/6.0/5.5/5.0); Range Type "Open to Close", Std Dev Length 100 |

Signal registry S1–S12 (repo `S<N>: descriptor` naming):
S1–S4 PB/PBJ, S5–S8 KC re-entry, S9 PUP / S10 PPD, S11/S12 Displacement (offset −1).

Repaint doctrine per source, preserved verbatim:
- S1–S4, S9/S10, S11/S12 gated by `barstate.isconfirmed` (as in their sources).
- S5–S8 NOT conf-gated — KC Rev 8 fires on raw crossovers; preserved for 1:1 parity with the standalone KC Rev 8 study.

Alerts: 12 individual `alertcondition()` + ANY, aggregated dynamic `alert()` with
name+count string, and multiplexer extended with "KC Re-entry Only", "PUP/PPD Only",
"Displacement Only" selections. All `alert()` calls use `alert.freq_once_per_bar_close`.
