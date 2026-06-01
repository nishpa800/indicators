# Pine Library Vault — TradingView house Pine sources

A permanent, redundant, auto-refreshed local mirror of **every TradingView house
(built-in) Pine script** plus the two libraries the indicator suite depends on
(`TradingView/ta` and `TradingView/RelativeValue`).

This vault is the **source-of-truth spec** for the Python port: when an indicator
does `import TradingView/ta/7 as tv_ta` and calls `tv_ta.relativeVolume(...)`, the
verified Pine implementation lives here so the Python `tv_ta` shim can be built and
parity-checked against real source instead of guesswork.

---

## What this is

- **148 Pine sources** (144 STD house studies/strategies + `RelativeValue` library +
  `ta` library at `last` and pinned `v7`/`v6`/`v5`).
- Pulled over **public, unauthenticated HTTP** from TradingView's `pine-facade`
  endpoint. **No login, no cookies, no session, no credentials** are used or required.
- Refreshed automatically every day at **06:30 America/Chicago** by a launchd agent.

## Directory layout

```
pine_libraries/
  raw/        all .pine sources, REAL decoded Pine (not the JSON wrapper)
  manifest/
    manifest.json   array of {scriptName, scriptIdPart, version, filename, bytes, sha256, source_url, fetched_utc}
    MANIFEST.md     human-readable table sorted by scriptName
  logs/       update_<YYYYMMDD_HHMMSS>.log  (one per daily run)
  README.md   this file
  update_pine_libraries.sh   the idempotent daily refresher
```

## ⚠️ NEVER hand-edit `raw/`

`raw/` is a **daily-refreshed mirror** of upstream TradingView source. Anything you
type into a file under `raw/` will be silently overwritten on the next 06:30 run.
If you need to modify a library for the Python port, copy it OUT of the vault first
and edit the copy in your own module.

---

## THE PROVEN PUBLIC FETCH METHOD (verified 2026-05-31, HTTP 200, no auth)

Always send header `User-Agent: Mozilla/5.0`.

### STEP A — get the master list of all house libraries

```bash
curl -s -A 'Mozilla/5.0' \
  'https://pine-facade.tradingview.com/pine-facade/list?filter=standard' \
  -o /tmp/std_list.json
```

Each entry is JSON with keys including `scriptName`, `scriptIdPart`
(e.g. `STD;24h%Volume` or `PUB;LIB_TradingView_RelativeValue`), `version`,
`scriptAccess`. As of 2026-05-31 the list returns **145 entries** (144 `STD;` +
1 `PUB;` library).

### STEP B — fetch the source of ONE library by its scriptIdPart

URL-encode `scriptIdPart`: encode `%` **first**, then `;`
(`%` -> `%25`, then `;` -> `%3B`). Then:

```bash
curl -s -A 'Mozilla/5.0' \
  "https://pine-facade.tradingview.com/pine-facade/get/<ENCODED_ID>/last" \
  -o out.json
```

Response is JSON: `{"source":"<FULL PINE SOURCE>", "scriptName":..., "version":...}`.
Write **only** the decoded `source` string to the `.pine` file — decode the JSON
properly (Python's `json` module), do **not** `sed`; the source contains real `\n`.

**Verified examples that return HTTP 200:**

| Library | ENCODED_ID | Notes |
|---|---|---|
| `TradingView/ta` | `PUB%3B77c0f0012daa4ff09d68b6f3bed95a7f` | 45,228 B at `last` (v21); contains `relativeVolume` |
| `TradingView/RelativeValue` | `PUB%3BLIB_TradingView_RelativeValue` | ~9,148 B; contains `averageAtTime` |

**Version-pinned fetch** (the suite pins `import TradingView/ta/7`): append the
version number instead of `last`:

```bash
curl -s -A 'Mozilla/5.0' \
  "https://pine-facade.tradingview.com/pine-facade/get/PUB%3B77c0f0012daa4ff09d68b6f3bed95a7f/7" \
  -o ta_v7.json
```

`ta/7`, `ta/6`, `ta/5` all return HTTP 200 (31,339 B each) and `ta/7` contains
`relativeVolume`. The exact pinned version IS retrievable — parity does not have to
reconcile a v7-vs-v21 gap by chart comparison, though that fallback remains available.

---

## Redundancy mirrors (Anish's standing rule: multiple copies)

The canonical vault and **two git mirrors** are kept in sync on every refresh:

| Role | Path |
|---|---|
| **Canonical (OWC drive)** | `/Volumes/OWC Envoy Ultra/TradingDataSystem/sources/tradingview/pine_libraries/` |
| **Mirror A (Python port spec)** | `/Users/anishpatel/code/anish/realtime-indicators/vendor/pine_libraries/` |
| **Mirror B (Pine suite repo)** | `/Users/anishpatel/code/anish/indicators/vendor/pine_libraries/` |

GitHub:
- https://github.com/nishpa800/realtime-indicators/tree/main/vendor/pine_libraries
- https://github.com/nishpa800/indicators/tree/main/vendor/pine_libraries

---

## Daily auto-update (launchd)

- **Updater:** `update_pine_libraries.sh` (in this directory). Idempotent. Re-runs
  STEP A + STEP B for every entry in `manifest.json`, overwrites `raw/`, recomputes
  sha256, rewrites the manifest with a fresh `fetched_utc`, logs to `logs/`, and —
  **only if any sha256 changed** — copies into both git mirrors and commits/pushes.
  If the OWC drive is unmounted it logs a note to `~/Library/Logs/` and exits 0
  (an unmounted drive is not an error).
- **launchd agent:** `~/Library/LaunchAgents/com.anish.pinelibvault.plist`
  (Label `com.anish.pinelibvault`), fires daily at **06:30 CT**, `RunAtLoad false`.
- A `.fetch.lock` file in this directory guards against overlapping runs.

Manual run / verify:

```bash
/bin/bash "/Volumes/OWC Envoy Ultra/TradingDataSystem/sources/tradingview/pine_libraries/update_pine_libraries.sh"
launchctl list | grep pinelibvault
```
