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
    # v2 "instrument" look: deeper ink panel, phosphor green for verified things, amber accent kept.
    "dark": dict(
        panel="#0b0f14", line="#263040", grid="#161c25", fg="#e8edf2", muted="#8b96a3",
        subtle="#59636f", accent="#f2b33d", ok="#4ade80", bad="#ff6b6b", blue="#38bdf8",
        glow=0.22, sheen=0.07,
    ),
    "light": dict(
        panel="#fbfaf7", line="#d6dbe2", grid="#eceff3", fg="#1b1f24", muted="#5a6472",
        subtle="#8a94a0", accent="#b35900", ok="#1a7f37", bad="#cf222e", blue="#0969da",
        glow=0.055, sheen=0.05,
    ),
}

# expo-out for entrances, linear only for things that represent clock time.
EASE = "cubic-bezier(.16,1,.3,1)"
EASE_IO = "cubic-bezier(.65,0,.35,1)"


def chrome(T, W: int, H: int, rx: int = 14, glow_at=(0.82, 0.1), strength: float = 1.0) -> tuple[str, str, str]:
    """Shared panel chrome: fine grid, accent glow, drawn border, corner ticks, one sheen pass.

    Returns (defs, background_body, css). Put `defs` first, `background_body` right after,
    and append `css`. Ids are prefixed `k-` so they never collide with per-image ids.
    """
    gx, gy = W * glow_at[0], H * glow_at[1]
    defs = (
        '<defs>'
        f'<pattern id="k-grid" width="24" height="24" patternUnits="userSpaceOnUse">'
        f'<path d="M24,0 H0 V24" stroke="{T["grid"]}" stroke-width="1"/></pattern>'
        f'<radialGradient id="k-glow" gradientUnits="userSpaceOnUse" cx="{gx:.0f}" cy="{gy:.0f}" r="{W * 0.42:.0f}">'
        f'<stop offset="0" stop-color="{T["accent"]}" stop-opacity="{T["glow"] * strength:.3f}"/>'
        f'<stop offset="1" stop-color="{T["accent"]}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="k-sheen" x1="0" x2="1"><stop offset="0" stop-color="{T["fg"]}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{T["fg"]}" stop-opacity="{T["sheen"]}"/>'
        f'<stop offset="1" stop-color="{T["fg"]}" stop-opacity="0"/></linearGradient>'
        '<filter id="k-blur" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="3"/></filter>'
        '<filter id="k-blur2" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="7"/></filter>'
        f'<clipPath id="k-frame"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="{rx}"/></clipPath>'
        '</defs>'
    )
    tick = 10
    corners = "".join(
        f'<path class="k-tick" style="animation-delay:{.5 + i * .06:.2f}s" d="{d}" stroke="{T["accent"]}" stroke-width="1.5" stroke-opacity=".8"/>'
        for i, d in enumerate([
            f"M{12},{12 + tick} V12 H{12 + tick}",
            f"M{W - 12 - tick},12 H{W - 12} V{12 + tick}",
            f"M{W - 12},{H - 12 - tick} V{H - 12} H{W - 12 - tick}",
            f"M{12 + tick},{H - 12} H12 V{H - 12 - tick}",
        ])
    )
    body = (
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="{rx}" fill="{T["panel"]}"/>'
        '<g clip-path="url(#k-frame)">'
        f'<rect class="k-fade" width="{W}" height="{H}" fill="url(#k-grid)"/>'
        f'<rect class="k-fade" style="animation-delay:.2s" width="{W}" height="{H}" fill="url(#k-glow)"/>'
        f'<rect class="k-sheen" x="{-W * .35:.0f}" y="-40" width="{W * .35:.0f}" height="{H + 80}" fill="url(#k-sheen)" transform="skewX(-18)"/>'
        '</g>'
        f'<rect class="k-edge" pathLength="1" stroke-dasharray="1" x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="{rx}" stroke="{T["line"]}"/>'
        f"{corners}"
    )
    css = (
        f".k-fade{{animation:k-fade 1.1s {EASE} both}}@keyframes k-fade{{from{{opacity:0}}}}"
        f".k-edge{{animation:k-edge 1.4s {EASE_IO} both}}@keyframes k-edge{{from{{stroke-dashoffset:1}}}}"
        f".k-tick{{transform-box:fill-box;transform-origin:center;animation:k-tick .5s {EASE} both}}"
        "@keyframes k-tick{from{opacity:0;transform:scale(.4)}}"
        f".k-sheen{{opacity:0;animation:k-sheen 1.5s {EASE_IO} .55s both}}"
        f"@keyframes k-sheen{{0%{{opacity:0;transform:skewX(-18deg) translateX(0)}}20%{{opacity:1}}80%{{opacity:1}}"
        f"100%{{opacity:0;transform:skewX(-18deg) translateX({W * 1.45:.0f}px)}}}}"
    )
    return defs, body, css

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
    "THEMES", "EASE", "chrome", "tr", "set_lang", "is_cjk", "text_w", "tc_attr", "ZH", "EASE_IO", "esc", "mono_w", "document", "write", "text",
    "smooth_path", "poly", "clamp", "math", "ROOT", "ASSETS",
]
