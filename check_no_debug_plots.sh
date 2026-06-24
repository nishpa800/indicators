#!/usr/bin/env bash
# CONSTITUTIONAL GATE -- DEFAULT-DENY on diagnostic plot() lines.
#
# WHY: diagnostic / numeric plot() readouts (counts, sums, scores, ratios, bool->int
# exports) clutter the TradingView Style/Settings tab with one row per plot. They must
# NOT be added to a study unless the user EXPLICITLY asked for that exact series.
# This gate is DEFAULT-DENY: you do not opt IN, you must opt OUT.
#
# RULES (per .pine file):
#   * DEFAULT (no marker): any plot() written to display.data_window or display.none
#     is a DIAGNOSTIC readout -> VIOLATION. (Catches the offender by default, everywhere.)
#   * // NO-DEBUG-PLOTS  (detection-only studies): tightens it -- ANY plot( is a violation
#     (these emit ONLY plotshape markers).
#   * // ALLOW-DEBUG-PLOTS  (legacy fire-matrix exporters ONLY): the single escape hatch;
#     the file may intentionally export numeric series for the offline Python fire-matrix.
#
# hooks/pre-commit runs this on STAGED *.pine only, so untouched legacy files are never
# nagged; the moment a file is edited it must be clean or carry an explicit marker.
#
# Usage: check_no_debug_plots.sh [file_or_dir ...]   (default: all *.pine under cwd)
# Exit 0 = clean; exit 1 = violations.
set -u
ANY_PLOT='^[[:space:]]*plot\('
DIAG_PLOT='^[[:space:]]*plot\(.*display\.(data_window|none)'
targets=("$@"); [ ${#targets[@]} -eq 0 ] && targets=(.)
fail=0
while IFS= read -r f; do
  [ -f "$f" ] || continue
  if grep -q 'ALLOW-DEBUG-PLOTS' "$f" 2>/dev/null; then
    continue                                                  # explicit opt-out (legacy exporter)
  elif grep -q 'NO-DEBUG-PLOTS' "$f" 2>/dev/null; then
    pat="$ANY_PLOT"; why="detection-only (NO-DEBUG-PLOTS): no plot( ) allowed at all"
  else
    pat="$DIAG_PLOT"; why="DEFAULT-DENY: diagnostic plot( ) to display.data_window/none"
  fi
  hits=$(grep -nE "$pat" "$f" 2>/dev/null)
  if [ -n "$hits" ]; then
    fail=1
    echo "DIAGNOSTIC PLOT VIOLATION in $f"
    echo "   reason: $why"
    echo "$hits" | sed 's/^/   /'
  fi
done < <(for t in "${targets[@]}"; do [ -d "$t" ] && find "$t" -name '*.pine' || echo "$t"; done)
if [ "$fail" = 0 ]; then
  echo "PASS: no diagnostic plot( ) violations."
else
  echo "FAIL: delete the plot( ) lines above. Use plotshape() for detections; keep aggregates UNPLOTTED."
  echo "      Only a legacy fire-matrix exporter may carry // ALLOW-DEBUG-PLOTS to opt out."
fi
exit $fail
