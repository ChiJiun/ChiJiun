"""Write the README variants: English / 繁體中文 × auto / dark / light.

GitHub shows README.md on the profile, so it is the default: English, and the
images follow the viewer's own GitHub theme through <picture>. Every image is an
opaque panel, so a fixed theme would sit as a hard dark block on a light page (or a
glaring white one on a dark page) for whoever uses the other theme. Matching the
viewer avoids that, and the switcher still offers a fixed dark or light version.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/ChiJiun/ChiJiun/blob/main/"
FILES = {("en", "auto"): "README.md", ("en", "dark"): "README.dark.md", ("en", "light"): "README.light.md",
         ("zh", "auto"): "README.zh-TW.md", ("zh", "dark"): "README.zh-TW.dark.md",
         ("zh", "light"): "README.zh-TW.light.md"}


def url(lang, theme):
    return "https://github.com/ChiJiun" if (lang, theme) == ("en", "auto") else REPO + FILES[(lang, theme)]


def switcher(lang, theme):
    def opt(label, l, t, current):
        return f"<b>{label}</b>" if current else f'<a href="{url(l, t)}">{label}</a>'
    langs = " · ".join([opt("English", "en", theme, lang == "en"), opt("繁體中文", "zh", theme, lang == "zh")])
    names = ("Auto", "Dark", "Light") if lang == "en" else ("自動", "深色", "淺色")
    themes = " · ".join(opt(n, lang, t, theme == t) for n, t in zip(names, ("auto", "dark", "light")))
    return f'<p align="right"><sub>{langs} &nbsp;│&nbsp; {themes}</sub></p>'


def img(name, lang, theme, alt, width="100%"):
    base = f"./assets/{name}{'-zh' if lang == 'zh' else ''}"
    if theme != "auto":
        return f'<img alt="{alt}" src="{base}-{theme}.svg" width="{width}">'
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{base}-dark.svg">'
            f'<source media="(prefers-color-scheme: light)" srcset="{base}-light.svg">'
            f'<img alt="{alt}" src="{base}-dark.svg" width="{width}"></picture>')


CARDS = [
    ("zk", "zk-verifiable-dp-fl",
     "zk-verifiable-dp-fl: 150/150 per-update Halo2 proofs verify on synthetic data; 300/300 in-bound attacks verify too.",
     "zk-verifiable-dp-fl：合成資料上 150/150 份逐更新 Halo2 證明通過；範圍內攻擊也 300/300 通過。"),
    ("lending", "bitfinex-lending-bot",
     "bitfinex-lending-bot: offers laddered on real fills; FRR was never reached in 250 hours.",
     "bitfinex-lending-bot：依實際成交價分層掛單；250 小時內成交價從未達到 FRR。"),
    ("mvdis", "mvdis-watch",
     "mvdis-watch: 360 station and license-class combinations rescanned on one Cloudflare Worker, free tier.",
     "mvdis-watch：單一 Cloudflare Worker 在免費方案內掃描 360 組監理站 × 照類。"),
    ("statsbot", "StatsDiscordBot",
     "StatsDiscordBot: statistics homework feedback bot used by about 150 students; I built the bot core: login, HTML parsing, LLM calls, storage and Drive sync.",
     "StatsDiscordBot：約 150 位學生使用的統計作業回饋 Bot；我負責 Bot 核心：登入、HTML 解析、LLM 呼叫、儲存與 Drive 同步。"),
    ("hoyabit", "aws-hoyabit",
     "aws-hoyabit: crypto market analysis agent; my part was the agent loop, parallel prefetch, question routing, 15 data tools and the report schema.",
     "aws-hoyabit：加密市場分析 Agent；我負責 Agent 迴圈、並行預抓、題型判別、15 個資料工具與報告 schema。"),
]

TEXT = {
    "en": dict(
        hero_alt="The world is one giant makeshift troupe, so fake it till you make it. Chi-Jiun Wong (翁祺鈞). CS undergrad at NCU, minor in finance. Verifiable-ML prototypes and small bots that run on free tiers.",
        intro=("My NSTC undergraduate research project at National Central University (Taiwan) is "
               "verifiable differential privacy for federated learning. Outside it I build small tools "
               "that run on free tiers.\n\n"
               "Every number on this page comes from the linked repo's README or result files, and each one sits next to its limit. "
               "Team projects describe only my part."),
        selected="Selected work", also="Also", activity="Activity",
        also_head="| repo | what | my part |",
        also_rows=[
            "| [NCU_AI_Guidance](https://github.com/ChiJiun/NCU_AI_Guidance) | NCU course-advisor platform (team project) | Deployed the frontend to Firebase and the API to Render, moved research-plan PDFs to Cloudinary; Firebase Google sign-in; chat history in PostgreSQL for signed-in users; Qdrant / Cloudinary monitor page |",
            "| [forcasting-fx-transformer](https://github.com/ChiJiun/forcasting-fx-transformer) | Fork of a senior's FX forecasting project | Added a leakage-free rolling-origin backtest to re-check the original results |",
            "| [usdt-invoice-pulse](https://github.com/ChiJiun/usdt-invoice-pulse) | Daily USDT/TWD fee-target and e-invoice dashboard; live orders off by default | everything |",
            "| [worldquant](https://github.com/ChiJiun/worldquant) | WorldQuant BRAIN API simulator with a one-change-at-a-time alpha research loop | everything |",
            "| [onework](https://github.com/ChiJiun/onework) | Spring Boot + PostgreSQL meeting-room booking API with conflict guards, approvals and Testcontainers | everything |",
        ],
        activity_alt="Weekly contributions over the last 12 months, regenerated daily.",
        how="How this page is built",
        quote="“The world is one giant makeshift troupe.” (a Chinese internet saying)",
        how_items=[
            "Every image is an SVG generated by `scripts/`. Fira Code and Noto Sans TC (both OFL) are subset to the glyphs used and inlined, so the text looks the same on every machine.",
            "All motion is CSS keyframes. With reduced motion turned on you get the last frame, which is a complete picture.",
            "The images follow your GitHub theme by default; the switcher at the top pins dark or light.",
            "No third-party stats services. The activity chart is rebuilt every day by GitHub Actions from the GraphQL contribution calendar.",
            "`python scripts/build.py` regenerates the images; `python scripts/readme.py` writes the four README variants.",
        ],
    ),
    "zh": dict(
        hero_alt="這個世界就是一個巨大的草台班子，所以弄假直到成真。翁祺鈞 Chi-Jiun Wong。中央大學資工系，輔系財金。做可驗證機器學習的原型，也做幾個跑在免費額度上的小工具。",
        intro=("目前在做國科會大專生計畫「可驗證差分隱私聯邦學習」；其餘時間做幾個跑在免費額度上的小工具。\n\n"
               "這頁上的數字都直接取自各 repo 的 README 或實驗結果，每個數字旁邊都寫出它的限制。團隊專案只寫我負責的部分。"),
        selected="精選作品", also="其他", activity="活動",
        also_head="| repo | 內容 | 我負責 |",
        also_rows=[
            "| [NCU_AI_Guidance](https://github.com/ChiJiun/NCU_AI_Guidance) | 中央大學選課助理平台（團隊專案） | 前端部署到 Firebase、API 部署到 Render、研究計畫 PDF 移到 Cloudinary；Firebase Google 登入；已登入使用者的聊天紀錄存進 PostgreSQL；Qdrant／Cloudinary 監控頁 |",
            "| [forcasting-fx-transformer](https://github.com/ChiJiun/forcasting-fx-transformer) | 學長匯率預測專題的 fork | 加入無資料洩漏的 rolling-origin 回測，重新檢驗原本的結果 |",
            "| [usdt-invoice-pulse](https://github.com/ChiJiun/usdt-invoice-pulse) | 每日 USDT/TWD 手續費目標與發票紀錄 dashboard，預設不送出真實訂單 | 全部 |",
            "| [worldquant](https://github.com/ChiJiun/worldquant) | WorldQuant BRAIN API simulator，搭配一次只改一個變因的 alpha 研究流程 | 全部 |",
            "| [onework](https://github.com/ChiJiun/onework) | Spring Boot + PostgreSQL 會議室預約 API，內含衝突防護、審核流程與 Testcontainers | 全部 |",
        ],
        activity_alt="近 12 個月的每週貢獻，每日重新產生。",
        how="這頁怎麼做的",
        quote="「這個世界就是一個巨大的草台班子。」（網路流行語）",
        how_items=[
            "所有圖片都是 `scripts/` 產生的 SVG。Fira Code 與 Noto Sans TC（皆為 OFL 授權）只取用到的字元並內嵌，任何機器上顯示都一樣。",
            "動畫全部用 CSS keyframes 製作。系統開啟「減少動態效果」時直接顯示最後一格，而最後一格本身就是完整的畫面。",
            "圖片預設跟隨你的 GitHub 主題；最上方的切換列可以固定為深色或淺色。",
            "沒有使用第三方統計卡片服務。活動圖由 GitHub Actions 每天用 GraphQL 貢獻資料重新產生。",
            "`python scripts/build.py` 重新產生圖片；`python scripts/readme.py` 產生四個語言／主題版本的 README。",
        ],
    ),
}


EMAIL = "0311gino@gmail.com"
LINKTREE = "https://linktr.ee/0311gino"


def contact(lang):
    label = "Contact" if lang == "en" else "聯絡"
    return (f"**{label}** · [{EMAIL}](mailto:{EMAIL}) · "
            f"[linktr.ee/0311gino]({LINKTREE})")


def render(lang, theme):
    t = TEXT[lang]
    out = ["<!-- Generated by scripts/readme.py. Edit that file, not this one. -->", "", switcher(lang, theme), "",
           img("hero", lang, theme, t["hero_alt"]), "", t["intro"], "", f"### {t['selected']}", ""]
    slug, repo, alt_en, alt_zh = CARDS[0]  # featured: full width
    out.append(f'<a href="https://github.com/ChiJiun/{repo}">{img("card-" + slug, lang, theme, alt_zh if lang == "zh" else alt_en)}</a>')
    out.append("")
    for i in range(1, len(CARDS), 2):
        out.append("<p>")
        for slug, repo, alt_en, alt_zh in CARDS[i:i + 2]:
            out.append(f'<a href="https://github.com/ChiJiun/{repo}">{img("card-" + slug, lang, theme, alt_zh if lang == "zh" else alt_en, "49%")}</a>')
        out.append("</p>")
    out += ["", f"### {t['also']}", "", t["also_head"], "|:--|:--|:--|", *t["also_rows"], "",
            f"### {t['activity']}", "", img("activity", lang, theme, t["activity_alt"]), "",
            "<details>", f"<summary><sub>{t['how']}</sub></summary>", "<br>", "",
            *[f"- {x}" for x in t["how_items"]], "", "</details>", ""]
    return "\n".join(out)


def main():
    for (lang, theme), name in FILES.items():
        (ROOT / name).write_text(render(lang, theme), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
