"""One-off: cut the Noto Sans TC subset that CI uses (Actions runners have no CJK fonts).

Collects every non-ASCII character in scripts/*.py plus printable ASCII, keeps the
weight axis, and writes fonts/NotoSansTC-subset.woff2 (OFL). Rerun after adding new
Chinese strings: `python scripts/make_cjk_font.py path/to/NotoSansTC-VF.ttf`.
"""
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

here = Path(__file__).parent
chars = {chr(c) for c in range(0x20, 0x7F)}
for p in here.glob("*.py"):
    chars |= {c for c in p.read_text(encoding="utf-8") if ord(c) > 0x7F}
chars |= set("一二三四五六七八九十")
src = sys.argv[1] if len(sys.argv) > 1 else "C:/Windows/Fonts/NotoSansTC-VF.ttf"
font = TTFont(src)
opts = subset.Options()
opts.flavor = "woff2"
opts.layout_features = ["*"]
s = subset.Subsetter(opts)
s.populate(unicodes=[ord(c) for c in chars])
s.subset(font)
font.flavor = "woff2"
out = here / "fonts" / "NotoSansTC-subset.woff2"
font.save(out)
print(out, out.stat().st_size, "bytes,", len(chars), "chars")
