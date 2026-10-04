"""Hero banner: split-flap name, typed intro, noise -> smoothed signal -> forecast band.

The band is drawn honestly wide (sigma * sqrt(h)), and one of the three "realized"
paths that loop inside it is chosen to poke out of the 95% band — which is what
a 95% band is supposed to let happen about one time in twenty.
"""
from __future__ import annotations

import random

from svgkit import EASE, EASE_IO, THEMES, document, esc, mono_w, poly, smooth_path, text, write

W, H = 840, 300
NAME = "Chi-Jiun Wong"
NAME_X, NAME_Y, NAME_SIZE = 44, 128, 46
LINES = [
    ("CS undergrad at NCU, minor in finance.", "fg"),
    ("I build forecasting experiments, verifiable-ML", "muted"),
    ("prototypes, and small bots that run on free tiers.", "muted"),
]
FLAP_GLYPHS = "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789#$%&*+<>=/?"


def bridge(n: int, rng: random.Random, sigma: float) -> list[float]:
    """Random walk pinned to 0 at both ends, so it tiles seamlessly."""
    w, s = [0.0], 0.0
    for _ in range(n):
        s += rng.gauss(0, sigma)
        w.append(s)
    return [w[i] - w[-1] * i / n for i in range(n + 1)]


def walk(n: int, rng: random.Random, sigma: float) -> list[float]:
    w, s = [0.0], 0.0
    for _ in range(n):
        s += rng.gauss(0, sigma)
        w.append(s)
    return w


def build(theme: str) -> str:
    T = THEMES[theme]
    css, body = [], []

    # ---- background: dot grid + scrolling noise traces (parallax) ----------------
    body.append(
        f'<defs><pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse">'
        f'<circle cx="1.5" cy="1.5" r="1" fill="{T["grid"]}"/></pattern>'
        f'<linearGradient id="scrim" gradientUnits="userSpaceOnUse" x1="0" x2="{W}" y1="0" y2="0">'
        f'<stop offset="0" stop-color="{T["panel"]}"/><stop offset=".58" stop-color="{T["panel"]}" stop-opacity=".95"/>'
        f'<stop offset=".71" stop-color="{T["panel"]}" stop-opacity="0"/></linearGradient>'
        f'<clipPath id="frame"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14"/></clipPath>'
        f'<clipPath id="flap"><rect x="{NAME_X-4}" y="{NAME_Y-40}" width="{mono_w(NAME, NAME_SIZE)+8}" height="54"/></clipPath>'
        f"</defs>"
    )
    body.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{T["panel"]}" stroke="{T["line"]}"/>')
    body.append('<g clip-path="url(#frame)">')
    body.append(f'<rect class="fade" style="animation-delay:0s" width="{W}" height="{H}" fill="url(#dots)"/>')

    rng = random.Random(7)
    step, n = 6, W // 6
    for i, (base, amp, dur, op) in enumerate([(160, 3.4, 70, 0.6), (196, 2.6, 95, 0.45), (128, 2.2, 130, 0.35)]):
        b = bridge(n, rng, amp)
        pts = [(k * step, base + b[k % n]) for k in range(2 * n + 1)]
        body.append(
            f'<g class="fade" style="animation-delay:{0.2 + i * 0.15:.2f}s">'
            f'<path class="drift" style="animation-duration:{dur}s" d="{poly(pts)}" '
            f'stroke="{T["subtle"]}" stroke-opacity="{op}" stroke-width="1"/></g>'
        )
    body.append(f'<rect width="{W}" height="{H}" fill="url(#scrim)"/>')

    # ---- signal: EMA of a walk, then a sqrt(h) fan --------------------------------
    x_start, x0, x1 = 520, 680, 812
    raw = walk(65, random.Random(11), 3.2)
    ema, e = [], raw[0]
    for v in raw:
        e = 0.82 * e + 0.18 * v
        ema.append(e)
    sig = [(x_start + i * (x0 - x_start) / (len(ema) - 1), 158 + 1.3 * (v - ema[-1])) for i, v in enumerate(ema)]
    y0 = 158.0
    C95 = 66
    body.append(
        f'<path class="draw" style="animation-delay:1.4s;animation-duration:1.6s" pathLength="1" '
        f'stroke-dasharray="1" d="{smooth_path(sig[::3] + [sig[-1]])}" stroke="{T["accent"]}" '
        f'stroke-width="2.2" stroke-linecap="round"/>'
    )

    def band(c: float) -> str:
        m = 24
        up = [(x0 + (x1 - x0) * k / m, y0 - c * (k / m) ** 0.5) for k in range(m + 1)]
        lo = [(x, 2 * y0 - y) for x, y in reversed(up)]
        return poly(up + lo) + "Z"

    body.append('<g class="cone fb" style="animation-delay:3s">')
    for c, op in [(C95, 0.10), (C95 * 0.66, 0.13), (C95 * 0.34, 0.18)]:
        body.append(f'<path d="{band(c)}" fill="{T["accent"]}" fill-opacity="{op}"/>')
    body.append(f'<path d="{band(C95)}" stroke="{T["accent"]}" stroke-opacity=".45" stroke-width="1" stroke-dasharray="2 3"/>')
    body.append("</g>")

    # three realized futures; #2 escapes the 95% band on purpose
    sigma = C95 / (1.96 * (44 ** 0.5))
    chosen, seed = [], 100
    wants = [False, False, True]
    while len(chosen) < 3:
        w = walk(44, random.Random(seed), sigma)
        seed += 1
        k_max = max(abs(v) / (C95 * ((i / 44) ** 0.5) + 1e-9) for i, v in enumerate(w) if i)
        escapes = k_max > 1.08
        tame = k_max < 0.85
        if (wants[len(chosen)] and escapes and k_max < 1.4) or (not wants[len(chosen)] and tame):
            chosen.append(w)
    for i, w in enumerate(chosen):
        pts = [(x0 + j * (x1 - x0) / 44, y0 + v) for j, v in enumerate(w)]
        base = "" if i == 0 else ";opacity:0"
        body.append(
            f'<path class="real" style="animation-delay:{3.6 + 3 * i:.1f}s{base}" pathLength="1" stroke-dasharray="1" '
            f'd="{poly(pts)}" stroke="{T["fg"]}" stroke-opacity=".85" stroke-width="1.3" stroke-linejoin="round"/>'
        )

    body.append(
        f'<circle class="ring fb" cx="{x0}" cy="{y0}" r="4" stroke="{T["accent"]}" stroke-width="1.5"/>'
        f'<circle class="pop fb" style="animation-delay:2.9s" cx="{x0}" cy="{y0}" r="4" fill="{T["accent"]}"/>'
    )
    body.append(
        f'<g class="fade" style="animation-delay:3.4s">'
        + text(x0, y0 - 14, "now", 10, "muted", anchor="middle", T=T)
        + text(x1, y0 - C95 - 10, "95% band", 10, "accent", anchor="end", T=T)
        + text(x1, y0 + C95 + 20, "h = 30d", 10, "subtle", anchor="end", T=T)
        + "</g>"
    )

    # legend, top right: says what each mark is
    lg = (
        f'<text x="{x1}" y="34" font-size="10.5" font-weight="400" text-anchor="end" fill="{T["subtle"]}">'
        f'<tspan fill="{T["subtle"]}">— noise   </tspan>'
        f'<tspan fill="{T["accent"]}">— smoothed signal   </tspan>'
        f'<tspan fill="{T["fg"]}">— what actually happened</tspan></text>'
    )
    body.append(f'<g class="fade" style="animation-delay:3.8s">{lg}</g>')
    body.append("</g>")

    # ---- name: split-flap ------------------------------------------------------------
    adv = NAME_SIZE * 0.6
    body.append(text(NAME_X, 54, "github.com/ChiJiun", 12, "subtle", cls="fade", T=T))
    body.append('<g clip-path="url(#flap)">')
    frng = random.Random(3)
    nflap = 7
    for i, ch in enumerate(NAME):
        if ch == " ":
            continue
        x = NAME_X + i * adv
        col = [text(x, NAME_Y, ch, NAME_SIZE, "fg", 700, T=T)]
        for k in range(1, nflap + 1):
            col.append(text(x, NAME_Y - k * 54, frng.choice(FLAP_GLYPHS), NAME_SIZE, "subtle", 700, T=T))
        body.append(f'<g class="flap" style="animation-delay:{0.25 + i * 0.065:.3f}s">{"".join(col)}</g>')
    body.append("</g>")
    cjk_x = NAME_X + len(NAME) * adv + 18
    body.append(
        f'<text class="tc rise" style="animation-delay:1.25s" x="{cjk_x:.1f}" y="{NAME_Y - 2}" '
        f'font-size="24" font-weight="500" fill="{T["muted"]}">翁祺鈞</text>'
    )

    # ---- typed intro -------------------------------------------------------------------
    size, y = 15, 172
    t = 1.0
    for i, (line, col) in enumerate(LINES):
        lw = mono_w(line, size)
        body.append(text(NAME_X, y, line, size, col, T=T))
        dur = len(line) * 0.022
        body.append(
            f'<rect class="type fb" style="animation-delay:{t:.2f}s;animation-duration:{dur:.2f}s;'
            f'animation-timing-function:steps({len(line)},end)" x="{NAME_X - 2}" y="{y - 15}" '
            f'width="{lw + 6:.1f}" height="21" fill="{T["panel"]}"/>'
        )
        t += dur + 0.12
        y += 24
    last_w = mono_w(LINES[-1][0], size)
    body.append(
        f'<rect class="caret" style="animation-delay:{t:.2f}s" x="{NAME_X + last_w + 4:.1f}" '
        f'y="{y - 24 - 13}" width="8" height="16" fill="{T["accent"]}"/>'
    )

    now = (
        f'<text x="{NAME_X}" y="266" font-size="12" font-weight="400" fill="{T["muted"]}">'
        f'<tspan fill="{T["accent"]}" font-weight="500">now </tspan>'
        f"{esc('verifiable DP for federated learning · NSTC undergrad research')}</text>"
    )
    body.append(f'<g class="fade" style="animation-delay:{t + 0.2:.2f}s">{now}</g>')

    css.append(
        f".fade{{animation:fade .9s {EASE} both}}"
        "@keyframes fade{from{opacity:0}}"
        ".drift{animation:drift linear infinite}"
        f"@keyframes drift{{to{{transform:translateX(-{W}px)}}}}"
        f".draw{{animation:draw 1.6s {EASE_IO} both}}"
        "@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
        f".cone{{transform-origin:left center;animation:cone .9s {EASE} both}}"
        "@keyframes cone{from{transform:scale(0,.2);opacity:0}}"
        f".pop{{transform-origin:center;animation:pop .5s {EASE} both}}"
        "@keyframes pop{from{transform:scale(0)}}"
        ".ring{transform-origin:center;animation:ring 2.4s ease-out 3s infinite both}"
        "@keyframes ring{from{transform:scale(1);opacity:.9}to{transform:scale(4.5);opacity:0}}"
        ".real{animation:real 9s linear infinite both}"
        "@keyframes real{0%{stroke-dashoffset:1;opacity:1}22%{stroke-dashoffset:0}30%{opacity:1}"
        "33.3%,100%{stroke-dashoffset:0;opacity:0}}"
        f".flap{{animation:flap .42s steps({nflap},end) both}}"
        f"@keyframes flap{{from{{transform:translateY({nflap * 54}px)}}to{{transform:none}}}}"
        f".rise{{animation:rise .8s {EASE} both}}"
        "@keyframes rise{from{opacity:0;transform:translateY(8px)}}"
        ".type{transform-origin:right center;transform:scaleX(0);animation:type 1s both}"
        "@keyframes type{from{transform:scaleX(1)}to{transform:scaleX(0)}}"
        ".caret{animation:blink 1.1s steps(1,end) infinite both}"
        "@keyframes blink{0%{opacity:0}50%{opacity:1}}"
    )
    return document(
        W, H, "".join(body), "".join(css),
        "Chi-Jiun Wong (翁祺鈞)",
        "CS undergrad at NCU, minor in finance. Builds forecasting experiments, verifiable-ML prototypes, "
        "and small bots that run on free tiers. Animated banner: a noisy series, a smoothed signal and a "
        "deliberately wide 95% forecast band.",
    )


def main():
    for th in THEMES:
        write("hero", th, build(th))


if __name__ == "__main__":
    main()
