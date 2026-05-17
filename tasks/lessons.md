# Lessons — corrections from the user, with guards added to CLAUDE.md

Each entry: date · what happened · the rule added to CLAUDE.md so it never repeats.

---

## 2026-05-17

- **Lost a reference person's name during plan rewrite.** Jake Van Clief (@lostandlucky) was the original file-and-folder reference and got dropped when I introduced leadgenman / Manthan / Boris. Guard: never strip a named reference from a section during a rewrite — preserve every attribution.
- **Misframed massive.com as one of many vendors.** It is the single vendor for Phase 0; the "sources" are the multiple data products inside it (stocks, options, ETFs, news, earnings, NYSE order imbalance, etc.). Guard: massive.com is the sole vendor in Phase 0.
- **Proposed verification stops during build.** User had granted full autonomy; pausing to confirm was rejected. Guard: no verification stops in Phase 0 build — autonomy granted; build through to PR.
- **Named the codebreaking division "Cryptography".** Collides with the crypto asset class. Guard: "Crypto" means cryptocurrency only; the codebreaking division is "Codebreakers."
- **Initially scoped Phase 0 to "download data."** User clarified: Phase 0 is scaffolding only; no live data movement. Guard: no data downloads in Phase 0; every Python module defaults to `DRY_RUN=true`.
