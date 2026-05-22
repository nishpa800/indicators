# FAILURE_MODES

Append-only ledger of failure modes the COT has encountered. Each entry
documents what happened, why, and the recovery path the operator must
unblock.

---

## FM-001 — Canonical fetch blocked by repo access (2026-05-11)

**Situation.** Operator instructed the COT to fetch 11 canonical
bootstrap files from `nishpa800/Google-Studio` branch `cot` via raw
URLs of the form
`https://raw.githubusercontent.com/nishpa800/Google-Studio/cot/COT/...`.

**What happened.** All 11 fetches returned HTTP 404 with the error
message hint *"If this URL requires authentication, use an authenticated
tool"*.

**Why.** This session has two paths to GitHub content:

1. **`WebFetch`** — anonymous. Returns 404 on private repos. Currently
   failing on all `nishpa800/Google-Studio` URLs.
2. **GitHub MCP server** (`mcp__github__*`) — hard-restricted by the
   session's system prompt to `nishpa800/indicators` only. Quote:
   *"Do NOT attempt to read from, write to, or interact with any other
   repository. Calls targeting repositories outside this list will be
   denied."*

The two tools are mutually exclusive: WebFetch cannot read private
repos; GitHub MCP cannot read non-`nishpa800/indicators` repos. The
Google-Studio repo falls between them.

**Impact.** The canonical COT/ files (NORTH_STAR, GENIE_MANIFESTO,
GENIE_RESPONSIBILITIES, instruction 00_master / 00_portability /
14_no_friction / 15_no_diagnostic_labels / 16_anti_shortcut /
19_universal_cross_connection, STRAIGHT_LINE, on_frustration_detected,
SYNONYMS, etc.) cannot be pulled into this session. The local
scaffolded versions at commit `0119656` are in use as a fallback —
they reproduce the bootstrap message's intent but may differ from the
operator's canonical wording, structure, and any nested references.

**Recovery (operator must choose one).**

- **(a)** Make `nishpa800/Google-Studio` public — `WebFetch` then
  succeeds against the raw URLs and the canonical supersedes the
  local scaffold automatically.
- **(b)** Mirror the canonical `COT/` tree into `nishpa800/indicators`
  (this branch or a dedicated `cot-canonical` branch) — the GitHub
  MCP can then read it.
- **(c)** Paste the canonical file contents inline in the next
  message — the COT writes them to disk verbatim, overwriting the
  scaffolded versions.
- **(d)** Provide alternative raw URLs (gist, public mirror) that
  `WebFetch` can reach anonymously.

Until one of (a)–(d) is in place, the local scaffold at commit
`0119656` is what the COT reads each turn. Future amendments the
operator pushes to `nishpa800/Google-Studio` will NOT be picked up
until access is resolved.

---
