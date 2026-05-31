# Pine v6-to-v5 Backport Audit

Date: 2026-05-31 CST
Scope: normalized Pine v5 copies only under `imports/20260531T103840_indicator_studies/pine_v5/`.

## Input -> Processing -> Output

Input: `anish_tb_foster_fix.pine`, `ultra_combo_v57_shorttitle_ultra_v57.pine`, `vob_asym_t3_x6_mutex_lines_claude_v10.pine`.

Processing: static Pine v5 compatibility scan for v6-only or v5-invalid constructs, focused on syntax that would block TradingView Pine v5 compilation. The scan checked version headers, common v6-only parameters/namespaces, case-sensitive `barstate.isconfirmed`, and comma-separated declaration/statement patterns.

Output: patched normalized Pine v5 copies plus this audit report. Originals outside this import folder were not touched.

## Seven-Pillar Assessment

Problem Solving: make the three normalized copies more likely to compile under Pine v5 without changing trading logic.

Critical Thinking: only safe mechanical edits were applied. Runtime behavior that needs Pine semantic intent was documented instead of guessed.

Cryptography: the hidden structure decoded here is syntax provenance: Pine v6/normalized-source artifacts versus Pine v5-legal statements.

Advanced Computer Modeling: no Python modules or conversion architecture files were modified.

Advanced Statistical Modeling: not applicable to this static backport audit; no signal behavior, thresholds, or detection outputs were changed.

Neuro-Linguistics: labels such as "compile blocker" are reserved for syntax patterns expected to stop Pine v5 compilation. Runtime risks are labeled separately.

Game Theory: the adversarial failure mode is a script that appears v5-normalized but fails during TradingView compile/add-to-chart, delaying parity work.

Synthesis: the decisive compile-blocking pattern found was comma-separated declarations/statements. I split those into independent Pine statements and left semantic-risk code untouched.

## File Findings

### `anish_tb_foster_fix.pine`

Version header: `//@version=5`.

Compile risks found:
- Lines 19 and 21 used comma-separated typed declarations.

Edits made:
- Split `ema50`, `ema150`, `ema200`, `w52Hi`, and `w52Lo` into separate typed declarations.

Remaining risks:
- No v6-only syntax found in the static scan.

### `ultra_combo_v57_shorttitle_ultra_v57.pine`

Version header: `//@version=5`.

Compile risks found:
- Array side-effect calls used comma-separated statements in the b1/b4 overlap queues.
- The top comment still mentions "UPGRADED TO v6"; this is documentation text only, not executable syntax.
- A comment says `barstate.isConfirmed`; executable code uses `barstate.isconfirmed`.

Edits made:
- Split comma-separated `array.shift()` and `array.push()` calls into one statement per line.

Remaining risks:
- No executable v6-only syntax found in the static scan.
- Still requires TradingView compile because imported library `TradingView/ta/7` and runtime resources are resolved by TradingView, not local shell tooling.

### `vob_asym_t3_x6_mutex_lines_claude_v10.pine`

Version header: `//@version=5`.

Compile risks found:
- Multiple comma-separated typed declarations in the VOB metrics block.
- Comma-separated `clear()` and `push()` side-effect statements.

Edits made:
- Split all identified comma-separated declarations/statements in the audited regions into one Pine statement per line.

Remaining risks:
- Lines now around 564 and 577 still call `lo_lvl.get(i - 1)` and `up_lvl.get(i - 1)` inside loops that start at `i = 0`. This is not a v5 compile syntax blocker, but it can be a Pine runtime array-index failure on the first loop iteration. I did not patch it because the intended first-element comparison behavior is semantic, not mechanical.
- The script uses Pine logs, alerts, linefills, user-defined types, and array methods. These are Pine v5-supported constructs per TradingView v5 docs, but TradingView must still compile/run the script to confirm library/runtime limits.

## Verification Run

Commands run:

```bash
./hooks/pine_to_python_intelligence_gate.sh
rg -n "version=6|isConfirmed|timeframe\\.main_period|\\binput\\.[a-z]+\\([^\\n]*active\\s*=|dynamic_requests\\s*=|request\\.seed|chart\\.point|polyline\\.|force_overlay\\s*=|behind_chart\\s*=|\\bvarip\\b|array\\.first\\(|array\\.last\\(" <three target files>
rg -n "\\.get\\(\\s*[^)]*-\\s*1\\s*\\)|array\\.get\\([^,]+,\\s*[^)]*-\\s*1\\s*\\)" <three target files>
git diff --check -- <three target files>
```

Result:
- Intelligence gate passed with run id `20260531T000746`.
- `git diff --check` passed.
- v6-only executable syntax scan found no actionable executable v6-only constructs after edits.
- Runtime index-risk scan found the two VOB `get(i - 1)` cases documented above.

## TradingView Compile Checks Required

1. Open each normalized copy in TradingView Pine Editor with Fast Calculation OFF.
2. Confirm Pine Editor compile succeeds under `//@version=5`.
3. Add each indicator to a chart without changing the immutable chart indicator stack unless this is done in a disposable/test chart.
4. For VOB, test runtime on at least 1m and 5m charts because the remaining `get(i - 1)` pattern may only surface after arrays populate.
5. Capture any Pine Editor error line numbers and route them back to this import folder before Python conversion/parity work.
