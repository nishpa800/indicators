# First Bar Fable

**Current version:** `v2` → `versions/FIRST_BAR_FABLE_v2.pine`
**(chart title: "First Bar Fable v2" / shorttitle "1st BAR FABLE v2")**

Previous: `v1` → `versions/FIRST_BAR_FABLE_v1.pine` (title "First Bar Fable v1").

Composite first-bar detection study, named in homage of Fable. Verbatim ports of
the suite's canonical engines (1st PUP FAUNA, B2B PUP v5.4, TNT OD v3, SQUARIFY v3,
Heavy Weapons Singles v2, Ultra v57, HW v3, HVD PBJ PPD).

- **v1** — S1–S17 (RVOL/GS/MOAB+Disp9+PBJ, Typhoon, Musashi, Whale, B2B SAAB/KRATOS,
  Dynamite, Ignite, Nagasaki-1stBar, B2B Napalm).
- **v2** — v1 plus S18–S25 (B2B PUP/PPD+Disp9, B2B FC Cluster, D9 Bull/Bear studies,
  Unified Combo+Disp9) and the HVD PBJ PPD groups (Pipeline D CO, Back-to-Back HV+D,
  HV+D Momentum co-occ), bull + bear. 53 plots total.

Common behavior:
- **First Bar Master** checkbox (default ON): detections only fire when their
  reference bar is the first bar of the session. Uncheck to fire on any bar.
  Exception in v2: **B2B FC Cluster (S20/S21) always fires on any bar** — it
  overrides the First Bar Master by design (loud tooltip in the settings).
- Every detection checkbox gates **both** the plot and the alert.
- Every adjustable displacement engine is grouped; the file header carries a
  DISPLACEMENT MAP stating which engine drives which plots.
- No fixed windows — rolling windows only.
- Pine v5, non-tick study. Fast Calculation must stay OFF in TradingView.

See `CHANGELOG.md` for the full plot tables and interpretation notes.
