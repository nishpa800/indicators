# Master Directory Ingest — Delta Report (2026-05-10)

Source: `~/Library/Mobile Documents/com~apple~CloudDocs/Sheets/Master Directory/`
(16 `.txt` Pine sources).

This report is the diff between Anish's iCloud "Master Directory" snapshot
and the repo as of branch `claude/organize-indicators-hierarchy-8JDw1` at
ingest time. **No file is labelled "canonical."** Picking the canonical
variant is the OUTPUT of root extraction + TradingView visual verification,
not the input to this report.

---

## 1. New families added (5)

Each was previously absent from the repo. Created `<family>/versions/` and
copied the source as `.pine`. No `LATEST.txt` written — that pointer waits
on per-variant vetting.

| Family            | New file                                                                      | Lines | Source in Master Directory                                                                                  |
|-------------------|-------------------------------------------------------------------------------|------:|-------------------------------------------------------------------------------------------------------------|
| `hv-ladder`       | `HV_LADDER_50_TO_1K_v1.pine`                                                  |   196 | `50 to 1k.txt`                                                                                              |
| `hv-ladder`       | `HV_LADDER_100_TO_1K_v1.pine`                                                 |   227 | `100 to 1000.txt`                                                                                           |
| `anish-tb-foster` | `ANISH_TB_FOSTER_AIRBUD_LEPROSY_ENHANCED_v1.pine`                             |   704 | `Anish TB Foster Air Bud Leprosy Enhanced_..._702_...txt`                                                  |
| `heavy-weapons`   | `HEAVY_WEAPONS_8FVG_MATRIX_COMBOS_NO_PENTAGON_v1.pine`                        |   489 | `Heavy Weapons 8 FVG Matrix Combos No Pentagon_..._488_...txt`                                              |
| `fauna-shifu`     | `FAUNA_SHIFU_JUMBO_CIA_1ST_PUP_v1.pine`                                       |  2338 | `fauna + SH.txt` (indicator title: "Jumbo CIA ★ 1st PUP FAUNA + SHIFU ★")                                  |
| `vob-single-sens` | `VOB_SINGLE_SENS_WITH_TABLES_v1.pine`                                         |   414 | `vob 6 tc 3 buy 3 sell based on one vob sensitivity.txt`                                                    |
| `vob-single-sens` | `VOB_SINGLE_SENS_NO_TABLES_NO_EMISSION_v1.pine`                               |   415 | `VOB but with just one sensitivity ... no tables no emission.txt`                                           |

Bible family count: **15 → 20** after this ingest.

---

## 2. New variants added to existing families (3)

`.pine` siblings inside an existing family folder. None of these gets
`LATEST.txt` updated; they coexist with the prior canonical until vetted.

| Family         | New variant file                                       | Lines | Source                                                                                                       | Why it's a variant (not the canonical)                                                                                                                                            |
|----------------|--------------------------------------------------------|------:|--------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `hvd-pbj-ppd`  | `HVDPBJPPD_2246_FROM_MASTERDIR_2026-05-10.pine`        |  2246 | `HV+D ↔ PBJ ↔ ..._2246_...txt` (133,324 bytes)                                                              | Significantly larger (133 KB) than current `THE_ONLY_ONE` (1767 lines / 109 KB) — likely a newer, broader build. To be vetted.                                                    |
| `hvd-pbj-ppd`  | `HVDPBJPPD_1939_FROM_MASTERDIR_2026-05-10.pine`        |  1939 | `HV+D ↔ PBJ ↔ ..._1939_...txt` (123,341 bytes)                                                              | Same logical predecessor as repo's `HVDPBJPPD_4.26.1244am_PPD_UC_RVOL_2026-05-05.pine` BUT with **flipped Tier-1 input defaults** (Bear UUUU/UUU/Bull UU/Omega/Alpha Strike toggled). |
| `vob-asym`     | `VOB_Asym_T3x6_FROM_MASTERDIR_ummmm_2026-05-10.pine`   |  1473 | `VOB Asym T3 ×6 + MutEx Lines + Claude ummmm.txt` (112,729 bytes)                                            | Indicator title ends in `+ Claude ummmm`; **plotshape locations/shapes for T3 buy/sell are visually different** from repo's `VOB_Asym_T3x6_MutEx_Claude_v8_2026-05-02.pine`.       |

---

## 3. Dupes — already in repo (whitespace-only or identical)

| Family               | Master-dir file                                                   | md5 vs repo canonical | Verdict                              |
|----------------------|-------------------------------------------------------------------|-----------------------|--------------------------------------|
| `heavy-combo-toggles`| `3 from 16 WMD WBUSH Heavy combo toggles_267_...txt`              | identical             | ✅ no action                          |
| `hv-fvg-gz1-og`      | `HV FVG GZ1 OG THIS No tables_..._5.9.753pm.txt`                  | identical             | ✅ no action                          |
| `hvd-pbj-ppd`        | `hvd+PBJ golf works ONLY THIS.txt` (1767 lines)                   | CRLF-only diff        | ✅ no action (content identical)      |
| `anish-50-1st-combo` | `Anish 50% 1st Combo_..._181_...txt`                              | trailing newline only | ✅ no action (1-byte cosmetic diff)   |
| `heavy-pentagon`     | `Heavy PENTAGON_heavy pentagon_444_...txt`                        | trailing blank line   | ✅ no action (1-byte cosmetic diff)   |
| `ultra-combo`        | `Ultra Combo v57 57_Ultra v57—1147_...txt`                        | trailing whitespace   | ✅ no action (2-byte cosmetic diff)   |

For each whitespace-only case the repo file is kept as-is; the master-dir
copy is not duplicated.

---

## 4. md5 evidence (Master Directory side)

| File                                                                                                  | md5                                |
|--------------------------------------------------------------------------------------------------------|------------------------------------|
| `100 to 1000.txt`                                                                                      | `a430389ff156d0187f0eb4b10568e91f` |
| `50 to 1k.txt`                                                                                         | `225fb5ec9cbceaedb55e6abbe19a6951` |
| `Anish 50% 1st Combo_..._181_...txt`                                                                   | `8c6559bef0b83ec77652eb5fdc5f7811` |
| `Anish TB Foster Air Bud Leprosy Enhanced_..._702_...txt`                                              | `12c7f7c5aaa37ef650052e58535ead34` |
| `Heavy PENTAGON_heavy pentagon_444_...txt`                                                             | `0c3e240777e0c873bec67b602fb0cb12` |
| `Heavy Weapons 8 FVG Matrix Combos No Pentagon_..._488_...txt`                                         | `13d1cb0f74f666a2ba54ef248e7f4f00` |
| `HV FVG GZ1 OG THIS No tables_..._5.9.753pm.txt`                                                       | `6f784f1c88ac1ac27c4861e41706ac6c` |
| `HV+D ↔ PBJ ↔ ..._1939_...txt`                                                                         | `632f14596bd75591b82431ba903b1cc3` |
| `HV+D ↔ PBJ ↔ ..._2246_...txt`                                                                         | `9e135a32021d968f51860ae6f292fcde` |
| `Ultra Combo v57 57_..._1147_...txt`                                                                   | `6e8a7d444dc83466cba92b442d5852dc` |
| `VOB Asym T3 ×6 + MutEx Lines + Claude ummmm.txt`                                                      | `f3e87fc5ca231d4e05c652ae2c804300` |
| `VOB but with just one sensitivity ... no tables no emission.txt`                                      | `e9d32e6753e364bb9db5a15b23d40871` |
| `fauna + SH.txt`                                                                                       | `44c4b58c5b577885d9e33ee360333c21` |
| `hvd+PBJ golf works ONLY THIS.txt`                                                                     | `59b844f8bb96307cd74e10eec4927928` |
| `vob 6 tc 3 buy 3 sell based on one vob sensitivity.txt`                                               | `e2961495bae8cae320d7fd4beacd0013` |
| `3 from 16 WMD WBUSH Heavy combo toggles_267_...txt`                                                   | `498bfee8cb4a4a5b850afec97cf60700` |

---

## 5. Next steps (queued in TodoWrite)

1. Run Stage-1 root/composite extraction for the 5 new families
   (`hv-ladder`, `anish-tb-foster`, `heavy-weapons`, `fauna-shifu`,
   `vob-single-sens`). One Agent(Explore) per family. Writes
   `bible-input/extract-<family>.yaml`.
2. Cross-variant audit for `hvd-pbj-ppd` (1767 / 1939-master-dir /
   2246-master-dir) and `vob-asym` (v8 / `+ Claude ummmm`) — extract
   each variant's roots and composites into `bible-input/extract-<family>-<variant>.yaml`.
3. Merge YAMLs → re-run `tools/merge_extracts.py`,
   `tools/build_lineage_cards.py`, `tools/build_docs.py`. Bible regen.
4. Generate `docs/cross-variant-commonality.md` — for every root in
   `data/indicators.yaml`, list which variants own it. Surfaces shared
   roots (likely correct across the board) vs unique ones (drift-prone,
   need TV checking).
5. Then continue Stage 3 TV verification.

No file in the repo has been labelled canonical as a result of this ingest.
