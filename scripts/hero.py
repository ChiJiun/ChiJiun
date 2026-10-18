"""Hero banner: motto, split-flap name, typed intro, and the zk-verifiable-dp-fl mechanism.

Right side loops one client update through the pipeline the research project proves:
raw Δw -> clipped to ±C (the cut-off part shows as a dashed ghost) -> DP noise added
(noise particles swarm the bars) -> wrapped in a proof -> verified (ring pulse).
Background: two phosphor traces with afterglow, drifting.

v2 motion: panel chrome (grid, glow, drawn border, corner ticks, sheen pass), motto
highlight sweep, name glow + underline, live dot, clip flash, noise swarm, proof glow,
verify pulse, cycle progress bar.
"""
from __future__ import annotations

import random

from svgkit import (EASE, EASE_IO, THEMES, ZH, chrome, document, esc, mono_w, poly, set_lang, tc_attr, text,
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


def clamp_h(v: float, B: float) -> float:
    return max(3.0, min(v, B + 10))


def build(theme: str) -> str:
    T = THEMES[theme]
    css, body = [], []
    S, A, OK = T["subtle"], T["accent"], T["ok"]

    defs, bg, kcss = chrome(T, W, H, 14, glow_at=(0.8, 0.5))
    css.append(kcss)
    body.append(defs)
    body.append(
        f'<defs><linearGradient id="scrim" gradientUnits="userSpaceOnUse" x1="0" x2="{W}" y1="0" y2="0">'
        f'<stop offset="0" stop-color="{T["panel"]}"/><stop offset=".56" stop-color="{T["panel"]}" stop-opacity=".96"/>'
        f'<stop offset=".7" stop-color="{T["panel"]}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="uline" x1="0" x2="1"><stop offset="0" stop-color="{A}"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="hl" x1="0" x2="1"><stop offset="0" stop-color="{A}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{A}" stop-opacity=".16"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></linearGradient>'
        f'<clipPath id="flap"><rect x="{NAME_X-4}" y="{NAME_Y-40}" width="{mono_w(NAME, NAME_SIZE)+8}" height="54"/></clipPath>'
        f'<clipPath id="motto"><rect x="{NAME_X}" y="28" width="360" height="44"/></clipPath>'
        f"</defs>"
    )
    body.append(bg)
    body.append('<g clip-path="url(#k-frame)">')

    # ---- phosphor traces with afterglow (drift) ----------------------------------------
    rng = random.Random(7)
    step, n = 6, W // 6
    for i, (base, amp, dur, op, col) in enumerate([(170, 3.6, 70, 0.55, OK), (204, 2.8, 95, 0.35, A), (132, 2.2, 130, 0.25, S)]):
        b = bridge(n, rng, amp)
        pts = [(k * step, base + b[k % n]) for k in range(2 * n + 1)]
        d = poly(pts)
        glow = (f'<path class="drift" style="animation-duration:{dur}s" d="{d}" stroke="{col}" stroke-opacity="{op * .7:.2f}" '
                f'stroke-width="3" filter="url(#k-blur)"/>') if i < 2 else ""
        body.append(
            f'<g class="k-fade" style="animation-delay:{0.3 + i * 0.15:.2f}s">{glow}'
            f'<path class="drift" style="animation-duration:{dur}s" d="{d}" stroke="{col}" stroke-opacity="{op}" stroke-width="1"/></g>'
        )
    body.append(f'<rect width="{W}" height="{H}" fill="url(#scrim)"/>')

    # ---- mechanism: one client update, clipped, noised, proven ---------------------
    P = 8.0
    bx0, pitch, bw, base, B = 546, 18, 10, 166, 40
    vrng = random.Random(21)
    raw = [vrng.choice([-1, 1]) * vrng.uniform(14, 74) for _ in range(14)]

    def scale(h: float, r: float) -> float:
        return max(0.08, h / abs(r))

    # ±C bounds flash while clipping happens
    body.append(f'<g class="k-fade" style="animation-delay:.6s">'
                f'<path class="bound" d="M538,{base - B} H812 M538,{base + B} H812" stroke="{A}" stroke-opacity=".5" stroke-dasharray="3 3"/>'
                f'<path d="M538,{base}.5 H812" stroke="{T["line"]}"/>'
                + text(812, base - B - 5, "+C", 9.5, "accent", anchor="end", T=T)
                + text(812, base + B + 13, "−C", 9.5, "accent", anchor="end", T=T) + "</g>")
    css.append(f".bound{{animation:bound {P}s linear .8s infinite both}}"
               "@keyframes bound{0%,20%{stroke-opacity:.5}24%,34%{stroke-opacity:1;stroke-width:1.6}40%,100%{stroke-opacity:.5}}")

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

    # DP noise swarm: particles that appear only during the "+ noise" phase
    nrng = random.Random(5)
    for k in range(26):
        px = nrng.uniform(540, 812)
        py = nrng.uniform(base - B - 16, base + B + 16)
        dx, dy = nrng.uniform(-9, 9), nrng.uniform(-9, 9)
        r = nrng.uniform(.9, 2.0)
        css.append(f"@keyframes nz{k}{{0%,36%{{opacity:0;transform:none}}42%{{opacity:.95}}"
                   f"50%{{transform:translate({dx:.1f}px,{dy:.1f}px)}}56%{{opacity:.5}}62%,100%{{opacity:0;transform:translate({dx * 1.6:.1f}px,{dy * 1.6:.1f}px)}}}}")
        body.append(f'<circle class="nz" style="animation-name:nz{k}" cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" fill="{A}"/>')
    css.append(f".nz{{opacity:0;animation:{P}s {EASE} .8s infinite both}}")

    box_y, box_h = base - B - 22, 2 * B + 44
    box = f'x="538" y="{box_y}" width="{14 * pitch + 2}" height="{box_h}" rx="8"'
    body.append(f'<rect class="pglow" {box} stroke="{OK}" stroke-width="5" filter="url(#k-blur2)"/>')
    body.append(f'<rect class="proof" pathLength="1" stroke-dasharray="1" {box} stroke="{OK}" stroke-width="1.4"/>')
    body.append(f'<rect class="vring" {box} stroke="{OK}" stroke-width="1.2"/>')
    badge = tr("π · verified")
    bwid = text_w(badge, 10.5) + 18
    body.append(f'<g class="badge fb"><rect x="{812 - bwid:.1f}" y="{box_y + box_h - 11}" width="{bwid:.1f}" height="22" rx="11" '
                f'fill="{T["panel"]}" stroke="{OK}"/>'
                + text(812 - bwid / 2, box_y + box_h + 4, badge, 10.5, "ok", 500, anchor="middle", T=T) + "</g>")

    # pipeline header: each step lights while it happens, progress bar tracks the cycle
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
    body.append(f'<rect x="544" y="70" width="268" height="2" rx="1" fill="{T["grid"]}"/>'
                f'<rect class="prog" x="544" y="70" width="268" height="2" rx="1" fill="{A}" fill-opacity=".8"/>')
    css.append(
        f".bar{{transform-box:fill-box;animation:{P}s {EASE} .8s infinite both}}"
        f".ghost{{opacity:0;animation:ghost {P}s linear .8s infinite both}}"
        "@keyframes ghost{0%,10%{opacity:0}14%,32%{opacity:.9}40%,100%{opacity:0}}"
        f".proof{{animation:proof {P}s {EASE_IO} .8s infinite both}}"
        "@keyframes proof{0%,58%{stroke-dashoffset:1;opacity:1}68%,92%{stroke-dashoffset:0;opacity:1}98%,100%{stroke-dashoffset:0;opacity:0}}"
        f".pglow{{opacity:0;animation:pglow {P}s {EASE} .8s infinite both}}"
        "@keyframes pglow{0%,64%{opacity:0}70%{opacity:.7}92%{opacity:.25}98%,100%{opacity:0}}"
        f".vring{{transform-box:fill-box;transform-origin:center;opacity:0;animation:vring {P}s {EASE} .8s infinite both}}"
        "@keyframes vring{0%,66%{opacity:0;transform:scale(.9)}69%{opacity:.9}88%,100%{opacity:0;transform:scale(1.22)}}"
        f".badge{{transform-origin:center;animation:badge {P}s {EASE} .8s infinite both}}"
        "@keyframes badge{0%,64%{transform:scale(0);opacity:0}69%,92%{transform:none;opacity:1}98%,100%{opacity:0}}"
        f".step{{opacity:0;animation:{P}s linear .8s infinite both}}"
        f".prog{{transform-box:fill-box;transform-origin:left;animation:prog {P}s linear .8s infinite both}}"
        "@keyframes prog{0%{transform:scaleX(0);opacity:1}92%{transform:scaleX(1);opacity:1}100%{transform:scaleX(1);opacity:0}}"
    )
    body.append("</g>")

    # ---- motto with a highlight sweep ------------------------------------------------------
    body.append(f'<rect class="bar0" x="{NAME_X}" y="30" width="3" height="38" rx="1.5" fill="{A}"/>')
    body.append(f'<g class="k-fade" style="animation-delay:.25s">'
                + text(NAME_X + 14, 45, "The world is one giant makeshift troupe,", 13, "muted", T=T)
                + text(NAME_X + 14, 64, "so fake it till you make it.", 13, "accent", 500, T=T) + "</g>")
    body.append(f'<g clip-path="url(#motto)"><rect class="hl" x="{NAME_X - 120}" y="28" width="120" height="44" fill="url(#hl)"/></g>')
    css.append(
        f".bar0{{transform-box:fill-box;transform-origin:top;animation:grow0 .7s {EASE} .15s both}}@keyframes grow0{{from{{transform:scaleY(0)}}}}"
        f".hl{{animation:hl 1.3s {EASE_IO} .45s both}}@keyframes hl{{to{{transform:translateX(480px)}}}}"
    )

    # ---- split-flap name, then glow + underline ---------------------------------------------
    adv = NAME_SIZE * 0.6
    name_w = mono_w(NAME, NAME_SIZE)
    body.append(f'<text class="nglow" x="{NAME_X}" y="{NAME_Y}" font-size="{NAME_SIZE}" font-weight="700" fill="{A}" '
                f'filter="url(#k-blur2)">{esc(NAME)}</text>')
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
    body.append(f'<rect class="uline" x="{NAME_X}" y="{NAME_Y + 9}" width="{name_w:.0f}" height="2" rx="1" fill="url(#uline)"/>')
    cjk_x = NAME_X + len(NAME) * adv + 18
    body.append(
        f'<text class="tc rise" style="animation-delay:1.25s" x="{cjk_x:.1f}" y="{NAME_Y - 2}" '
        f'font-size="24" font-weight="500" fill="{T["muted"]}">翁祺鈞</text>'
    )
    css.append(
        ".nglow{opacity:0;animation:nglow 2.4s ease-out 1.05s both}"
        "@keyframes nglow{0%{opacity:0}30%{opacity:.55}100%{opacity:.16}}"
        f".uline{{transform-box:fill-box;transform-origin:left;animation:growx0 .9s {EASE} 1.15s both}}@keyframes growx0{{from{{transform:scaleX(0)}}}}"
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
        f'y="{y - 24 - 13}" width="8" height="16" fill="{A}"/>'
    )

    now = (
        f'<text{tc_attr()} x="{NAME_X + 14}" y="266" font-size="12" font-weight="400" fill="{T["muted"]}">'
        f'<tspan fill="{A}">{esc(tr("now "))}</tspan>'
        f"{esc(tr('verifiable DP for federated learning · NSTC undergrad research'))}</text>"
    )
    body.append(f'<g class="k-fade" style="animation-delay:{t + 0.2:.2f}s">'
                f'<circle class="live" cx="{NAME_X + 4}" cy="262" r="3" fill="{OK}"/>'
                f'<circle class="livering" cx="{NAME_X + 4}" cy="262" r="3" stroke="{OK}"/>{now}</g>')

    css.append(
        ".drift{animation:drift linear infinite}"
        f"@keyframes drift{{to{{transform:translateX(-{W}px)}}}}"
        f".flap{{animation:flap .42s steps({nflap},end) both}}"
        f"@keyframes flap{{from{{transform:translateY({nflap * 54}px)}}to{{transform:none}}}}"
        f".rise{{animation:rise .8s {EASE} both}}"
        "@keyframes rise{from{opacity:0;transform:translateY(8px)}}"
        ".type{transform-origin:right center;transform:scaleX(0);animation:type 1s both}"
        "@keyframes type{from{transform:scaleX(1)}to{transform:scaleX(0)}}"
        ".caret{animation:blink 1.1s steps(1,end) infinite both}"
        "@keyframes blink{0%{opacity:0}50%{opacity:1}}"
        ".live{animation:live 2s ease-in-out infinite both}@keyframes live{50%{opacity:.45}}"
        ".livering{transform-box:fill-box;transform-origin:center;animation:livering 2s ease-out infinite both}"
        "@keyframes livering{from{transform:scale(1);opacity:.8}to{transform:scale(3.4);opacity:0}}"
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
    "so fake it till you make it.": "所以弄假直到成真。",
    "π · verified": "π · 驗證通過", "+ noise": "+ 噪聲", "verified": "驗證通過",
    "now": "現在", "now ": "現在 ",
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
