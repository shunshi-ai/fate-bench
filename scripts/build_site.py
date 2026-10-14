#!/usr/bin/env python3
"""Build the browsable site served by GitHub Pages from `docs/`.

Every page is rendered to static HTML here rather than assembled in the browser: the questions
are the content, and a crawler that does not run JavaScript should still see all of them. The
small script on each page only adds the "pick an answer, see if you were right" interaction;
without it, each question still has a <details> that reveals the answer.

    python scripts/build_site.py            # writes docs/*.html
    python scripts/build_site.py --check    # build in memory, validate, write nothing
"""
import argparse
import html
import json
import sys
import urllib.parse
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QA = ROOT / "data" / "hkjfma_qa.json"
CASES = ROOT / "data" / "cases.json"
BASELINE = ROOT / "data" / "human_baseline.json"
OUT = ROOT / "docs"

BASE_URL = "https://shunshi-ai.github.io/fate-bench"
REPO = "https://github.com/shunshi-ai/fate-bench"
SHUNSHI = "https://shunshi.ai/zh-tw?utm_source=github&utm_medium=fate-bench&utm_campaign=site"
CN_NUM = "零一二三四五六七八九十"
PILLARS = (("year", "年柱"), ("month", "月柱"), ("day", "日柱"), ("hour", "時柱"))


def e(s) -> str:
    return html.escape(str(s), quote=True)


def edition_cn(n: int) -> str:
    if n <= 10:
        return CN_NUM[n] if n < 10 else "十"
    return "十" + CN_NUM[n - 10]


CSS = """
:root{--bg:#faf6ed;--card:#fffdf8;--ink:#2a2420;--muted:#7a6f63;--line:#e6dccb;--accent:#8a5a2b;
--ok:#2f7d4f;--ok-bg:#e5f3ea;--bad:#b23a3a;--bad-bg:#f8e3e1;--chip:#f1e8d8}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1c1916;--card:#25211d;--ink:#eee6da;
--muted:#a89c8d;--line:#3a332c;--accent:#d9a46a;--ok:#6cc08d;--ok-bg:#1f3428;--bad:#e07b74;--bad-bg:#3a2321;--chip:#302a24}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.7 -apple-system,"PingFang TC","Noto Sans TC","Microsoft JhengHei",sans-serif}
a{color:var(--accent)}
.wrap{max-width:880px;margin:0 auto;padding:0 16px}
header.top{border-bottom:1px solid var(--line);padding:14px 0}
header.top .wrap{display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap}
header.top a.brand{font-weight:700;text-decoration:none;color:var(--ink)}
nav.years{display:flex;gap:6px;flex-wrap:wrap;margin:18px 0}
nav.years a{padding:4px 10px;border:1px solid var(--line);border-radius:999px;text-decoration:none;color:var(--ink);font-size:14px;background:var(--card)}
nav.years a.on{background:var(--ink);color:var(--bg);border-color:var(--ink)}
h1{font-size:28px;line-height:1.3;margin:28px 0 8px}
h2{font-size:21px;margin:36px 0 12px}
.sub{color:var(--muted);margin:0 0 16px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:18px 0}
.stat{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.stat b{display:block;font-size:22px}
.stat span{color:var(--muted);font-size:13px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin:18px 0}
.case-h{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:baseline}
.case-h h3{margin:0;font-size:18px}
.meta{color:var(--muted);font-size:14px}
.birth{margin:10px 0;padding:10px 12px;background:var(--chip);border-radius:10px;font-size:15px}
table.pillars{border-collapse:collapse;margin:10px 0;width:100%;max-width:420px;text-align:center}
table.pillars th,table.pillars td{border:1px solid var(--line);padding:4px 6px}
table.pillars th{font-weight:500;color:var(--muted);font-size:13px}
table.pillars td.gz{font-size:20px;letter-spacing:2px}
table.pillars td.tg{font-size:12px;color:var(--muted)}
.luck{font-size:13px;color:var(--muted);overflow-x:auto;white-space:nowrap;padding-bottom:4px}
.luck span{display:inline-block;margin-right:10px}
.q{border-top:1px dashed var(--line);padding-top:14px;margin-top:14px}
.q p.stem{margin:0 0 8px;font-weight:600}
.opts{display:grid;gap:6px}
.opts button{all:unset;cursor:pointer;display:block;padding:8px 12px;border:1px solid var(--line);border-radius:10px;background:var(--bg)}
.opts button:hover{border-color:var(--accent)}
.opts button.ok{background:var(--ok-bg);border-color:var(--ok);color:var(--ok)}
.opts button.bad{background:var(--bad-bg);border-color:var(--bad);color:var(--bad)}
.opts button[disabled]{cursor:default}
details.ans{margin-top:6px;font-size:14px;color:var(--muted)}
.tag{display:inline-block;font-size:12px;padding:1px 8px;border-radius:999px;background:var(--chip);color:var(--muted);margin-left:6px}
.tag.warn{color:var(--bad)}
.score{position:sticky;bottom:12px;margin:24px auto;max-width:520px;background:var(--ink);color:var(--bg);border-radius:999px;padding:8px 16px;text-align:center;font-size:14px}
table.ed{width:100%;border-collapse:collapse;font-size:15px}
table.ed th,table.ed td{border-bottom:1px solid var(--line);padding:8px 6px;text-align:left}
table.ed td.n{text-align:right;white-space:nowrap}
.cta{display:block;text-align:center;margin:28px 0;padding:14px;border-radius:12px;background:var(--ink);color:var(--bg);text-decoration:none;font-weight:600}
footer{border-top:1px solid var(--line);margin-top:40px;padding:20px 0 40px;color:var(--muted);font-size:13px}
@media (max-width:520px){h1{font-size:23px}.card{padding:14px}table.pillars td.gz{font-size:17px}}
"""

JS = """
(function(){var done=0,right=0,el=document.getElementById('score');
document.querySelectorAll('.q').forEach(function(q){var ans=q.dataset.answer;
q.querySelectorAll('.opts button').forEach(function(b){b.addEventListener('click',function(){
if(q.dataset.done)return;q.dataset.done=1;done++;
q.querySelectorAll('.opts button').forEach(function(x){x.disabled=true;if(x.dataset.l===ans)x.classList.add('ok')});
if(b.dataset.l===ans){right++}else{b.classList.add('bad')}
var d=q.querySelector('details');if(d)d.open=true;
if(el){el.hidden=false;el.textContent='你已作答 '+done+' 題，答對 '+right+' 題'+(el.dataset.best?' · '+el.dataset.best:'')}
})})})})();
"""


def page(title, desc, canonical, body, years, current=None):
    nav = "".join(f'<a href="{y}.html"{" class=on" if y == current else ""}>{y}</a>' for y in years)
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary">
<style>{CSS}</style>
</head>
<body>
<header class="top"><div class="wrap">
<a class="brand" href="index.html">全球算命師大賽 歷屆真題</a>
<span class="meta"><a href="{REPO}">GitHub</a> · <a href="{SHUNSHI}">ShunShi.ai</a></span>
</div></header>
<main class="wrap">
<nav class="years" aria-label="屆次"><a href="index.html"{" class=on" if current is None else ""}>總覽</a>{nav}</nav>
{body}
</main>
<footer><div class="wrap">
題目與答案出自香港青年術數家協會「全球算命師大賽」（<a href="https://hkjfma.org">hkjfma.org</a>），版權屬原作者，此處僅作整理與引用。
2022–2025 題目經 <a href="https://github.com/DestinyLinker/MingLi-Bench">MingLi-Bench</a>（MIT）、2021 答案經 <a href="https://github.com/ChenJiangxi/BaziQA">BaziQA</a>（MIT）。
八字由第三方庫 lunar-python 排出，時間依原題，未做真太陽時校正。
彙編資料以 <a href="{REPO}/blob/main/LICENSE-DATA">CC BY 4.0</a> 釋出 · 整理：<a href="{SHUNSHI}">ShunShi.ai</a> · <a href="{REPO}">原始碼與資料</a>
</div></footer>
<script>{JS}</script>
</body>
</html>
"""


def source_label(url):
    u = urllib.parse.unquote(url)
    return "MingLi-Bench" if "github.com" in u else "hkjfma.org · " + u.rstrip("/").rsplit("/", 1)[-1]


def birth_line(b):
    """由结构化字段拼一句干净的生辰。原文（常混着英文对照、师傅网址）另放在折叠里。"""
    if b.get("missing"):
        return "主辦方網頁未刊登此命例的生辰（比賽紙本上有）—— 本例無法排盤。"
    parts = []
    if g := b.get("gender"):
        parts.append(f"{g}命")
    if b.get("year"):
        d = f"西曆 {b['year']} 年 {b.get('month', '?')} 月 {b.get('day', '?')} 日"
        # 原文给时辰时，钟点常是时辰起点（2018 的 `7:00 – 9:00AM`），不是确切时刻 —— 只在
        # 有分钟、或时辰本就由钟点推出时才显示钟点
        clock = b.get("clock_hour") is not None and (
            b.get("clock_minute") or b.get("shichen_derived_from_clock") or not b.get("shichen"))
        if clock:
            d += f" {b['clock_hour']:02d}:{b.get('clock_minute', 0):02d}"
        if z := b.get("shichen"):
            d += f"（{z}時）"
        elif b.get("clock_hour") is None:
            d += "（時辰未知）"
        parts.append(d)
    if loc := b.get("location"):
        parts.append(f"{loc}出生")
    return " · ".join(parts) or (b.get("raw") or "")


def chart_html(case):
    bz = ((case or {}).get("charts") or {}).get("bazi")
    if not bz:
        return ""
    p, tg = bz["pillars"], bz.get("ten_gods", {})
    cols = [(lab, p.get(k)) for k, lab in PILLARS if p.get(k)]
    head = "".join(f"<th>{lab}</th>" for lab, _ in cols)
    gz = "".join(f'<td class="gz">{e(v)}</td>' for _, v in cols)
    tgs = "".join(f'<td class="tg">{e(tg.get(k, ""))}</td>' for k, lab in PILLARS if p.get(k))
    luck = ""
    if lc := bz.get("luck_cycles"):
        items = [f'<span>{c["ganzhi"]} {c["years"][0]}–{c["years"][1]}</span>'
                 for c in lc.get("cycles", []) if c.get("ganzhi")]
        luck = f'<div class="luck">大運（{e(lc.get("direction", ""))}，{e(lc.get("starts", ""))} 起）：{"".join(items)}</div>'
    return (f'<table class="pillars"><tr>{head}</tr><tr>{gz}</tr><tr>{tgs}</tr></table>{luck}')


def question_html(r):
    opts = "".join(f'<button type="button" data-l="{o["letter"]}">{o["letter"]}. {e(o["text"])}</button>'
                   for o in r["options"])
    cat = f'<span class="tag">{e(r["category"])}</span>' if r.get("category") else ""
    return (f'<div class="q" id="q{r["question_number"]}" data-answer="{r["answer"]}">'
            f'<p class="stem">Q{r["question_number"]}. {e(r["question"])}{cat}</p>'
            f'<div class="opts">{opts}</div>'
            f'<details class="ans"><summary>看答案</summary>正確答案：{r["answer"]}</details></div>')


def year_page(year, rows, cases, ed_base, years):
    first = rows[0]
    ed = first["edition"]
    third = first.get("answer_provenance") == "third-party"
    best = (ed_base or {}).get("best_raw_overall")
    by_case = defaultdict(list)
    for r in rows:
        by_case[r["case_id"]].append(r)
    blocks = []
    for i, (cid, qs) in enumerate(by_case.items(), 1):
        q0 = qs[0]
        who = " · ".join(x for x in (q0.get("master"), q0.get("method")) if x)
        blocks.append(
            f'<section class="card" id="c{i}"><div class="case-h"><h3>命例 {i}</h3>'
            f'<span class="meta">{e(who)}</span></div>'
            f'<div class="birth">{e(birth_line(q0["birth_info"]))}'
            + (f'<details class="ans"><summary>原題生辰原文</summary>{e(q0["birth_info"]["raw"])}</details>'
               if q0["birth_info"].get("raw") else "") + '</div>'
            f'{chart_html(cases.get(cid))}'
            + "".join(question_html(r) for r in qs) + "</section>")
    title = f"{year} 第{edition_cn(ed)}屆全球算命師大賽 真題與答案（{len(rows)} 題）"
    best_txt = (f"本屆職業命理師最高 {best['score']}/{best['of']}（{best['accuracy']:.1%}）"
                if best else "本屆未公布參賽者成績")
    intro = (f'<h1>{e(title)}</h1>'
             f'<p class="sub">{len(by_case)} 個真實命例、{len(rows)} 道選擇題，每題都有出題師傅掌握的真實經歷作答案。'
             f'先看生辰與八字，自己判斷，再點選項揭曉。{e(best_txt)}。'
             + ('<span class="tag warn">答案來自第三方轉錄，主辦方未公布答案表</span>' if third else "")
             + f'</p><p class="meta">原題出處：<a href="{e(first["source_url"])}">{e(source_label(first["source_url"]))}</a></p>')
    score = (f'<div class="score" id="score" hidden data-best="{e(best_txt)}"></div>')
    cta = f'<a class="cta" href="{SHUNSHI}">用 ShunShi.ai 免費排八字、紫微、星盤，問 AI 怎麼看 →</a>'
    desc = (f"{year}年香港全球算命師大賽 {len(rows)} 道真題：真實生辰、八字四柱、大運與官方答案，"
            f"可線上作答對照職業命理師成績。")
    return page(title, desc, f"{BASE_URL}/{year}.html",
                intro + "".join(blocks) + score + cta, years, current=year)


def index_page(by_year, baseline, years):
    total = sum(len(v) for v in by_year.values())
    people = len({r["case_id"] for v in by_year.values() for r in v})
    accs = [b["best_raw_overall"]["accuracy"] for b in baseline.values() if b.get("best_raw_overall")]
    lo, hi = f"{int(min(accs) * 100)}%", f"{max(accs):.0%}"
    rows = []
    for y in years:
        qs = by_year[y]
        b = baseline.get(y, {}).get("best_raw_overall")
        best = f'{b["score"]}/{b["of"]}（{b["accuracy"]:.0%}）' if b else "未公布"
        prov = "第三方" if qs[0].get("answer_provenance") == "third-party" else "官方"
        rows.append(f'<tr><td><a href="{y}.html">{y}</a></td><td>第{edition_cn(qs[0]["edition"])}屆</td>'
                    f'<td class="n">{len(qs)}</td><td class="n">{len({r["case_id"] for r in qs})}</td>'
                    f'<td>{best}</td><td>{prov}</td></tr>')
    body = f"""
<h1>全球算命師大賽 歷屆真題（2010–{years[-1]}）</h1>
<p class="sub">香港青年術數家協會自 2010 年起舉辦的公開比賽：出題師傅提供真實人物的生辰與經歷，
職業命理師以真名參賽作答，賽後公布答案與成績。這裡把歷屆題目整理成可以直接作答的網頁 ——
先看生辰和八字，自己判斷，再點選項看對錯。</p>
<div class="stats">
<div class="stat"><b>{total}</b><span>道真題</span></div>
<div class="stat"><b>{people}</b><span>個真實命例</span></div>
<div class="stat"><b>{len(years)}</b><span>屆比賽</span></div>
<div class="stat"><b>{lo[:-1]}–{hi}</b><span>職業命理師最高正確率</span></div>
</div>
<h2>歷屆一覽</h2>
<table class="ed"><tr><th>年份</th><th>屆次</th><th class="n">題數</th><th class="n">命例</th><th>最高分（原始）</th><th>答案</th></tr>
{"".join(rows)}</table>
<h2>怎麼看這些分數</h2>
<p>隨機亂猜的正確率是 20–25%（依選項數）。有公布成績的屆次裡，冠軍級命理師的原始正確率落在 {lo} 到 {hi} 之間 ——
都明顯高於亂猜，也都遠遠稱不上「算準」。只公布了前幾名的分數，所以這是天花板，不是平均。
自第九屆起官方排名去掉每人最好與最差的一個命例，表中列的是 40 題的原始分，才能跟你自己的作答直接比。</p>
<h2>資料下載</h2>
<p>完整資料（題目、答案、生辰、八字與紫微盤、人類成績）在 <a href="{REPO}">GitHub</a>，
CC BY 4.0 授權，研究與教學可自由使用，請註明出處。</p>
<a class="cta" href="{SHUNSHI}">用 ShunShi.ai 免費排八字、紫微、星盤，問 AI 怎麼看 →</a>
"""
    desc = (f"香港全球算命師大賽 2010–{years[-1]} 歷屆 {total} 道真題，真實生辰配真實經歷，"
            f"附八字四柱、大運與官方答案，可線上作答。")
    return page(f"全球算命師大賽 歷屆真題與答案（{total} 題）", desc, f"{BASE_URL}/", body, years)


def build():
    qa = json.loads(QA.read_text(encoding="utf-8"))
    cases = {c["case_id"]: c for c in json.loads(CASES.read_text(encoding="utf-8"))}
    baseline = {x["year"]: x for x in json.loads(BASELINE.read_text(encoding="utf-8"))["editions"]}
    by_year = defaultdict(list)
    for r in qa:
        by_year[r["year"]].append(r)
    for y in by_year:
        by_year[y].sort(key=lambda r: (r["question_number"] or 0))
    years = sorted(by_year)
    files = {"index.html": index_page(by_year, baseline, years)}
    for y in years:
        files[f"{y}.html"] = year_page(y, by_year[y], cases, baseline.get(y), years)
    urls = [f"{BASE_URL}/"] + [f"{BASE_URL}/{y}.html" for y in years]
    files["sitemap.xml"] = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                            + "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    files[".nojekyll"] = ""
    return files, qa


def validate(files, qa):
    n_q = sum(f.count('class="q"') for k, f in files.items() if k.endswith(".html") and k != "index.html")
    bad = [r["id"] for r in qa if not r.get("answer")]
    print(f"{len(files)} 个文件 · 题目 {n_q}/{len(qa)} · 无答案 {len(bad)}")
    return n_q == len(qa) and not bad


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    files, qa = build()
    ok = validate(files, qa)
    if not args.check:
        OUT.mkdir(exist_ok=True)
        for name, text in files.items():
            (OUT / name).write_text(text, encoding="utf-8")
        print(f"→ {OUT.relative_to(ROOT)}/  ({len(files)} 个文件)")
    sys.exit(0 if ok else 1)
