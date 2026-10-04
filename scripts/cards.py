"""Project cards. One mechanism animation per project, plus up to three plain rows.

Every number on a card is copied from that repo's README / results files; where a
picture is schematic (cell positions, packet timing) the *counts* are still real.
Row labels are fixed vocabulary so the cards read as one system:
  measured / finding / used by   -> green: things that were actually observed
  decision / cadence / scope ... -> blue: what was chosen and where it applies
  caveat                         -> red: the limit, stated next to the claim
"""
from __future__ import annotations

import random

from svgkit import (EASE, EASE_IO, THEMES, ZH, document, esc, mono_w, poly, set_lang, smooth_path, tc_attr, text,
                    text_w, tr, write)

W, H = 420, 290
VX, VY = 22, 66  # viz origin
ROW_COLORS = {
    "measured": "ok", "finding": "ok", "used by": "ok",
    "decision": "blue", "my part": "accent", "cadence": "blue", "budget": "blue", "scope": "blue",
    "does": "blue", "keeps": "blue", "design": "blue",
    "caveat": "bad",
}

COMMON_CSS = (
    f".in{{animation:in .8s {EASE} both}}"
    "@keyframes in{from{opacity:0;transform:translateY(6px)}}"
    f".fade{{animation:fade .8s {EASE} both}}"
    "@keyframes fade{from{opacity:0}}"
    f".draw{{animation:draw 1.4s {EASE_IO} both}}"
    "@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
    f".grow{{transform-box:fill-box;transform-origin:bottom;animation:grow .9s {EASE} both}}"
    "@keyframes grow{from{transform:scaleY(0)}}"
    f".growx{{transform-box:fill-box;transform-origin:left;animation:growx .9s {EASE} both}}"
    "@keyframes growx{from{transform:scaleX(0)}}"
    f".pop{{transform-box:fill-box;transform-origin:center;animation:pop .6s {EASE} both}}"
    "@keyframes pop{0%{transform:scale(0)}60%{transform:scale(1.25)}100%{transform:none}}"
    ".ring{transform-box:fill-box;transform-origin:center;animation:ring 2s ease-out infinite both}"
    "@keyframes ring{from{transform:scale(1);opacity:.9}to{transform:scale(3.2);opacity:0}}"
    ".big{animation-name:ringbig}@keyframes ringbig{from{transform:scale(1);opacity:.8}to{transform:scale(1.7);opacity:0}}"
    ".march{animation:march 1.2s linear infinite}"
    "@keyframes march{to{stroke-dashoffset:-8}}"
)


def d(t: float) -> str:
    return f"animation-delay:{t:.2f}s"


def frame(T, idx, title, tags, chip, rows, viz, css, alt, desc):
    b = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="{T["panel"]}" stroke="{T["line"]}"/>']
    b.append(f'<g class="in">{text(22, 34, idx, 12, "accent", 500, T=T)}{text(50, 34, title, 15, "fg", 700, T=T)}</g>')
    b.append(f'<g class="in" style="{d(.08)}">{text(22, 54, tags, 11, "muted", T=T)}</g>')
    cw = text_w(tr(chip), 10.5) + 16
    b.append(
        f'<g class="in" style="{d(.12)}"><rect x="{W-22-cw:.1f}" y="20" width="{cw:.1f}" height="20" rx="10" '
        f'stroke="{T["line"]}"/>{text(W-22-cw/2, 34, chip, 10.5, "muted", anchor="middle", T=T)}</g>'
    )
    b.append(f'<g transform="translate({VX},{VY})">{viz}</g>')
    b.append(f'<line class="fade" style="{d(.3)}" x1="22" x2="{W-22}" y1="216.5" y2="216.5" stroke="{T["grid"]}"/>')
    for i, (label, value) in enumerate(rows):
        y = 238 + i * 20
        b.append(
            f'<g class="in" style="{d(.35 + i * .08)}">'
            + text(22, y, label, 10.5, ROW_COLORS[label], 500, T=T)
            + text(100, y, value, 11, "fg", T=T)
            + "</g>"
        )
        assert text_w(tr(value), 11) <= W - 22 - 100 + 4, f"row too long: {tr(value)}"
    return document(W, H, "".join(b), COMMON_CSS + css, tr(alt), tr(desc))


# ------------------------------------------------------------------------------------------
def zk(T):
    v, css = [], []
    lanes = [34, 72, 110]
    agg = (330, 72)
    v.append(f'<g class="fade">{text(0, 8, "clients", 10, "muted", T=T)}'
             f'{text(197, 8, "verify π", 10, "accent", anchor="middle", T=T)}'
             f'{text(agg[0], 8, "aggregate", 10, "muted", anchor="middle", T=T)}</g>')
    for i, y in enumerate(lanes):
        v.append(
            f'<g class="pop" style="{d(.2 + i*.08)}"><circle cx="12" cy="{y}" r="11" stroke="{T["muted"]}"/>'
            + text(12, y + 3.5, f"c{i+1}", 9.5, "muted", anchor="middle", T=T) + "</g>"
        )
        v.append(f'<path class="fade" style="{d(.4)}" d="M26,{y} H188" stroke="{T["grid"]}" stroke-dasharray="2 3"/>')
        v.append(f'<path class="fade" style="{d(.5)}" d="M206,{y} C260,{y} 270,{agg[1]} {agg[0]-26},{agg[1]}" stroke="{T["grid"]}"/>')
    v.append(f'<rect class="grow" style="{d(.3)}" x="190" y="18" width="14" height="108" rx="4" '
             f'fill="{T["accent"]}" fill-opacity=".08" stroke="{T["accent"]}"/>')
    v.append(f'<rect class="scan" x="191" y="18" width="12" height="14" rx="3" fill="{T["accent"]}" fill-opacity=".55"/>')
    v.append(f'<circle class="ring big" style="{d(1)}" cx="{agg[0]}" cy="{agg[1]}" r="24" stroke="{T["ok"]}" stroke-opacity=".6"/>')
    v.append(f'<g class="pop" style="{d(.45)}"><circle cx="{agg[0]}" cy="{agg[1]}" r="24" fill="{T["panel"]}" stroke="{T["ok"]}"/>'
             + text(agg[0], agg[1] + 3.5, "FedAvg", 9.5, "ok", 500, anchor="middle", T=T) + "</g>")

    period = 4.2
    for i, y in enumerate(lanes):
        m = y + (agg[1] - y) * 0.6
        css.append(
            f"@keyframes zk{i}{{0%{{transform:translate(26px,{y}px);opacity:0}}6%{{opacity:1}}"
            f"46%{{transform:translate(184px,{y}px)}}54%{{transform:translate(212px,{y}px)}}"
            f"70%{{transform:translate(268px,{m:.1f}px)}}86%{{transform:translate(306px,{agg[1]}px);opacity:1}}"
            f"94%,100%{{transform:translate(318px,{agg[1]}px);opacity:0}}}}"
        )
    css.append(
        f".pk{{opacity:0;animation:{period}s linear infinite both}}"
        "@keyframes honest{0%,49%{fill:" + T["muted"] + "}55%,100%{fill:" + T["ok"] + "}}"
        "@keyframes badge{0%,49%{stroke-opacity:0}55%,100%{stroke-opacity:1}}"
        f".scan{{animation:scan {period/2}s {EASE_IO} infinite alternate both}}"
        "@keyframes scan{to{transform:translateY(94px)}}"
    )
    packets = [(0, 0.0, False), (1, 0.7, False), (2, 1.4, False), (0, 2.1, False), (1, 2.8, False), (2, 3.5, True)]
    for lane, delay, attack in packets:
        if attack:
            inner = (f'<rect x="-5" y="-5" width="10" height="10" rx="2" fill="{T["bad"]}"/>'
                     f'<rect style="animation:badge {period}s linear {1 + delay:.2f}s infinite both" x="-7.5" y="-7.5" '
                     f'width="15" height="15" rx="3.5" stroke="{T["ok"]}" stroke-width="1.5"/>')
        else:
            inner = (f'<rect style="animation:honest {period}s linear {1 + delay:.2f}s infinite both" x="-5" y="-5" '
                     f'width="10" height="10" rx="2" fill="{T["muted"]}"/>')
        v.append(f'<g class="pk" style="animation-name:zk{lane};animation-delay:{1 + delay:.2f}s">{inner}</g>')

    legend = (f'<text{tc_attr()} x="0" y="134" font-size="9.5" font-weight="400" fill="{T["muted"]}">'
              f'<tspan fill="{T["ok"]}">■</tspan>{esc(tr(" honest update   "))}<tspan fill="{T["bad"]}">■</tspan>{esc(tr(" in-bound attack"))}'
              f'<tspan fill="{T["subtle"]}">{esc(tr(" — both verify"))}</tspan></text>')
    v.append(f'<g class="fade" style="{d(.8)}">{legend}</g>')

    return frame(
        T, "01", "zk-verifiable-dp-fl", "python · rust · halo2 · ezkl", "capstone · NSTC grant",
        [("measured", "150/150 per-update Halo2 proofs verify"),
         ("scope", "synthetic data, 4-param model, 10 rounds"),
         ("caveat", "300/300 in-bound attacks verify too")],
        "".join(v), "".join(css),
        "zk-verifiable-dp-fl: verifiable differential privacy for federated learning",
        "Each client update carries a Halo2 proof that it was clipped and noised; only verified updates are "
        "aggregated. Measured: 150/150 per-update proofs verify (synthetic data, 4-parameter model, 10 rounds). "
        "Caveat: 300/300 attacker updates that stay inside the clipping bound also verify, so a proof is not "
        "evidence of honest training.",
    )


# ------------------------------------------------------------------------------------------
def fx(T):
    v, css = [], []
    rw = 5.0419
    models = [("ridge+ft", 5.0089), ("mlp", 5.0341), ("patchtst", 5.1063), ("rf", 5.1156),
              ("chronos", 5.5893), ("hf-tfm", 6.1905)]
    lo, hi, xa, xb = 0.95, 1.25, 62, 150
    X = lambda r: xa + (r - lo) / (hi - lo) * (xb - xa)
    v.append(f'<g class="fade">{text(0, 8, "level error ÷ random walk", 9.5, "muted", T=T)}</g>')
    x1 = X(1.0)
    v.append(f'<path class="draw" pathLength="1" stroke-dasharray="1" d="M{x1:.1f},16 V104" stroke="{T["fg"]}" '
             f'stroke-opacity=".6"/>')
    v.append(f'<g class="fade" style="{d(.4)}">{text(x1, 116, "RW = 1.00", 9, "fg", anchor="middle", T=T)}</g>')
    for k, (name, m) in enumerate(models):
        y = 26 + k * 15
        r = m / rw
        col = "accent" if k == 0 else "muted"
        v.append(f'<g class="fade" style="{d(.1 + k*.06)}">{text(0, y + 3, name, 9.5, "muted", T=T)}'
                 f'<path d="M{xa},{y} H{xb}" stroke="{T["grid"]}"/>{text(178, y + 3, f"{r:.3f}", 9, col, anchor="end", T=T)}</g>')
        v.append(f'<circle class="settle" style="{d(.5 + k*.09)}" cx="{X(r):.1f}" cy="{y}" r="3.6" fill="{T[col]}"/>')
    v.append(f'<g class="fade" style="{d(1.4)}">{text(0, 134, "best p = 0.21 → not significant", 9, "subtle", T=T)}</g>')
    css.append(f".settle{{animation:settle 1.1s {EASE} both}}@keyframes settle{{from{{transform:translateX(90px);opacity:0}}}}")

    # right: Pesaran-Timmermann -log10 p, with vs without valuation features
    ox = 200
    v.append(f'<g class="fade" style="{d(.2)}">{text(ox, 8, "direction: −log10 p (h=5)", 9.5, "muted", T=T)}</g>')
    base, unit = 106, 21
    thr = base - 1.301 * unit
    pairs = [("ridge", 4.0, 0.28, True), ("rf", 3.52, 0.19, False), ("mlp", 3.22, 0.19, False)]
    for k, (name, w, wo, capped) in enumerate(pairs):
        cx = ox + 56 + k * 50
        hw, hwo = w * unit, wo * unit
        v.append(f'<rect class="grow" style="{d(.6 + k*.12)}" x="{cx-19}" y="{base-hwo:.1f}" width="16" height="{hwo:.1f}" '
                 f'rx="2" fill="{T["subtle"]}"/>')
        v.append(f'<rect class="grow" style="{d(.7 + k*.12)}" x="{cx+3}" y="{base-hw:.1f}" width="16" height="{hw:.1f}" '
                 f'rx="2" fill="{T["accent"]}"/>')
        v.append(f'<g class="fade" style="{d(.5)}">{text(cx, 118, name, 9.5, "muted", anchor="middle", T=T)}</g>')
        if capped:
            v.append(f'<g class="fade" style="{d(1.4)}">{text(cx + 11, base - hw - 4, "≥4", 8.5, "accent", anchor="middle", T=T)}</g>')
    v.append(f'<path class="fade march" style="{d(1.2)}" d="M{ox},{thr:.1f} H376" stroke="{T["fg"]}" stroke-opacity=".7" stroke-dasharray="4 4"/>')
    v.append(f'<g class="fade" style="{d(1.3)}">{text(ox, thr - 4, "p=.05", 8.5, "fg", T=T)}</g>')
    v.append(f'<path d="M{ox},{base}.5 H376" stroke="{T["line"]}"/>')
    legend = (f'<text{tc_attr()} x="{ox}" y="134" font-size="9" font-weight="400" fill="{T["muted"]}">'
              f'<tspan fill="{T["accent"]}">■</tspan> +UIRP/CIRP  <tspan fill="{T["subtle"]}">■</tspan>{esc(tr(" without"))}</text>')
    v.append(f'<g class="fade" style="{d(1)}">{legend}</g>')

    return frame(
        T, "02", "forcasting-fx-transformer", "python · pytorch · rolling-origin backtest", "re-test · fork",
        [("measured", "best level model 0.993× RW, p = 0.21"),
         ("finding", "UIRP/CIRP features carry direction info"),
         ("scope", "2 test years × 52 origins × 11 series")],
        "".join(v), "".join(css),
        "forcasting-fx-transformer: a re-test of an existing FX forecasting study",
        "Leakage-free rolling-origin re-evaluation. On levels no model significantly beats a random walk "
        "(best MASE ratio 0.993, Diebold-Mariano p = 0.21). On direction, models with UIRP/CIRP valuation "
        "features pass the Pesaran-Timmermann test (p < 0.001) while the same models without them do not.",
    )


# ------------------------------------------------------------------------------------------
def lending(T):
    v, css = [], []
    pts = [(0.014, 5.11, 100.0), (0.018, 5.83, 88.8), (0.022, 5.65, 70.4), (0.026, 3.15, 33.2), (0.0309, 0.48, 4.4)]
    X = lambda r: 34 + (r - 0.012) / (0.033 - 0.012) * 332
    Y = lambda a: 104 - a * 12.5
    v.append(f'<g class="fade">{text(0, 8, "expected realized APR by offer rate · backtest", 9.5, "muted", T=T)}</g>')
    for a in (2, 4, 6):
        v.append(f'<g class="fade" style="{d(.1)}"><path d="M34,{Y(a)} H376" stroke="{T["grid"]}"/>'
                 f'{text(0, Y(a) + 3, f"{a}%", 8.5, "subtle", T=T)}</g>')
    v.append(f'<path d="M34,104.5 H376" stroke="{T["line"]}"/>')
    for k, (r, apr, fill) in enumerate(pts):
        x = X(r)
        h = fill * 0.8
        v.append(f'<rect class="grow" style="{d(.2 + k*.07)}" x="{x-10:.1f}" y="{104-h:.1f}" width="20" height="{h:.1f}" '
                 f'rx="2" fill="{T["subtle"]}" fill-opacity=".22"/>')
        lab = "FRR" if k == 4 else f"{r:.3f}"
        v.append(f'<g class="fade" style="{d(.3)}">{text(x, 118, lab, 9, "bad" if k == 4 else "muted", anchor="middle", T=T)}'
                 f'{text(x, 132, f"{fill:.0f}%", 9, "subtle", anchor="middle", T=T)}</g>')
    v.append(f'<g class="fade" style="{d(.3)}">{text(0, 118, "rate", 9, "subtle", T=T)}{text(0, 132, "fill", 9, "subtle", T=T)}</g>')
    curve = smooth_path([(X(r), Y(a)) for r, a, _ in pts])
    v.append(f'<path class="draw" style="{d(.6)}" pathLength="1" stroke-dasharray="1" d="{curve}" stroke="{T["accent"]}" stroke-width="2"/>')
    v.append(f'<path class="comet" pathLength="1" stroke-dasharray=".08 1" d="{curve}" stroke="{T["fg"]}" '
             f'stroke-width="2.6" stroke-linecap="round"/>')
    for k, (r, apr, _) in enumerate(pts):
        col = "bad" if k == 4 else "accent"
        v.append(f'<circle class="pop" style="{d(.9 + k*.12)}" cx="{X(r):.1f}" cy="{Y(apr):.1f}" r="3.6" fill="{T["panel"]}" '
                 f'stroke="{T[col]}" stroke-width="2"/>')
    bx, by = X(0.018), Y(5.83)
    v.append(f'<circle class="ring" style="{d(1.8)}" cx="{bx:.1f}" cy="{by:.1f}" r="4" stroke="{T["accent"]}"/>')
    v.append(f'<g class="fade" style="{d(1.6)}">{text(bx, by - 10, "5.83% · ladder floor", 9.5, "accent", 500, anchor="middle", T=T)}'
             f'{text(X(0.0309) - 12, Y(0.48) + 3, "0.48%", 9.5, "bad", 500, anchor="end", T=T)}</g>')
    css.append(".comet{stroke-dashoffset:.08;animation:comet 3.2s linear 2.2s infinite both}"
               "@keyframes comet{from{stroke-dashoffset:.08;opacity:1}90%{opacity:1}to{stroke-dashoffset:-1;opacity:0}}")

    return frame(
        T, "03", "bitfinex-lending-bot", "python · github actions · bitfinex api", "solo · live",
        [("measured", "fills ≥ FRR in 0 of 250 hours"),
         ("decision", "floor 0.018%/day, the backtest optimum"),
         ("caveat", "5.83% APR is a backtest, not a promise")],
        "".join(v), "".join(css),
        "bitfinex-lending-bot: funding offers laddered on real fills, not FRR",
        "Backtest of expected realized APR against offer rate: 5.11% at 0.014%/day, 5.83% at 0.018%, 5.65% at "
        "0.022%, 3.15% at 0.026%, and 0.48% at the FRR (0.0309%), because FRR offers almost never fill. Over "
        "250 hours the close never reached FRR once. Runs every 15 minutes on GitHub Actions.",
    )


# ------------------------------------------------------------------------------------------
def mvdis(T):
    v, css = [], []
    gx, gy, px, py = 34, 18, 9.5, 10.5
    rows_y = [gy + r * py + (6 if r >= 3 else 0) for r in range(10)]
    rng = random.Random(36)
    cold = [(r, c) for r in range(3, 10) for c in range(36)]
    idle = set(rng.sample(cold, 153))
    v.append(f'<g class="fade">{text(0, 8, "36 stations × 10 license classes = 360 combos", 9.5, "muted", T=T)}</g>')
    v.append(f'<g class="fade" style="{d(.2)}">{text(0, rows_y[1] + 7, "hot", 9.5, "accent", T=T)}'
             f'{text(0, rows_y[6] + 7, "cold", 9.5, "blue", T=T)}</g>')
    cells = []
    for r in range(10):
        for c in range(36):
            x, y = gx + c * px, rows_y[r]
            if (r, c) in idle:
                cells.append(f'<rect x="{x}" y="{y}" width="7.5" height="8" rx="1.5" stroke="{T["line"]}" stroke-width=".8"/>')
            else:
                cells.append(f'<rect x="{x}" y="{y}" width="7.5" height="8" rx="1.5" fill="{T["line"]}"/>')
    v.append(f'<g class="fade" style="{d(.15)};animation-duration:1.2s">{"".join(cells)}</g>')

    v.append('<defs>'
             f'<linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="{T["accent"]}" stop-opacity="0"/>'
             f'<stop offset=".8" stop-color="{T["accent"]}" stop-opacity=".55"/><stop offset="1" stop-color="{T["accent"]}" stop-opacity=".9"/></linearGradient>'
             f'<linearGradient id="swc" x1="0" x2="1"><stop offset="0" stop-color="{T["blue"]}" stop-opacity="0"/>'
             f'<stop offset=".8" stop-color="{T["blue"]}" stop-opacity=".45"/><stop offset="1" stop-color="{T["blue"]}" stop-opacity=".85"/></linearGradient>'
             f'<clipPath id="grid"><rect x="{gx}" y="{gy-2}" width="{36*px}" height="120"/></clipPath></defs>')
    hot_h = 3 * py
    cold_h = 7 * py
    v.append('<g clip-path="url(#grid)">'
             f'<rect class="sweep" style="animation-duration:1.5s" x="{gx-28}" y="{gy-2}" width="28" height="{hot_h+1}" fill="url(#sw)"/>'
             f'<rect class="sweep" style="animation-duration:18s" x="{gx-28}" y="{rows_y[3]-2}" width="28" height="{cold_h+1}" fill="url(#swc)"/>'
             '</g>')
    sweep_px = 36 * px + 28
    css.append(f".sweep{{animation:sweep linear .8s infinite both}}@keyframes sweep{{to{{transform:translateX({sweep_px}px)}}}}")

    # a few seats released: lit when the hot sweep passes them, then taken again
    for k, (r, c, nth) in enumerate([(0, 9, 1), (2, 27, 2), (1, 17, 3), (0, 31, 0)]):
        t = 0.8 + (c * px + 28) / sweep_px * 1.5 + nth * 1.5
        base = "" if k == 0 else ";opacity:0"
        v.append(f'<rect class="seat" style="animation-delay:{t:.2f}s{base}" x="{gx + c*px - 1}" y="{rows_y[r] - 1}" '
                 f'width="9.5" height="10" rx="2" fill="{T["ok"]}"/>')
    css.append(".seat{animation:seat 6s linear infinite both}"
               "@keyframes seat{0%{opacity:1}35%{opacity:1}50%,100%{opacity:0}}")

    legend = (f'<text{tc_attr()} x="0" y="134" font-size="9" font-weight="400" fill="{T["muted"]}">'
              f'<tspan fill="{T["ok"]}">■</tspan>{esc(tr(" seat released   "))}'
              f'<tspan fill="{T["muted"]}">□</tspan>{esc(tr(" no sessions (153), checked daily"))}</text>')
    v.append(f'<g class="fade" style="{d(.6)}">{legend}</g>')

    return frame(
        T, "04", "mvdis-watch", "typescript · cloudflare workers · d1", "solo · live",
        [("cadence", "hot ~10 min, cold ~2 h · sweeps to scale"),
         ("budget", "14 of 50 subrequests per run, free tier"),
         ("caveat", "not real-time: the source has no push")],
        "".join(v), "".join(css),
        "mvdis-watch: driving-test seat monitor for 36 stations x 10 license classes",
        "A single Cloudflare Worker rescans 360 station/class combinations: the 108 popular ones about every 10 "
        "minutes, the 252 others about every 2 hours, and 153 combinations with no sessions once a day. It uses 14 "
        "of the 50 allowed subrequests per run on the free plan. It is not real-time because the source has no push.",
    )


# ------------------------------------------------------------------------------------------
def statsbot(T):
    v, css = [], []
    cw, ch = 210, 136
    v.append(f'<g class="fade"><rect x=".5" y=".5" width="{cw}" height="{ch-1}" rx="8" stroke="{T["line"]}"/>'
             + text(10, 16, "# stats-hw", 10, "muted", 500, T=T)
             + f'<path d="M1,24.5 H{cw}" stroke="{T["grid"]}"/></g>')
    v.append(f'<defs><clipPath id="chat"><rect x="1" y="26" width="{cw-1}" height="{ch-28}"/></clipPath></defs>')

    def pair(y, hw, reply):
        s = []
        s.append(f'<circle cx="16" cy="{y+9}" r="6" fill="{T["subtle"]}"/>')
        s.append(text(28, y + 12, "student", 9, "muted", T=T))
        s.append(f'<rect x="28" y="{y+17}" width="74" height="15" rx="3" stroke="{T["line"]}"/>')
        s.append(text(34, y + 28, hw, 9, "fg", T=T))
        s.append(f'<rect x="10" y="{y+36}" width="12" height="12" rx="3" fill="{T["accent"]}"/>')
        s.append(text(28, y + 46, "grader", 9, "accent", 500, T=T))
        s.append(text(72, y + 46, reply, 9, "fg", T=T))
        return "".join(s)

    items = [("hw3.html", "feedback → report"), ("hw3_v2.html", "attempt 2 → report"), ("hw4.html", "feedback → report")]
    ph = 54
    stack = "".join(pair(30 + k * ph, hw, rep) for k, (hw, rep) in enumerate(items + items[:2]))
    v.append(f'<g clip-path="url(#chat)"><g class="scroll">{stack}</g></g>')
    css.append(
        ".scroll{animation:scroll 9s " + EASE_IO + " 1s infinite both}"
        f"@keyframes scroll{{0%,25%{{transform:none}}33%,58%{{transform:translateY(-{ph}px)}}"
        f"66%,91%{{transform:translateY(-{2*ph}px)}}100%{{transform:translateY(-{3*ph}px)}}}}"
    )

    nx, nw = 228, 148
    steps = [("parse .html", 0), ("grade · English", 1), ("grade · statistics", 1), ("report.html + SQLite", 2),
             ("→ Google Drive", 3)]
    for k, (label, stage) in enumerate(steps):
        y = 2 + k * 27
        v.append(f'<g class="in" style="{d(.2 + k*.07)}"><rect x="{nx}" y="{y}" width="{nw}" height="20" rx="5" stroke="{T["line"]}"/>'
                 + text(nx + 10, y + 13.5, label, 9.5, "muted", T=T) + "</g>")
        v.append(f'<rect class="lit" style="animation-delay:{1.6 + stage*.35:.2f}s" x="{nx}" y="{y}" width="{nw}" height="20" '
                 f'rx="5" stroke="{T["accent"]}" fill="{T["accent"]}" fill-opacity=".1"/>')
        if k < len(steps) - 1:
            v.append(f'<path class="fade" style="{d(.5)}" d="M{nx+nw/2},{y+21} v5" stroke="{T["line"]}"/>')
    css.append(".lit{opacity:0;animation:lit 3s linear infinite both}"
               "@keyframes lit{0%{opacity:0}6%{opacity:1}30%{opacity:1}45%,100%{opacity:0}}")

    return frame(
        T, "05", "StatsDiscordBot", "python · discord.py · openai · sqlite", "team of 2",
        [("used by", "~150 students in statistics courses"),
         ("my part", "bot core: login, parsing, LLM calls, Drive"),
         ("keeps", "every attempt, plus an HTML report")],
        "".join(v), "".join(css),
        "StatsDiscordBot: Discord bot that gives feedback on statistics free-response homework",
        "Students upload HTML answers in a class channel; the bot parses them, asks an LLM for feedback on "
        "English expression and statistical content, logs every attempt to SQLite and writes an HTML report that "
        "is synced to Google Drive. Used by about 150 students in statistics courses. Team of two; my part was the "
        "bot itself: login and roles, HTML parsing, LLM calls with timeouts, SQLite, local and Drive storage, admin commands.",
    )


# ------------------------------------------------------------------------------------------
def hoyabit(T):
    v, css = [], []
    P = 7.0
    v.append(f'<g class="fade">{text(0, 8, "A · 8 fetches in parallel", 9.5, "muted", T=T)}'
             f'{text(222, 8, "B · agent fills gaps", 9.5, "muted", T=T)}</g>')
    ends = [0.16, 0.22, 0.12, 0.28, None, 0.19, 0.25, 0.14]  # fraction of period when each lane finishes
    for k, e in enumerate(ends):
        y = 18 + k * 13
        v.append(f'<g class="fade" style="{d(.1 + k*.03)}">{text(0, y + 7, f"s{k+1}", 8.5, "subtle", T=T)}'
                 f'<rect x="22" y="{y}" width="170" height="8" rx="2" fill="{T["grid"]}"/></g>')
        if e is None:
            css.append("@keyframes l4{0%{transform:scaleX(0);fill:" + T["muted"] + "}20%{transform:scaleX(.55);fill:"
                       + T["muted"] + "}23%,86%{transform:scaleX(.55);fill:" + T["bad"] + ";opacity:1}95%,100%{transform:scaleX(.55);"
                       "fill:" + T["bad"] + ";opacity:0}}"
                       "@keyframes x4{0%,22%{opacity:0}25%,86%{opacity:1}95%,100%{opacity:0}}")
            v.append(f'<rect class="lane" style="animation-name:l4" x="22" y="{y}" width="170" height="8" rx="2" fill="{T["bad"]}"/>')
            v.append(f'<g class="lane" style="animation-name:x4">{text(200, y + 7.5, "× timeout", 8.5, "bad", T=T)}</g>')
        else:
            pct = e * 100
            css.append(f"@keyframes l{k}{{0%{{transform:scaleX(0)}}{pct:.0f}%,86%{{transform:scaleX(1);opacity:1}}95%,100%{{transform:scaleX(1);opacity:0}}}}")
            v.append(f'<rect class="lane" style="animation-name:l{k}" x="22" y="{y}" width="170" height="8" rx="2" fill="{T["muted"]}"/>')
    css.append(f".lane{{transform-box:fill-box;transform-origin:left;animation:{P}s {EASE} .6s infinite both}}")

    cx, cy, r = 262, 62, 26
    v.append(f'<circle class="fade" cx="{cx}" cy="{cy}" r="{r}" stroke="{T["line"]}"/>')
    v.append(text(cx, cy + 3.5, "agent", 9.5, "fg", anchor="middle", T=T))
    v.append(f'<g class="phb"><circle class="spin" cx="{cx}" cy="{cy}" r="{r}" pathLength="100" stroke="{T["accent"]}" '
             f'stroke-width="2.4" stroke-dasharray="22 78" stroke-linecap="round"/></g>')
    v.append(f'<g class="phb">{text(cx + r + 8, cy - 8, "+ on-chain", 8.5, "muted", T=T)}'
             f'{text(cx + r + 8, cy + 4, "+ derivatives", 8.5, "muted", T=T)}{text(cx + r + 8, cy + 16, "+ news", 8.5, "muted", T=T)}</g>')
    bx, bw, by = 222, 154, 108
    v.append(f'<g class="fade">{text(bx, by - 6, "time budget", 8.5, "subtle", T=T)}'
             f'<rect x="{bx}" y="{by}" width="{bw}" height="6" rx="3" fill="{T["grid"]}"/>'
             f'<path d="M{bx + bw*.2:.1f},{by-3} v12" stroke="{T["bad"]}"/></g>')
    v.append(f'<rect class="budget" x="{bx}" y="{by}" width="{bw}" height="6" rx="3" fill="{T["accent"]}"/>')
    v.append(f'<g class="conv">{text(bx + bw*.2 - 2, by + 22, "20% left → converge", 8.5, "bad", T=T)}</g>')
    v.append(f'<g class="conv">{text(bx, 134, "→ report, every claim sourced", 9, "ok", T=T)}</g>')
    css.append(
        f".phb{{animation:phb {P}s linear .6s infinite both}}"
        "@keyframes phb{0%,28%{opacity:0}33%,84%{opacity:1}92%,100%{opacity:0}}"
        f".spin{{transform-box:fill-box;transform-origin:center;animation:spin 1.1s linear infinite}}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
        f".budget{{transform-box:fill-box;transform-origin:left;animation:budget {P}s linear .6s infinite both}}"
        "@keyframes budget{0%,30%{transform:none}72%,86%{transform:scaleX(.2);opacity:1}95%,100%{transform:scaleX(.2);opacity:0}}"
        f".conv{{animation:conv {P}s linear .6s infinite both}}"
        "@keyframes conv{0%,72%{opacity:0}75%,86%{opacity:1}95%,100%{opacity:0}}"
    )

    return frame(
        T, "06", "aws-hoyabit", "python · aws · llm agent", "team of 4 · finalist",
        [("my part", "agent loop, 15 data tools, report schema"),
         ("measured", "19/19 test phrasings routed by rules"),
         ("caveat", "information tool, not investment advice")],
        "".join(v), "".join(css),
        "aws-hoyabit: crypto market analysis agent (hackathon finalist)",
        "Phase A fetches eight sources in parallel with bounded concurrency, and one failing source does not "
        "cancel the others. Phase B lets an agent fill gaps until 20% of the time budget remains, then it converges "
        "on a report where every claim cites a source. Question-type routing handled 19 of 19 test phrasings with "
        "rules alone. Team of four (HOYA BIT track finalist); my part was the agent loop, the parallel prefetch, "
        "question routing, the data tools, the report schema and the frontend.",
    )


CARDS = {"zk": zk, "fx": fx, "lending": lending, "mvdis": mvdis, "statsbot": statsbot, "hoyabit": hoyabit}


ZH.update({
    # row labels
    "measured": "實測", "finding": "發現", "used by": "使用者", "decision": "決策", "my part": "我負責",
    "cadence": "頻率", "budget": "用量", "scope": "範圍", "keeps": "保存", "caveat": "限制",
    # chips
    "capstone · NSTC grant": "專題 · 國科會大專生計畫", "re-test · fork": "重新檢驗 · fork",
    "solo · live": "個人 · 運行中", "team of 2": "2 人團隊", "team of 4 · finalist": "4 人團隊 · 決賽",
    # zk
    "clients": "客戶端", "verify π": "驗證 π", "aggregate": "聚合",
    " honest update   ": " 正常更新   ", " in-bound attack": " 範圍內攻擊", " — both verify": " — 都通過驗證",
    "150/150 per-update Halo2 proofs verify": "150/150 份逐更新 Halo2 證明全數通過",
    "synthetic data, 4-param model, 10 rounds": "合成資料、四參數模型、10 輪",
    "300/300 in-bound attacks verify too": "範圍內攻擊也 300/300 通過驗證",
    # fx
    "level error ÷ random walk": "點位誤差 ÷ 隨機漫步", "best p = 0.21 → not significant": "最佳 p = 0.21 → 不顯著",
    "direction: −log10 p (h=5)": "方向：−log10 p（h=5）", " without": " 無特徵",
    "best level model 0.993× RW, p = 0.21": "點位最佳模型 0.993× RW，p = 0.21",
    "UIRP/CIRP features carry direction info": "UIRP/CIRP 特徵對方向有預測力",
    "2 test years × 52 origins × 11 series": "2 個測試年度 × 52 起點 × 11 條序列",
    # lending
    "expected realized APR by offer rate · backtest": "各掛單利率的預期實現年化 · 回測",
    "5.83% · ladder floor": "5.83% · 階梯下限", "rate": "利率", "fill": "成交",
    "fills ≥ FRR in 0 of 250 hours": "250 小時內成交價達到 FRR：0 次",
    "floor 0.018%/day, the backtest optimum": "下限 0.018%/日，回測最佳點",
    "5.83% APR is a backtest, not a promise": "5.83% 年化是回測值，不是保證",
    # mvdis
    "36 stations × 10 license classes = 360 combos": "36 站 × 10 種照類 = 360 組",
    "hot": "熱門", "cold": "冷門", " seat released   ": " 釋出名額   ",
    " no sessions (153), checked daily": " 無場次（153 組），每日檢查",
    "hot ~10 min, cold ~2 h · sweeps to scale": "熱門約 10 分、冷門約 2 小時，速度按比例",
    "14 of 50 subrequests per run, free tier": "每次執行 14／50 個子請求，免費方案",
    "not real-time: the source has no push": "不是即時：官網沒有推播",
    # statsbot
    "student": "學生", "grader": "批改", "feedback → report": "回饋 → 報告", "attempt 2 → report": "第 2 次 → 報告",
    "parse .html": "解析 .html", "grade · English": "評分 · 英文表達", "grade · statistics": "評分 · 統計內容",
    "~150 students in statistics courses": "統計學課程約 150 位學生",
    "bot core: login, parsing, LLM calls, Drive": "Bot 核心：登入、解析、LLM 呼叫、Drive",
    "every attempt, plus an HTML report": "每次提交與 HTML 評分報告",
    # hoyabit
    "A · 8 fetches in parallel": "A · 8 個來源並行抓取", "B · agent fills gaps": "B · Agent 補足缺口",
    "× timeout": "× 逾時", "+ on-chain": "+ 鏈上", "+ derivatives": "+ 衍生品", "+ news": "+ 新聞",
    "time budget": "時間預算", "20% left → converge": "剩 20% → 收斂",
    "→ report, every claim sourced": "→ 報告，每條判斷附來源",
    "agent loop, 15 data tools, report schema": "Agent 迴圈、15 個資料工具、報告 schema",
    "19/19 test phrasings routed by rules": "19/19 種問法由規則判別題型",
    "information tool, not investment advice": "資訊提煉工具，不提供投資建議",
    # titles
    "zk-verifiable-dp-fl: verifiable differential privacy for federated learning": "zk-verifiable-dp-fl：可驗證差分隱私聯邦學習",
    "forcasting-fx-transformer: a re-test of an existing FX forecasting study": "forcasting-fx-transformer：重新檢驗既有的匯率預測研究",
    "bitfinex-lending-bot: funding offers laddered on real fills, not FRR": "bitfinex-lending-bot：依實際成交價（而非 FRR）分層掛單的放貸機器人",
    "mvdis-watch: driving-test seat monitor for 36 stations x 10 license classes": "mvdis-watch：36 個監理站 × 10 種照類的考照名額監測",
    "StatsDiscordBot: Discord bot that gives feedback on statistics free-response homework": "StatsDiscordBot：統計學 FRQ 作業回饋 Discord Bot",
    "aws-hoyabit: crypto market analysis agent (hackathon finalist)": "aws-hoyabit：加密市場分析 AI Agent（黑客松決賽）",
})


def main():
    for lang in ("en", "zh"):
        set_lang(lang)
        for slug, fn in CARDS.items():
            for th, T in THEMES.items():
                write(f"card-{slug}", th, fn(T))
    set_lang("en")


if __name__ == "__main__":
    main()
