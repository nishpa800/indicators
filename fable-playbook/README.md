# Fable Playbook v1 — the plays study

Houses the machine playbook's play TRIGGERS (lake: `contracts/playbook_v1.json`, 50 plays,
25 bull / 25 bear; human doc `docs/2026-07-14_TV-TickBar-RE_FablePlaybook-v1-Top50Plays_v1.0.md`).
16 S-plots = play families (mass legs, PUP runner, fades, naked-spike shorts, CORE
confluence feeds). MASS floor is an input: default 2000, selectable 1000/1500/1750/4000
(operator order 2026-07-14). Opening-window gate (default first 3 bars of session).
Engines are verbatim adaptations of FIRST_BAR_FABLE_v2 blocks; no vendor imports
(tick-safe by construction — no relativeVolume). Entry/stop/target law lives ONLY in the
playbook JSON — this study detects, it never advises.

- **Current version: v4** — `versions/FABLE_PLAYBOOK_v4.pine` (+ `versions/FABLE_PLAYBOOK_v4_NTS.pine`,
  the non-tick-friendly twin). Every S1-S19 toggle's tooltip is now GENERATED from
  `contracts/playbook_v1.json` by `scripts/alpha/gen_playbook_tooltips.py` (lake root) —
  the settings-dialog info button is the complete play card (ids, status, trigger,
  evidence, entry/stop/exit, ESTIMATED caveat); study UI and playbook cannot drift apart.
