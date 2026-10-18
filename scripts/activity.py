"""Weekly contribution bars for the last year, regenerated daily by GitHub Actions.

Data: GraphQL contributionsCollection (the same numbers the public profile shows).
Token: GITHUB_TOKEN / GH_TOKEN in CI; locally falls back to `gh auth token`.
Zero weeks are drawn as dots on purpose: the gaps are part of the record.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import urllib.request

from svgkit import EASE, EASE_IO, THEMES, ZH, chrome, document, esc, set_lang, smooth_path, tc_attr, text, tr, write
import svgkit

USER = "ChiJiun"
W, H = 840, 224
X0, X1, BASE, TOP = 44, 800, 160, 62

QUERY = """query($login:String!){user(login:$login){contributionsCollection{
  totalCommitContributions totalPullRequestContributions
  contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


ZH.update({
    "contributions per week · last 12 months": "每週貢獻 · 近 12 個月",
    "refreshed daily by GitHub Actions": "每日由 GitHub Actions 更新",
    "— 4-week average": "— 四週平均",
})


def token() -> str:
    for k in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(k):
            return os.environ[k]
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def fetch() -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token()}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]["user"]["contributionsCollection"]


def build(theme: str, data: dict, today: dt.date) -> str:
    T = THEMES[theme]
    cal = data["contributionCalendar"]
    weeks = [(dt.date.fromisoformat(w["contributionDays"][0]["date"]), sum(d["contributionCount"] for d in w["contributionDays"]))
             for w in cal["weeks"]]
    n = len(weeks)
    vmax = max(v for _, v in weeks) or 1
    pitch = (X1 - X0) / n
    bw = pitch * 0.62
    zeros = sum(1 for _, v in weeks if v == 0)
    total = cal["totalContributions"]

    b, css = [], []
    defs, bg, kcss = chrome(T, W, H, 14, glow_at=(0.5, 0.0))
    css.append(kcss)
    b.append(defs)
    b.append(bg)
    # last four weeks: a soft band behind the bars
    band_x = X0 + (n - 4) * pitch
    b.append(f'<rect class="fade" style="animation-delay:1.1s" x="{band_x:.1f}" y="{TOP - 14}" width="{4 * pitch:.1f}" '
             f'height="{BASE - TOP + 14}" rx="4" fill="{T["accent"]}" fill-opacity=".07"/>')
    b.append(f'<g class="fade">{text(X0, 36, "contributions per week · last 12 months", 12, "muted", T=T)}</g>')
    num = lambda v: f'<tspan fill="{T["fg"]}" font-weight="500">{v}</tspan>'
    c, p = data["totalCommitContributions"], data["totalPullRequestContributions"]
    if svgkit.LANG == "zh":
        inner = f"總計 {num(total)} · commit {num(c)} · PR {num(p)}"
    else:
        inner = f"{num(total)} total · {num(c)} commits · {num(p)} PRs"
    head = (f'<text{tc_attr()} x="{X1}" y="36" font-size="12" font-weight="400" text-anchor="end" fill="{T["muted"]}">'
            f"{inner}</text>")
    b.append(f'<g class="fade">{head}</g>')
    b.append(f'<path d="M{X0},{BASE + .5} H{X1}" stroke="{T["line"]}"/>')

    peak_i = max(range(n), key=lambda i: weeks[i][1])
    last_month = None
    for i, (start, v) in enumerate(weeks):
        x = X0 + i * pitch + (pitch - bw) / 2
        delay = 0.25 + i * 0.016
        if v == 0:
            b.append(f'<circle class="fade" style="animation-delay:{delay:.2f}s" cx="{x + bw/2:.1f}" cy="{BASE - 3}" r="1.6" fill="{T["subtle"]}"/>')
        else:
            h = max(3.0, v / vmax * (BASE - TOP))
            op = 0.4 + 0.6 * (v / vmax) ** 0.6
            b.append(f'<rect class="grow" style="animation-delay:{delay:.2f}s" x="{x:.1f}" y="{BASE - h:.1f}" width="{bw:.1f}" '
                     f'height="{h:.1f}" rx="2" fill="{T["accent"]}" fill-opacity="{op:.2f}"/>')
        mid = start + dt.timedelta(days=3)
        if mid.month != last_month:
            if last_month is not None or mid.day <= 7:
                b.append(f'<g class="fade" style="animation-delay:.4s">{text(x + bw/2, BASE + 21, (f"{mid.month}月" if svgkit.LANG == "zh" else mid.strftime("%b")), 10, "subtle", anchor="middle", T=T)}</g>')
            last_month = mid.month

    # 4-week moving average, drawn as a phosphor line with afterglow
    ma = []
    for i in range(n):
        win = [v for _, v in weeks[max(0, i - 3): i + 1]]
        ma.append(sum(win) / len(win))
    ma_pts = [(X0 + i * pitch + pitch / 2, BASE - max(1.5, m / vmax * (BASE - TOP))) for i, m in enumerate(ma)]
    ma_d = smooth_path(ma_pts, 0.6)
    b.append(f'<path class="ma" pathLength="1" stroke-dasharray="1" d="{ma_d}" stroke="{T["ok"]}" stroke-width="4" '
             f'stroke-opacity=".35" filter="url(#k-blur)"/>')
    b.append(f'<path class="ma" pathLength="1" stroke-dasharray="1" d="{ma_d}" stroke="{T["ok"]}" stroke-width="1.6" stroke-linejoin="round"/>')
    b.append(f'<g class="fade" style="animation-delay:2.2s">{text(W / 2, 206, tr("— 4-week average"), 10, "ok", anchor="middle", T=T)}</g>')

    # ---- looping playhead: a cursor sweeps the year, lights each bar, and a readout follows -------
    LOOP, L0 = 14.0, 2.8  # seconds per sweep, start after the entrance
    span = (n - 1) * pitch
    step_pct = 100.0 / (n - 1)
    css.append(f".ph{{opacity:0;animation:ph {LOOP}s linear {L0}s infinite both}}"
               f"@keyframes ph{{0%{{opacity:0;transform:none}}2%{{opacity:1}}96%{{opacity:1}}100%{{opacity:0;transform:translateX({span:.1f}px)}}}}")
    x_first = X0 + pitch / 2
    b.append(f'<g class="ph"><rect x="{x_first - 1:.1f}" y="{TOP - 12}" width="2" height="{BASE - TOP + 12}" fill="{T["fg"]}" fill-opacity=".55"/>'
             f'<rect x="{x_first - 3:.1f}" y="{TOP - 12}" width="6" height="{BASE - TOP + 12}" fill="{T["accent"]}" fill-opacity=".35" filter="url(#k-blur)"/></g>')
    # each bar flares as the cursor passes
    for i, (start, v) in enumerate(weeks):
        if v == 0:
            continue
        x = X0 + i * pitch + (pitch - bw) / 2
        h = max(3.0, v / vmax * (BASE - TOP))
        p = i * step_pct
        a, c = max(0.0, p - 1.5), min(100.0, p + 7)
        css.append(f"@keyframes f{i}{{0%,{a:.1f}%{{opacity:0}}{p:.1f}%{{opacity:.8}}{c:.1f}%,100%{{opacity:0}}}}")
        b.append(f'<rect class="fl" style="animation-name:f{i}" x="{x:.1f}" y="{BASE - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="2" fill="{T["fg"]}"/>')
    css.append(f".fl{{opacity:0;animation:{LOOP}s linear {L0}s infinite both}}")
    # a phosphor dot rides the 4-week average under the cursor
    stops = "".join(f"{i * step_pct:.1f}%{{transform:translate({x - x_first:.1f}px,{y - ma_pts[0][1]:.1f}px)}}" for i, (x, y) in enumerate(ma_pts))
    css.append(f"@keyframes mdot{{{stops}}}"
               f".mdot{{animation:mdot {LOOP}s linear {L0}s infinite both}}"
               f".mdotv{{opacity:0;animation:mdotv {LOOP}s linear {L0}s infinite both}}@keyframes mdotv{{0%{{opacity:0}}2%,96%{{opacity:1}}100%{{opacity:0}}}}")
    b.append(f'<g class="mdotv"><g class="mdot"><circle cx="{ma_pts[0][0]:.1f}" cy="{ma_pts[0][1]:.1f}" r="7" fill="{T["ok"]}" fill-opacity=".35" filter="url(#k-blur)"/>'
             f'<circle cx="{ma_pts[0][0]:.1f}" cy="{ma_pts[0][1]:.1f}" r="3" fill="{T["panel"]}" stroke="{T["ok"]}" stroke-width="1.5"/></g></g>')
    # readout in the title row (between the title and the totals): one text per week, shown while the cursor is on it
    ro_x, ro_y = 350, 36
    for i, (start, v) in enumerate(weeks):
        p = i * step_pct
        a, c = max(0.0, p - step_pct / 2), min(100.0, p + step_pct / 2)
        last = i == n - 1
        if svgkit.LANG == "zh":
            s = f"{start.month}/{start.day} 那週 · {v} 次貢獻"
        else:
            s = f"{start.strftime('%b')} {start.day} · {v} contribution{'s' if v != 1 else ''}"
        css.append(f"@keyframes r{i}{{0%,{a:.2f}%{{opacity:{1 if last else 0}}}{a + 0.01:.2f}%,{c:.2f}%{{opacity:1}}{c + 0.01:.2f}%,100%{{opacity:0}}}}"
                   if not last else
                   f"@keyframes r{i}{{0%,{a:.2f}%{{opacity:0}}{a + 0.01:.2f}%,100%{{opacity:1}}}}")
        b.append(f'<g class="ro" style="animation-name:r{i};opacity:{1 if last else 0}">'
                 f'{text(ro_x, ro_y, s, 10.5, "accent", 500, T=T)}</g>')
    css.append(f".ro{{animation:{LOOP}s linear {L0}s infinite both}}")

    px = X0 + peak_i * pitch + pitch / 2
    ph = weeks[peak_i][1] / vmax * (BASE - TOP)
    pk = weeks[peak_i][0]
    if svgkit.LANG == "zh":
        label = f"高峰 {weeks[peak_i][1]} · {pk.month}/{pk.day} 那週"
    else:
        label = f"peak {weeks[peak_i][1]} · week of {pk.strftime('%b')} {pk.day}"
    anchor = "end" if peak_i > n * 0.7 else "start"
    lx = px + (6 if anchor == "start" else -6)
    b.append(f'<g class="fade" style="animation-delay:1.3s"><path d="M{px:.1f},{BASE - ph - 4:.1f} V{TOP - 8}" stroke="{T["subtle"]}" stroke-dasharray="2 2"/>'
             f'{text(lx, TOP - 4, label, 10.5, "fg", anchor=anchor, T=T)}</g>')
    b.append(f'<circle class="pk" style="animation-delay:1.3s" cx="{px:.1f}" cy="{BASE - ph:.1f}" r="3" fill="{T["panel"]}" stroke="{T["accent"]}" stroke-width="1.5"/>'
             f'<circle class="ring" style="animation-delay:2.4s" cx="{px:.1f}" cy="{BASE - ph:.1f}" r="3" stroke="{T["accent"]}"/>')

    lx_last = X0 + (n - 1) * pitch + pitch / 2
    b.append(f'<circle class="ring" cx="{lx_last:.1f}" cy="{BASE + 6}" r="2.5" stroke="{T["accent"]}"/>'
             f'<circle cx="{lx_last:.1f}" cy="{BASE + 6}" r="2.5" fill="{T["accent"]}"/>')
    b.append(f'<rect class="sweep" x="{X0 - 2}" y="{TOP - 14}" width="2" height="{BASE - TOP + 14}" fill="{T["fg"]}"/>')

    note = (f"集中衝刺，不追連續紀錄：{n} 週中有 {zeros} 週沒有貢獻。" if svgkit.LANG == "zh"
            else f"Sprints, not streaks: {zeros} of {n} weeks had none.")
    b.append(f'<g class="fade" style="animation-delay:1.6s">{text(X0, 206, note, 11, "muted", T=T)}'
             f'{text(X1, 206, "refreshed daily by GitHub Actions", 10, "subtle", anchor="end", T=T)}</g>')

    css.append(
        f".fade{{animation:fade .8s {EASE} both}}@keyframes fade{{from{{opacity:0}}}}"
        f".grow{{transform-box:fill-box;transform-origin:bottom;animation:grow .9s {EASE} both}}"
        "@keyframes grow{from{transform:scaleY(0)}}"
        f".sweep{{opacity:0;animation:sweep 1.6s cubic-bezier(.65,0,.35,1) .25s both}}"
        f"@keyframes sweep{{0%{{opacity:.5;transform:none}}90%{{opacity:.5}}100%{{opacity:0;transform:translateX({X1 - X0 + 2}px)}}}}"
        ".ring{transform-box:fill-box;transform-origin:center;animation:ring 2.2s ease-out 2s infinite both}"
        "@keyframes ring{from{transform:scale(1);opacity:.9}to{transform:scale(2.4);opacity:0}}"
        f".ma{{animation:ma 2.2s {EASE_IO} 1.2s both}}@keyframes ma{{from{{stroke-dashoffset:1}}}}"
        f".pk{{transform-box:fill-box;transform-origin:center;animation:pop .5s {EASE} both}}@keyframes pop{{from{{transform:scale(0)}}}}"
    )
    return document(
        W, H, "".join(b), "".join(css),
        f"{total} contributions in the last 12 months",
        f"Weekly contribution counts for the last {n} weeks: {total} total, {data['totalCommitContributions']} commits, "
        f"{data['totalPullRequestContributions']} pull requests. Peak week: {weeks[peak_i][1]}. {zeros} weeks had none.",
    )


def main():
    data = fetch()
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date()
    for lang in ("en", "zh"):
        set_lang(lang)
        for th in THEMES:
            write("activity", th, build(th, data, today))
    set_lang("en")


if __name__ == "__main__":
    main()
