#!/usr/bin/env python3
"""Fork a Pine source into a tick-safe variant.

Usage: python3 tick_safe_fork.py <src.pine> <dest.pine>

Rules applied (idempotent — safe to re-run):
  * Drop `import TradingView/ta/7 as tv_ta` line.
  * Insert the tick-safe shim block right after the `indicator(...)` call.
  * Rename indicator title → "<title> (tick-safe)" and shorttitle → "<x> tk".
  * Replace `time("D")` → `_dayKey()` everywhere.
  * Replace `tv_ta.relativeVolume(L, A, C, R)` → `_rvol(L, C)`.
  * Wrap `timeframe.in_seconds(...)` with `nz(..., 60)` (skips already-wrapped).
"""
import re
import sys
from pathlib import Path

SHIM = """
// ═══ TICK-SAFE SHIM ═══════════════════════════════════════════════════════════
// Replaces time("D") and tv_ta.relativeVolume() — both throw RE10023 on tick
// charts. See tick-compatible/README.md for the full conversion contract.
_dayKey() => year * 10000 + month * 100 + dayofmonth
_rvol(simple int length, simple bool cumulative) =>
    bool _isNew = ta.change(_dayKey()) != 0
    var float _cum = 0.0
    _cum := (_isNew or bar_index == 0) ? volume : _cum + volume
    float _cur = cumulative ? _cum : volume
    float _avg = ta.sma(_cur, math.max(length, 1))
    [_cur, _avg, _isNew]
// ═════════════════════════════════════════════════════════════════════════════
"""


def find_indicator_call_end(src: str) -> int:
    """Return char position just after the closing `)` of the first `indicator(...)` call."""
    m = re.search(r"^\s*indicator\(", src, re.MULTILINE)
    if not m:
        return -1
    i = m.end()
    depth = 1
    in_str = False
    while i < len(src) and depth > 0:
        c = src[i]
        if in_str:
            if c == '"' and src[i - 1] != "\\":
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
        i += 1
    return i


def patch_title(src: str) -> str:
    """Add ' (tick-safe)' to first string arg of indicator() and ' tk' to shorttitle."""
    end = find_indicator_call_end(src)
    if end < 0:
        return src
    head = src[:end]
    tail = src[end:]

    m = re.search(r"indicator\(", head)
    body = head[m.end() : -1]  # arguments without surrounding parens

    if "(tick-safe)" not in body:
        body = re.sub(r'"([^"]*)"', lambda mm: '"' + mm.group(1) + ' (tick-safe)"', body, count=1)
    if " tk" not in body:
        body = re.sub(r'shorttitle\s*=\s*"([^"]*)"', lambda mm: 'shorttitle="' + mm.group(1) + ' tk"', body)

    return head[: m.end()] + body + ")" + tail


def split_args(s: str) -> list[str]:
    parts, depth, buf, in_str = [], 0, "", False
    for c in s:
        if in_str:
            buf += c
            if c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
            buf += c
        elif c == "," and depth == 0:
            parts.append(buf.strip())
            buf = ""
        else:
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            buf += c
    if buf.strip():
        parts.append(buf.strip())
    return parts


def replace_relvol(src: str) -> str:
    pattern = re.compile(r"tv_ta\.relativeVolume\((.*?)\)", re.DOTALL)

    def repl(m: re.Match) -> str:
        args = split_args(m.group(1))
        if len(args) >= 3:
            return f"_rvol({args[0]}, {args[2]})"
        return m.group(0)

    return pattern.sub(repl, src)


def wrap_tf_in_seconds(src: str) -> str:
    out, i, n = [], 0, len(src)
    needle = "timeframe.in_seconds("
    while i < n:
        j = src.find(needle, i)
        if j < 0:
            out.append(src[i:])
            break
        out.append(src[i:j])
        depth = 1
        k = j + len(needle)
        while k < n and depth > 0:
            if src[k] == "(":
                depth += 1
            elif src[k] == ")":
                depth -= 1
            k += 1
        call = src[j:k]
        already_wrapped = src[max(0, j - 3) : j] == "nz("
        if already_wrapped:
            out.append(call)
        else:
            out.append(f"nz({call}, 60)")
        i = k
    return "".join(out)


def patch(src: str) -> str:
    src = re.sub(r"^import\s+TradingView/ta/7\s+as\s+tv_ta\s*\n", "", src, flags=re.MULTILINE)
    src = patch_title(src)
    src = src.replace('time("D")', "_dayKey()")
    src = replace_relvol(src)
    src = wrap_tf_in_seconds(src)
    end = find_indicator_call_end(src)
    if end > 0:
        nl = src.find("\n", end)
        if nl < 0:
            nl = end - 1
        if "TICK-SAFE SHIM" not in src:
            src = src[: nl + 1] + SHIM + src[nl + 1 :]
    return src


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    src_path = Path(sys.argv[1])
    dest_path = Path(sys.argv[2])
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(patch(src_path.read_text()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
