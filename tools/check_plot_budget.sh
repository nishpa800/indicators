#!/usr/bin/env bash
# ============================================================================
# Pine plot-budget guardrail.
# ----------------------------------------------------------------------------
# Why this exists: TradingView caps a script at 64 plot-objects. EVERY plot-
# family call counts toward it — including plot(..., display=display.data_window),
# which draws nothing on the chart but still burns budget AND litters the Style
# tab with junk blue lines. Shipping a "numeric data-window fire matrix" of
# dozens of such plots blew ULTRA 57 past the ceiling -> RE10140 (2026-06-13).
#
# This script FAILS (exit 1) if any .pine file:
#   (a) exceeds the 64 plot-object budget (plot-family + alertcondition), or
#   (b) contains ANY display.data_window plot (banned — use log.info() instead,
#       which does NOT count against the limit).
#
# Usage:  tools/check_plot_budget.sh [file.pine ...]   (default: all tracked .pine)
# Run it before declaring any Pine deliverable "done".
# ============================================================================
set -uo pipefail
LIMIT=64
fail=0

files=("$@")
if [ ${#files[@]} -eq 0 ]; then
    # Default scope = the deliverable surface (what gets loaded into TradingView):
    # every tick-friendly build. Verbatim imports/ and vendor/ libraries are
    # read-only references and intentionally excluded. Pass explicit file args to
    # check anything else (e.g. a versions/ file before promoting it).
    mapfile -t files < <(git ls-files '*.pine' | grep -E 'tick_friendly|(^|/)dateroll/')
fi

printf "%-68s %6s %6s  %s\n" "FILE" "PLOTS" "DWIN" "STATUS"
printf -- '-%.0s' {1..96}; echo
for f in "${files[@]}"; do
    [ -f "$f" ] || continue
    # Count only real code — drop full-line comments first.
    code=$(grep -vE '^[[:space:]]*//' "$f")
    pf=$(printf '%s\n' "$code" | grep -cE '(^|[^a-zA-Z_.])(plot|plotshape|plotchar|plotarrow|plotcandle|plotbar)\(')
    ac=$(printf '%s\n' "$code" | grep -cE 'alertcondition\(')
    dw=$(printf '%s\n' "$code" | grep -cE 'display[[:space:]]*=[[:space:]]*display\.data_window')
    tt=$(printf '%s\n' "$code" | grep -cE 'time(_close)?\(timeframe\.period,')
    ba=$(printf '%s\n' "$code" | grep -cE 'relativeVolume\([^,]+,[[:space:]]*""')
    tot=$((pf + ac))
    status="ok"
    if [ "$tot" -gt "$LIMIT" ]; then status="OVER-64 ($tot)"; fail=1; fi
    if [ "$dw" -gt 0 ]; then status="$status DATA_WINDOW-BANNED"; fail=1; fi
    if [ "$tt" -gt 0 ]; then status="$status RE10023-time(tf)"; fail=1; fi
    if [ "$ba" -gt 0 ]; then status="$status RE10023-blank-anchor"; fail=1; fi
    printf "%-68s %6s %6s  %s\n" "${f#./}" "$tot" "$dw" "$status"
done

echo
if [ "$fail" -eq 0 ]; then
    echo "PASS — within 64-plot budget; zero data_window plots; zero RE10023 patterns (time(timeframe.period,…) or blank relativeVolume anchor)."
else
    echo "FAIL — fix the files flagged above (plots>64 / data_window / time(timeframe.period,…) / blank relativeVolume anchor)."
fi
exit "$fail"
