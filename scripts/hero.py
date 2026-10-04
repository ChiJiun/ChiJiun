"""Hero banner: motto, split-flap name, typed intro, and the zk-verifiable-dp-fl mechanism.

Right side loops one client update through the pipeline the research project proves:
raw Δw -> clipped to ±C (the cut-off part shows as a dashed ghost) -> DP noise added
-> wrapped in a proof -> verified. Background traces are noise, drifting.
"""
from __future__ import annotations

import random

from svgkit import (EASE, EASE_IO, THEMES, ZH, document, esc, mono_w, poly, set_lang, smooth_path, tc_attr, text,
                    text_w, tr, write)

W, H = 840, 300
NAME = "Chi-Jiun Wong"
NAME_X, NAME_Y, NAME_SIZE = 44, 128, 46
LINES = [
    ("CS undergrad at NCU, minor in finance.", "fg"),
    ("I build verifiable-ML prototypes, and small", "muted"),
    ("bots that run on free tiers.", "muted"),
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


def clamp_h(v: float, B: float) -> float:
    return max(3.0, min(v, B + 10))


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
    for i, (base, amp, dur, op) in enumerate([(160, 3.4, 70, 0.4), (196, 2.6, 95, 0.3), (128, 2.2, 130, 0.22)]):
        b = bridge(n, rng, amp)
        pts = [(k * step, base + b[k % n]) for k in range(2 * n + 1)]
        body.append(
            f'<g class="fade" style="animation-delay:{0.2 + i * 0.15:.2f}s">'
            f'<path class="drift" style="animation-duration:{dur}s" d="{poly(pts)}" '
            f'stroke="{T["subtle"]}" stroke-opacity="{op}" stroke-width="1"/></g>'
        )
    body.append(f'<rect width="{W}" height="{H}" fill="url(#scrim)"/>')

    # ---- mechanism: one client update, clipped, noised, proven ---------------------
    # Same story as zk-verifiable-dp-fl: Δw -> clip to ±C -> + DP noise -> π -> verified.
    P = 8.0
    bx0, pitch, bw, base, B = 546, 18, 10, 166, 40
    vrng = random.Random(21)
    raw = [vrng.choice([-1, 1]) * vrng.uniform(14, 74) for _ in range(14)]
    S, A = T["subtle"], T["accent"]

    def scale(h: float, r: float) -> float:
        return max(0.08, h / abs(r))

    body.append(f'<g class="fade" style="animation-delay:.6s">'
                f'<path d="M538,{base - B} H812 M538,{base + B} H812" stroke="{A}" stroke-opacity=".55" stroke-dasharray="3 3"/>'
                f'<path d="M538,{base}.5 H812" stroke="{T["line"]}"/>'
                + text(812, base - B - 5, "+C", 9.5, "accent", anchor="end", T=T)
                + text(812, base + B + 13, "−C", 9.5, "accent", anchor="end", T=T) + "</g>")
    for i, r in enumerate(raw):
        x = bx0 + i * pitch
        h = abs(r)
        y = base - h if r > 0 else base
        c = scale(min(h, B), r)
        noisy = [clamp_h(min(h, B) + vrng.gauss(0, 7), B) for _ in range(3)]
        a1, a2, f = (scale(v, r) for v in noisy)
        origin = "bottom" if r > 0 else "top"
        css.append(
            f"@keyframes b{i}{{0%{{transform:scaleY(0);fill:{S}}}12%,22%{{transform:scaleY(1)}}"
            f"30%,38%{{transform:scaleY({c:.3f});fill:{S}}}44%{{transform:scaleY({a1:.3f})}}50%{{transform:scaleY({a2:.3f})}}"
            f"56%,92%{{transform:scaleY({f:.3f});fill:{A};opacity:1}}98%,100%{{transform:scaleY({f:.3f});fill:{A};opacity:0}}}}"
        )
        body.append(f'<rect class="bar" style="animation-name:b{i};transform-origin:{origin};transform:scaleY({f:.3f})" '
                    f'x="{x}" y="{y:.1f}" width="{bw}" height="{h:.1f}" rx="2" fill="{A}"/>')
        if h > B:
            body.append(f'<rect class="ghost" x="{x - .5}" y="{y - .5:.1f}" width="{bw + 1}" height="{h + 1:.1f}" rx="2" '
                        f'stroke="{T["muted"]}" stroke-dasharray="2 2"/>')

    box_y, box_h = base - B - 22, 2 * B + 44
    body.append(f'<rect class="proof" pathLength="1" stroke-dasharray="1" x="538" y="{box_y}" width="{14 * pitch + 2}" '
                f'height="{box_h}" rx="8" stroke="{T["ok"]}" stroke-width="1.4"/>')
    badge = tr("π · verified")
    bwid = text_w(badge, 10.5) + 18
    body.append(f'<g class="badge fb"><rect x="{812 - bwid:.1f}" y="{box_y + box_h - 11}" width="{bwid:.1f}" height="22" rx="11" '
                f'fill="{T["panel"]}" stroke="{T["ok"]}"/>'
                + text(812 - bwid / 2, box_y + box_h + 4, badge, 10.5, "ok", 500, anchor="middle", T=T) + "</g>")

    # pipeline header: each step lights while it happens
    steps = [("Δw", 2, 24), ("clip", 22, 40), ("+ noise", 38, 58), ("π", 58, 92), ("verified", 64, 92)]
    x = 544
    for k, (label, on, off) in enumerate(steps):
        lab = tr(label)
        body.append(text(x, 62, lab, 11, "subtle", T=T))
        css.append(f"@keyframes s{k}{{0%,{on - 1}%{{opacity:0}}{on}%,{off}%{{opacity:1}}{off + 3}%,100%{{opacity:0}}}}")
        col = "ok" if label in ("π", "verified") else "accent"
        body.append(f'<g class="step" style="animation-name:s{k}">{text(x, 62, lab, 11, col, 500, T=T)}</g>')
        x += text_w(lab, 11)
        if k < len(steps) - 1:
            body.append(text(x + 5, 62, "→", 11, "subtle", T=T))
            x += 26
    css.append(
        f".bar{{transform-box:fill-box;animation:{P}s {EASE} .8s infinite both}}"
        f".ghost{{opacity:0;animation:ghost {P}s linear .8s infinite both}}"
        "@keyframes ghost{0%,10%{opacity:0}14%,32%{opacity:.9}40%,100%{opacity:0}}"
        f".proof{{animation:proof {P}s {EASE_IO} .8s infinite both}}"
        "@keyframes proof{0%,58%{stroke-dashoffset:1;opacity:1}68%,92%{stroke-dashoffset:0;opacity:1}98%,100%{stroke-dashoffset:0;opacity:0}}"
        f".badge{{transform-origin:center;animation:badge {P}s {EASE} .8s infinite both}}"
        "@keyframes badge{0%,64%{transform:scale(0);opacity:0}69%,92%{transform:none;opacity:1}98%,100%{opacity:0}}"
        f".step{{opacity:0;animation:{P}s linear .8s infinite both}}"
    )
    body.append("</g>")

    # ---- motto ---------------------------------------------------------------------------
    adv = NAME_SIZE * 0.6
    body.append(f'<g class="fade" style="animation-delay:.1s"><rect x="{NAME_X}" y="30" width="3" height="38" rx="1.5" fill="{T["accent"]}"/>'
                + text(NAME_X + 14, 45, "The world is one giant makeshift troupe,", 13, "muted", T=T)
                + text(NAME_X + 14, 64, "so fake it till you make it.", 13, "accent", 500, T=T) + "</g>")
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
        line = tr(line)
        lw = text_w(line, size)
        body.append(text(NAME_X, y, line, size, col, T=T))
        dur = len(line) * 0.022
        body.append(
            f'<rect class="type fb" style="animation-delay:{t:.2f}s;animation-duration:{dur:.2f}s;'
            f'animation-timing-function:steps({len(line)},end)" x="{NAME_X - 2}" y="{y - 15}" '
            f'width="{lw + 6:.1f}" height="21" fill="{T["panel"]}"/>'
        )
        t += dur + 0.12
        y += 24
    last_w = text_w(tr(LINES[-1][0]), size)
    body.append(
        f'<rect class="caret" style="animation-delay:{t:.2f}s" x="{NAME_X + last_w + 4:.1f}" '
        f'y="{y - 24 - 13}" width="8" height="16" fill="{T["accent"]}"/>'
    )

    now = (
        f'<text{tc_attr()} x="{NAME_X}" y="266" font-size="12" font-weight="400" fill="{T["muted"]}">'
        f'<tspan fill="{T["accent"]}">{esc(tr("now "))}</tspan>'
        f"{esc(tr('verifiable DP for federated learning · NSTC undergrad research'))}</text>"
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
        tr("Chi-Jiun Wong (翁祺鈞)"),
        "CS undergrad at NCU, minor in finance. Builds verifiable-ML prototypes "
        "and small bots that run on free tiers. Motto: the world is one giant makeshift troupe, so fake it "
        "till you make it. Animated banner: a client update is clipped, noised and proven, as in zk-verifiable-dp-fl.",
    )


ZH.update({
    "CS undergrad at NCU, minor in finance.": "中央大學資工系，輔系財金。",
    "I build verifiable-ML prototypes, and small": "做可驗證機器學習的原型，",
    "bots that run on free tiers.": "也做幾個跑在免費額度上的小工具。",
    "The world is one giant makeshift troupe,": "這個世界就是一個巨大的草台班子，",
    "so fake it till you make it.": "所以 fake it till you make it。",
    "π · verified": "π · 驗證通過", "+ noise": "+ 噪聲", "verified": "驗證通過",
    "— noise   ": "— 雜訊   ", "— smoothed signal   ": "— 平滑訊號   ", "— what actually happened": "— 實際走勢",
    "now": "現在", "now ": "現在 ", "95% band": "95% 區間",
    "verifiable DP for federated learning · NSTC undergrad research": "可驗證差分隱私聯邦學習 · 國科會大專生計畫",
    "Chi-Jiun Wong (翁祺鈞)": "翁祺鈞 Chi-Jiun Wong",
})


def main():
    for lang in ("en", "zh"):
        set_lang(lang)
        for th in THEMES:
            write("hero", th, build(th))
    set_lang("en")


if __name__ == "__main__":
    main()
