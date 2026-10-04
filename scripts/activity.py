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

from svgkit import EASE, THEMES, ZH, document, esc, set_lang, tc_attr, text, tr, write
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
    b.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="{T["panel"]}" stroke="{T["line"]}"/>')
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
