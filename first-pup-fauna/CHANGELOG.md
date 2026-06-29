# 1st PUP FAUNA — Changelog

Newest first. Each version = one file in `versions/`.

---

## LTF v1 — 2026-06-29
**File:** `versions/FIRST_PUP_FAUNA_LTF_v1.pine`
**Derived from:** the current `Jumbo CIA ★ FIRST BAR ONLY FAUNA FIXED★` (`1st PUP FAUNA`) — base logic
byte-for-byte unchanged; this is a **separate Long-Timeframe build**, not a replacement.

**What changed (LTF gate layer only):**
- Renamed: name + shorttitle now end in **` LTF`**.
- New `★ LTF GATE LAYER ★`: defines `ltf_1k = volume == ta.highest(volume, 1000)` and
  `ltf_volGate = ltf_1k or sigNagasaki` (HEV), plus a gated `g_*` boolean per detection.
- **Every detection plot now additionally requires `1k` OR `Nagasaki`** (1000-bar volume high, or
  all-time-high volume).
- **Every detection plot that did not already require displacement now requires it**
  (direction-matched `sigDISPBull` / `sigDISPBear`): Grand Slam, MOAB, Whale±, SAAB²/KRATOS²,
  Typhoon, Nagasaki, PAF, Foxtrot, Katana, Musashi. Detections that already required displacement
  (Super, Tomcat, Double Disp, PUP/PPD Combo, Full Stack, FVG Stack, FAUNA+ Alpha–Echo, Golf, OD)
  get only the volume gate.
- Underlying `sig*` definitions, inputs, toggles, offsets, colors, and alert payloads are **unchanged**;
  only the plot/alert *fire* conditions were tightened (via `g_*`), so combos that reuse a raw `sig*`
  (e.g. `nag_dir`, `nag_special`) are not affected.

See `../DETECTION_PLOTS_LTF_TABLE.md` for the full current-vs-additional comparison per detection plot.
