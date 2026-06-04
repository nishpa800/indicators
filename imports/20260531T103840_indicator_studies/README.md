# Desktop Indicator Studies Import

Run ID CST: `20260531T103840`

This folder preserves Anish's Desktop Pine Editor exports and creates Pine v5-normalized copies for Python conversion and TradingView parity testing.

## Rules

- Originals are preserved under `originals/`.
- Pine v5-normalized copies are under `pine_v5/`.
- Old versions are not deleted or overwritten.
- Files originally marked `//@version=6` are backported by version directive here and require TradingView compile/parity verification before trust promotion.
- Duplicate Desktop exports are recorded in `IMPORT_MANIFEST.json`.

## Counts

- Files total: 16
- Unique source hashes: 15
- Pine v6 sources backported to v5 directive: 3
