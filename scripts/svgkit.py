"""Shared helpers for the profile SVGs: themes, font embedding, small geometry utils.

Every SVG is rendered by GitHub inside an <img>, so: no scripts, no external
requests, no hover. Fonts are subset and inlined as base64 WOFF2, and all motion
is CSS keyframes (so `prefers-reduced-motion` can switch it off). The un-animated
state of every element is its final state, so a frozen frame is still complete.
"""
from __future__ import annotations

import base64
import html
import io
import math
import os
import re
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "scripts" / "fonts"
ASSETS = ROOT / "assets"

THEMES = {
    "dark": dict(
        panel="#0d1117", line="#30363d", grid="#21262d", fg="#e6edf3", muted="#9198a1",
        subtle="#656c76", accent="#f2b33d", ok="#3fb950", bad="#f85149", blue="#58a6ff",
    ),
    "light": dict(
        panel="#ffffff", line="#d1d9e0", grid="#eef1f4", fg="#1f2328", muted="#59636e",
        subtle="#8c959f", accent="#b35900", ok="#1a7f37", bad="#cf222e", blue="#0969da",
    ),
}

# expo-out for entrances, linear only for things that represent clock time.
EASE = "cubic-bezier(.16,1,.3,1)"
EASE_IO = "cubic-bezier(.65,0,.35,1)"

MONO = "FC"  # Fira Code (OFL)
CJK = "TC"   # Noto Sans TC (OFL), only used for three glyphs in the hero

FIRA = {400: "FiraCode-Regular.ttf", 500: "FiraCode-Medium.ttf", 700: "FiraCode-Bold.ttf"}


LANG = "en"           # set by the builders; "zh" renders Traditional Chinese
ZH: dict[str, str] = {}  # English source string -> zh-TW, registered by each builder


def set_lang(lang: str) -> None:
    global LANG
    LANG = lang


def tr(s: str) -> str:
    return ZH.get(s, s) if LANG == "zh" else s


def is_cjk(s: str) -> bool:
    return any(ord(c) >= 0x2E80 for c in s)


def text_w(s: str, size: float) -> float:
    """Advance estimate: Fira Code is 0.6 em; CJK glyphs are 1 em."""
    return sum(size * (1.0 if ord(c) >= 0x2E80 else 0.6) for c in s)


def tc_attr() -> str:
    """class attribute for hand-built <text> elements that may hold translated tspans."""
    return ' class="tc"' if LANG == "zh" else ""


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def mono_w(text: str, size: float) -> float:
    """Fira Code advance is 600/1000 em for every glyph."""
    return len(text) * size * 0.6


def _subset_b64(path: Path, chars: str, wght: int | None = None) -> str:
    font = TTFont(str(path))
    if wght is not None and "fvar" in font:
        from fontTools.varLib import instancer
        font = instancer.instantiateVariableFont(font, {"wght": wght})
    cmap = font.getBestCmap()
    missing = {c for c in chars if ord(c) not in cmap and not c.isspace()}
    if missing:
        print(f"  ! {path.name} lacks glyphs: {''.join(sorted(missing))}")
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk"]
    opts.name_IDs = []
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=sorted({ord(c) for c in chars}))
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def _cjk_font() -> Path | None:
    for p in (FONT_DIR / "NotoSansTC-subset.woff2", FONT_DIR / "NotoSansTC-VF.ttf", Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "NotoSansTC-VF.ttf"):
        if p.exists():
            return p
    return None


TEXT_RE = re.compile(r"<text\b([^>]*)>(.*?)</text>", re.S)


def font_faces(body: str) -> str:
    """Collect rendered glyphs per family/weight from <text> nodes and inline subsets."""
    want: dict[tuple[str, int], set[str]] = {}
    for attrs, inner in TEXT_RE.findall(body):
        txt = html.unescape(re.sub(r"<[^>]+>", "", inner))
        fam = CJK if f'class="{CJK}' in attrs or " tc" in attrs or 'class="tc' in attrs else MONO
        m = re.search(r'font-weight="(\d+)"', attrs)
        w = int(m.group(1)) if m else 400
        if fam == MONO:
            w = min(FIRA, key=lambda k: abs(k - w))
        want.setdefault((fam, w), set()).update(txt)
    css = []
    for (fam, w), chars in sorted(want.items()):
        chars |= {" "}
        if fam == MONO:
            data = _subset_b64(FONT_DIR / FIRA[w], "".join(chars))
        else:
            p = _cjk_font()
            if not p:
                continue
            data = _subset_b64(p, "".join(chars), wght=w)
        css.append(
            f"@font-face{{font-family:{fam};font-weight:{w};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
        )
    return "".join(css)


BASE_CSS = (
    f"text{{font-family:{MONO},ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;"
    "font-variant-ligatures:contextual}"
    f".tc{{font-family:{CJK},'Noto Sans TC','PingFang TC','Microsoft JhengHei',sans-serif}}"
    ".fb{transform-box:fill-box}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)


def document(w: int, h: int, body: str, css: str, title: str, desc: str) -> str:
    faces = font_faces(body)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-labelledby="t d" fill="none">'
        f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>'
        f"<style>{faces}{BASE_CSS}{css}</style>{body}</svg>"
    )


def write(name: str, theme: str, svg: str) -> Path:
    ASSETS.mkdir(exist_ok=True)
    p = ASSETS / (f"{name}-zh-{theme}.svg" if LANG == "zh" else f"{name}-{theme}.svg")
    p.write_text(svg, encoding="utf-8", newline="\n")
    return p


def text(x, y, s, size=12, fill="fg", weight=400, anchor="start", cls="", extra="", T=None) -> str:
    color = T[fill] if T and fill in T else fill
    s = tr(s)
    if is_cjk(s):
        cls = f"{cls} tc".strip()
    c = f' class="{cls}"' if cls else ""
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{color}"{a}{c}{extra}>'
        f"{esc(s)}</text>"
    )


def smooth_path(pts: list[tuple[float, float]], k: float = 0.5) -> str:
    """Catmull-Rom through points, emitted as cubic Béziers."""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 3, p1[1] + (p2[1] - p0[1]) * k / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 3, p2[1] - (p3[1] - p1[1]) * k / 3)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def poly(pts) -> str:
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


__all__ = [
    "THEMES", "EASE", "tr", "set_lang", "is_cjk", "text_w", "tc_attr", "ZH", "EASE_IO", "esc", "mono_w", "document", "write", "text",
    "smooth_path", "poly", "clamp", "math", "ROOT", "ASSETS",
]
