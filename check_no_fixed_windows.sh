#!/usr/bin/env bash
# CONSTITUTIONAL GATE — fixed/anchored windows are disallowed. Every window/lookback-bar
# detection must be ROLLING (sliding trailing-N via f_sum_true / f_rolling_sum, leading-edge fire,
# gated on barstate.isconfirmed). The BANNED antipattern is an anchored window that waits N bars:
#   var int xStartBar ... if bar_index - xStartBar >= len: reset
# Usage: check_no_fixed_windows.sh [file_or_dir ...]   (default: all *.pine under cwd)
# Exit 0 = clean; exit 1 = violations found.
set -u
ANTIPATTERN='bar_index - [A-Za-z0-9_]*[Ss]tart[A-Za-z0-9_]* >=|var int [A-Za-z0-9_]*[Ss]tartBar'
targets=("$@"); [ ${#targets[@]} -eq 0 ] && targets=(.)
fail=0
while IFS= read -r f; do
  hits=$(grep -nE "$ANTIPATTERN" "$f" 2>/dev/null)
  if [ -n "$hits" ]; then
    fail=1
    echo "FIXED-WINDOW VIOLATION in $f:"
    echo "$hits" | sed 's/^/   /'
  fi
done < <(for t in "${targets[@]}"; do [ -d "$t" ] && find "$t" -name '*.pine' || echo "$t"; done)
[ "$fail" = 0 ] && echo "PASS: no fixed/anchored windows found." || echo "FAIL: convert the above to rolling (f_sum_true/f_rolling_sum sliding windows)."
exit $fail
