# Fable Playbook v1 — the plays study

Houses the machine playbook's play TRIGGERS (lake: `contracts/playbook_v1.json`, 50 plays,
25 bull / 25 bear; human doc `docs/2026-07-14_TV-TickBar-RE_FablePlaybook-v1-Top50Plays_v1.0.md`).
16 S-plots = play families (mass legs, PUP runner, fades, naked-spike shorts, CORE
confluence feeds). MASS floor is an input: default 2000, selectable 1000/1500/1750/4000
(operator order 2026-07-14). Opening-window gate (default first 3 bars of session).
Engines are verbatim adaptations of FIRST_BAR_FABLE_v2 blocks; no vendor imports
(tick-safe by construction — no relativeVolume). Entry/stop/target law lives ONLY in the
playbook JSON — this study detects, it never advises.

- **Current version: v5** — `versions/FABLE_PLAYBOOK_v5.pine` (+ `versions/FABLE_PLAYBOOK_v5_NTS.pine`,
  the non-tick-friendly twin). Every S1-S19 toggle's info button is now LOGIC-FIRST: it
  opens with a verbatim "FIRES WHEN (ALL true): ①②③…" condition list (never truncated),
  then `► PLAYS:` (ids + status), `► EVIDENCE:`, `► ENTRY/STOP/EXIT:` (from
  `contracts/playbook_v1.json`, as generated for v4), and the ESTIMATED/VALIDATED-promotion
  caveat. 5 ABOUT rows (`ab_1..ab_5`, before S1) define the shared engines (MASS,
  Displacement, RVOL tiers incl. an honesty note on the unoptimized legacy threshold curve,
  Pocket Pivot/FAUNA/window) so every toggle's tooltip can stay short and precise. v4's
  cards led with bookkeeping and truncated the trigger first — the operator could not tell
  what fires a plot from the info button; v5 fixes that (lessons ledger L-54 follow-up).
