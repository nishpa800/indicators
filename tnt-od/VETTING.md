# TNT-OD v3 — Vetting Status

Anish confirmed on 2026-05-10 that `versions/TNT_OD_v3.pine` (2,150 lines,
148,437 bytes, md5 `30fc1ebf1da9f113bd285f8993211226`) **is** the version
currently on his TradingView canvas — the one with the v3 features:

- New conditional gate (6 atoms — RVOL 1x / GS / UC / Nagasaki+Any / HCT / DISP ≥ σ)
- T1 RELAY (bull/bear) — consecutive Tier-1 visual on bar[2] AND bar[1]
- T1 STACK (bull/bear) — ≥ 2 distinct Tier-1 visuals on bar[1]
- Five distinct displacement engines (Main / DYNAMITE / USE V5 / HCT / Gate)
- Inline-ported HCT engine
- Inline UC engine (placeholder; replaceable with Squarify v2 UC)

## Stage 6.4 correction (this commit)

The earlier Stage 6.4 rename was wrong. The file was renamed
`TNT_OD_v3.pine → TNT_OD_v3_LEGACY_PRE_CONSOLIDATION.pine` on the
assumption that the smaller `TNT_Opening_Drive_OD_v3_2026-05-04.pine`
was the current canonical. In fact:

- `TNT_OD_v3.pine` (148 KB, 2150 lines, internally titled "TNT Opening
  Drive OD v3") **is** the v3 source matching Anish's CHANGELOG and his
  canvas.
- `TNT_Opening_Drive_OD_v3_2026-05-04.pine` (123 KB, 1802 lines,
  internally titled v2) is an older snapshot — likely an earlier
  consolidated rename that was filename-tagged v3 before the actual v3
  features were authored.

This commit reverts the rename. Both files remain in the repo (Anish's
explicit instruction: "make sure that we vet it and don't get rid of the
prior versions").

## Vetting status

| Item | Status |
|---|---|
| File on disk | ✅ `versions/TNT_OD_v3.pine` present |
| Header matches Anish's paste (lines 1-92 — CHANGELOG + tier system + offset summary + alert format + master toggles + exceptions) | ✅ verified by line-by-line inspection on 2026-05-10 |
| Body matches Anish's paste (lines 93-2150 — engine implementation) | ✅ markers verified (header line 4 `CHANGELOG v2 → v3 (2026-05-08)`, footer last 3 lines `END — TNT OPENING DRIVE (OD)`, contains `T1 RELAY`/`T1 STACK`/`gateStdMult`/`en_newGate`/`hct_disp_strength`/`u5_*` per spec) |
| TradingView compile | ⏸️ Anish to verify |
| Plots match v2 with gate OFF | ⏸️ Anish to verify side-by-side |
| Gate filters NPM-family when ON | ⏸️ Anish to verify |
| T1 RELAY fires on consecutive Tier-1 visuals | ⏸️ Anish to verify |
| T1 STACK fires on ≥ 2 distinct Tier-1 visuals | ⏸️ Anish to verify |
| Inline HCT matches HCT standalone | ⏸️ Anish to verify |
| Inline UC placeholder is acceptable (or replace with Squarify v2 UC) | ⏸️ Anish to decide |
| 5 displacement engines do not cross-contaminate | ⏸️ Anish to verify |
| `LATEST.txt` updated to point at `TNT_OD_v3.pine` | ⏸️ **PENDING all chart-side verifications above** |
| Bible extraction (`bible-input/extract-tnt-od.yaml`) updated to v3 schema | ⏸️ Stage 8 follow-up |

## When vetting completes

1. Flip `tnt-od/versions/LATEST.txt` to `TNT_OD_v3.pine`.
2. Re-extract `bible-input/extract-tnt-od.yaml` to capture v3-only
   roots/composites:
   - `tnt-od::T1_RELAY_BULL`, `T1_RELAY_BEAR`
   - `tnt-od::T1_STACK_BULL`, `T1_STACK_BEAR`
   - 5 displacement engines as separate IPSF entries
   - Inline HCT outputs (`hct_bull` / `hct_bear` / `hct_neutral`)
   - Inline UC outputs (`uc_bull` / `uc_bear`)
3. Re-run `tools/merge_extracts.py` then
   `tools/build_lineage_cards.py` then `tools/build_docs.py`.
4. Update this VETTING.md to "Completed YYYY-MM-DD".
5. Commit + push + PR comment.

## Prior versions — DO NOT DELETE

All four prior versions are intact:

- `versions/TNT_OD_v1.pine` (99.9 KB, 1556 lines)
- `versions/TNT_OD_v2.pine` (123.0 KB, 1802 lines)
- `versions/TNT_OD_v3.pine` (148.4 KB, 2150 lines) — **the v3 Anish confirmed**
- `versions/TNT_Opening_Drive_OD_v3_2026-05-04.pine` (123.0 KB, 1802 lines — internally v2)

The redundancy / drift analysis depends on the predecessors. They stay.
