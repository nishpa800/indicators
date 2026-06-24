#!/usr/bin/env bash
# CONSTITUTIONAL GATE -- detection-only studies must NOT carry numeric/count/debug
# plot() lines. They clutter the TradingView Style/Settings tab (every plot() gets
# its own row). A file OPTS IN to this gate by carrying the marker  NO-DEBUG-PLOTS
# near the top. In a marked file, ANY plot( call is a violation -- use plotshape()
# for detection markers and keep aggregates as UNPLOTTED export variables.
#
# Legacy studies that legitimately export 0/1 series via plot(...display.data_window)
# for the offline Python fire-matrix simply DO NOT carry the marker, so they are
# untouched by this gate.
#
# Usage: check_no_debug_plots.sh [file_or_dir ...]   (default: all *.pine under cwd)
# Exit 0 = clean; exit 1 = violations found.
set -u
MARKER='NO-DEBUG-PLOTS'
PLOTCALL='^[[:space:]]*plot\('
targets=("$@"); [ ${#targets[@]} -eq 0 ] && targets=(.)
fail=0
checked=0
while IFS= read -r f; do
  [ -f "$f" ] || continue
  grep -q "$MARKER" "$f" 2>/dev/null || continue   # only marked (detection-only) files are gated
  checked=$((checked+1))
  hits=$(grep -nE "$PLOTCALL" "$f" 2>/dev/null)
  if [ -n "$hits" ]; then
    fail=1
    echo "DEBUG/COUNT PLOT VIOLATION in $f (file is marked $MARKER -> detection-only):"
    echo "$hits" | sed 's/^/   /'
  fi
done < <(for t in "${targets[@]}"; do [ -d "$t" ] && find "$t" -name '*.pine' || echo "$t"; done)
if [ "$fail" = 0 ]; then
  echo "PASS: no debug/count plot() in detection-only (marked) files. (checked $checked marked file(s))"
else
  echo "FAIL: delete the plot() lines above. Use plotshape() for detections; keep aggregates UNPLOTTED."
fi
exit $fail
