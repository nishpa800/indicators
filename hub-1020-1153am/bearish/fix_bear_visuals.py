#!/usr/bin/env python3
"""
Bear-mirror VISUAL + ALERT differentiation pass (run AFTER build_bear_mirror.py).

Four mandates so bull and bear are never confusable side-by-side:
  1. TITLE   : append " Bear" to every detection-plot title.
  2. LOCATION: flip every plot location (abovebar<->belowbar, top<->bottom).
  3. COLOR   : remap every FILL color to a warm/opposite bear palette distinct
               from the bull's (textcolor left intact for readability).
  4. ALERTS  : append " Bear" to every alertcondition name + message, every
               multiplexer signal name, and prefix the aggregate alert "BEAR".

Non-structural: only string contents, color values, and location enums change.
"""
import re
import pathlib

F = pathlib.Path(__file__).resolve().parent / "HUB_1020_1153am_BEAR_Hub1020-Bear_v20260613_bearish_mirror.pine"

# bull fill color -> bear fill color: warm, reads bear, and DISTINCT from the bull's
CMAP = {
    "white": "color.red", "lime": "color.orange", "green": "color.maroon",
    "teal": "color.maroon", "aqua": "color.orange", "blue": "color.orange",
    "purple": "color.rgb(199, 0, 57)", "fuchsia": "color.rgb(255, 82, 82)",
    "yellow": "color.rgb(178, 34, 34)", "red": "color.rgb(255, 87, 34)",
    "orange": "color.rgb(178, 34, 34)", "maroon": "color.rgb(255, 69, 0)",
    "silver": "color.rgb(205, 92, 92)", "gray": "color.rgb(165, 42, 42)",
}
_CNAMES = "|".join(CMAP)


def swap_location(s):
    s = (s.replace("location.abovebar", "\x00A")
          .replace("location.belowbar", "location.abovebar")
          .replace("\x00A", "location.belowbar"))
    s = (s.replace("location.top", "\x00T")
          .replace("location.bottom", "location.top")
          .replace("\x00T", "location.bottom"))
    return s


def recolor_fill(s):
    s = s.replace("textcolor=color.", "textcolor=\x00C.")          # protect text color
    s = re.sub(r"color\.(" + _CNAMES + r")\b", lambda m: CMAP[m.group(1)], s)
    s = s.replace("textcolor=\x00C.", "textcolor=color.")
    s = s.replace("#CD853F", "#B22222")                             # custom B hex -> firebrick
    return s


def append_first_string(s, suffix=" Bear"):
    return re.sub(r'"([^"]*)"', lambda m: '"' + m.group(1) + suffix + '"', s, count=1)


counts = {"plot": 0, "alertcond": 0, "galert": 0, "emit": 0, "agg": 0}
out = []
for ln in F.read_text().split("\n"):
    st = ln.lstrip()
    if st.startswith("plotshape(") or st.startswith("plotchar("):
        ln = recolor_fill(swap_location(append_first_string(ln)))
        counts["plot"] += 1
    elif st.startswith("alertcondition("):
        ln = append_first_string(ln)                                   # name + Bear
        ln = ln.replace(" on {{ticker}}", " Bear on {{ticker}}")       # message + Bear
        counts["alertcond"] += 1
    elif "_galert_msg := _galert_msg +" in ln and ln.rstrip().endswith('"'):
        ln = re.sub(r'"([^"]*)"(\s*)$', r'"\1 Bear"\2', ln)            # trailing signal name + Bear
        counts["galert"] += 1
    elif st.startswith('alert("Signals: "'):
        ln = ln.replace('"Signals: "', '"BEAR Signals: "')             # aggregate alert
        counts["agg"] += 1
    elif re.match(r'\s*alert\("[^"]+ " \+ alert_base_string', ln):
        ln = re.sub(r'alert\("([^"]+) " \+', r'alert("\1 Bear " +', ln)  # per-signal emit + Bear
        counts["emit"] += 1
    out.append(ln)

src = "\n".join(out)
# signals carried as variables, not inline strings -> patch at their definition:
src = src.replace('"RVOL D>Th (Value: "', '"RVOL D>Th Bear (Value: "')   # rvol_name_full (build + emit)
src = src.replace('input.color(color.new(color.yellow, 60), "Signal Color"',
                  'input.color(color.new(color.rgb(199, 0, 57), 60), "Signal Color"')  # FC Cluster fill default

F.write_text(src)
print("EDITS:", counts)
