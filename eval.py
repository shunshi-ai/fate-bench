#!/usr/bin/env python3
"""Score a model on fate-bench, against the human baseline rather than against other models.

This repository does not keep a leaderboard. Leaderboards go stale within weeks and say nothing
about the thing that is actually interesting here: these questions were answered by practising
fortune tellers, in public, under their own names, for a trophy — and the organizer published what
they scored. So the comparison worth printing is model vs. those people, not model vs. model.

Any OpenAI-compatible endpoint works; there is no model registry to maintain.

    export FB_API_KEY=sk-...
    python eval.py --base-url https://api.deepseek.com --model deepseek-chat

    --limit N       stop after N questions (smoke test)
    --year 2024     restrict to one edition, so the human baseline is exactly comparable
    --no-charts     withhold the precomputed BaZi/Zi Wei charts
    --out FILE      write per-question results as JSONL

By default the precomputed charts are included in the prompt. That is deliberate: without them a
score mostly measures whether the model can convert a date into a sexagenary chart, which is
arithmetic a library already does. With them, the score is about reading the chart.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "fate_bench.jsonl"
BASELINE = ROOT / "data" / "human_baseline.json"

PROMPT = """你是一位資深命理師。以下是一位真實人物的生辰與命盤，請根據命理推斷回答問題。

{birth}
{charts}
問題：{question}
{options}

請先簡要推理，最後單獨一行輸出「答案：X」，X 為選項字母。"""


def render(row, with_charts=True):
    b = row["birth_info"]
    birth = "生辰：" + " ".join(filter(None, [
        f"{b['year']}年{b['month']}月{b['day']}日" if b.get("year") else None,
        f"{b.get('shichen', '')}時" if b.get("shichen") else None,
        b.get("gender"), b.get("location"),
    ])) if b.get("year") else "生辰：源站未公布"

    charts = ""
    if with_charts and (c := row.get("charts")):
        p = c["bazi"]["pillars"]
        charts = (f"八字：{p['year']} {p['month']} {p['day']} {p['hour']}"
                  f"（日主 {c['bazi']['day_master']}）\n")
        if z := c.get("ziwei"):
            # py-iztro 的宫名多数不带「宫」字，唯独「命宫」自带 —— 不剥就成了「命宫宮」
            palaces = "、".join(
                f"{x['name'].rstrip('宫宮')}宮[{x['branch']}]"
                f"{''.join(s['name'] for s in x['major_stars']) or '空'}"
                for x in z["palaces"])
            charts += f"紫微（{z['five_elements_class']}，命主{z['soul']}）：{palaces}\n"

    opts = "\n".join(f"{o['letter']}. {o['text']}" for o in row["options"])
    return PROMPT.format(birth=birth, charts=charts, question=row["question"], options=opts)


def ask(row, args, key):
    body = json.dumps({
        "model": args.model,
        "messages": [{"role": "user", "content": render(row, not args.no_charts)}],
        "temperature": 0,
        "max_tokens": args.max_tokens,
    }).encode()
    req = urllib.request.Request(
        args.base_url.rstrip("/") + "/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=args.timeout) as r:
                text = json.load(r)["choices"][0]["message"]["content"]
            return text, parse_letter(text, row["num_options"])
        except Exception as e:                      # noqa: BLE001 — 网络/限流都只是重试
            if attempt == 2:
                return f"<error: {e}>", None
    return None, None


def parse_letter(text, n):
    """Take the last letter the model committed to — models often restate options while reasoning."""
    valid = "ABCDE"[:n]
    if m := re.findall(rf"答案\s*[:：]?\s*([{valid}])", text):
        return m[-1]
    if m := re.findall(rf"(?:^|\n)\s*\(?([{valid}])[\.、\)]", text):
        return m[-1]
    if m := re.findall(rf"\b([{valid}])\b", text):
        return m[-1]
    return None


def human_reference(rows):
    """Best published human score over exactly the editions being scored.

    An edition only counts if every one of its questions was scored. A human total is a score over
    the whole paper; setting it against a model that answered a third of that paper compares two
    different things — with `--limit` that is easy to do by accident.
    """
    editions = {e["year"]: e for e in json.loads(BASELINE.read_text(encoding="utf-8"))["editions"]}
    scored = Counter(r["year"] for r in rows)
    full = [e for y, n in scored.items()
            if (e := editions.get(y)) and e.get("results") and e["items"] == n]
    if not full:
        return None
    items = sum(e["items"] for e in full)
    best = sum((e.get("best_raw_overall") or e["results"][0])["score"] for e in full)
    return {"score": best, "of": items, "accuracy": best / items,
            "years": sorted(e["year"] for e in full),
            "skipped": sorted(set(scored) - {e["year"] for e in full})}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=os.environ.get("FB_BASE_URL", "https://api.deepseek.com"))
    ap.add_argument("--model", default="deepseek-chat")
    ap.add_argument("--api-key", default=os.environ.get("FB_API_KEY"))
    ap.add_argument("--limit", type=int)
    ap.add_argument("--year", type=int)
    ap.add_argument("--no-charts", action="store_true")
    ap.add_argument("--include-unanswerable", action="store_true",
                    help="也算上生辰缺失的题（默认排除，见下方说明）")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--out")
    args = ap.parse_args()

    if not args.api_key:
        sys.exit("需要 --api-key 或环境变量 FB_API_KEY")

    rows = [json.loads(l) for l in DATA.read_text(encoding="utf-8").splitlines()]

    # 五道题的生辰主办方只印在卷子上、没登到网页，所以我们手里没有。比赛当天选手是看得到的
    # —— 拿这几题扣模型的分，等于用一份比选手更少的资料去比选手的成绩。默认剔除。
    unanswerable = [r for r in rows if r["birth_info"].get("missing")]
    if unanswerable and not args.include_unanswerable:
        rows = [r for r in rows if not r["birth_info"].get("missing")]

    if args.year:
        rows = [r for r in rows if r["year"] == args.year]
    if args.limit:
        rows = rows[:args.limit]
    if not rows:
        sys.exit("没有符合条件的题目")

    print(f"{args.model} · {len(rows)} 题 · 命盘{'不给' if args.no_charts else '给'}", flush=True)
    with ThreadPoolExecutor(args.workers) as pool:
        results = list(pool.map(lambda r: ask(r, args, args.api_key), rows))

    correct = [r for r, (_, g) in zip(rows, results) if g == r["answer"]]
    unparsed = [r["id"] for r, (_, g) in zip(rows, results) if g is None]
    acc = len(correct) / len(rows)
    chance = sum(1 / r["num_options"] for r in rows) / len(rows)

    print(f"\n  {args.model:<22} {acc:>6.1%}   ({len(correct)}/{len(rows)})")
    if h := human_reference(rows):
        yrs = "、".join(str(y) for y in h["years"])
        print(f"  {'人类最好成绩':<20} {h['accuracy']:>6.1%}   ({h['score']}/{h['of']})  {yrs} 届")
    else:
        print(f"  {'人类最好成绩':<20}      —    没有整届跑完，无可比的人类分数")
    print(f"  {'随机猜':<21} {chance:>6.1%}")

    if h and h["skipped"]:
        editions = {e["year"]: e for e in json.loads(BASELINE.read_text(encoding="utf-8"))["editions"]}
        why = []
        for y in h["skipped"]:
            e = editions.get(y, {})
            why.append(f"{y}（{'该届未公布成绩' if not e.get('results') else '本次未整届跑完'}）")
        print(f"\n  不计入人类对比：{'、'.join(why)}")
    if unanswerable and not args.include_unanswerable:
        print(f"  已剔除 {len(unanswerable)} 题：主办方只把生辰印在卷子上、没登到网页，"
              f"我们手里没有，而比赛当天选手看得到（--include-unanswerable 可保留）")
    if unparsed:
        print(f"\n  ⚠ {len(unparsed)} 题未能从回答中解析出选项: {unparsed[:5]}")

    by_cat = defaultdict(lambda: [0, 0])
    for r, (_, g) in zip(rows, results):
        if c := r.get("category"):
            by_cat[c][0] += g == r["answer"]
            by_cat[c][1] += 1
    if len(by_cat) > 1:
        print("\n  按题型（分类是近似的，见 README）")
        for c, (k, n) in sorted(by_cat.items(), key=lambda kv: -kv[1][0] / kv[1][1]):
            print(f"    {c:<6} {k / n:>6.1%}  ({k}/{n})")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            for r, (text, g) in zip(rows, results):
                f.write(json.dumps({"id": r["id"], "year": r["year"],
                                    "category": r.get("category"), "gold": r["answer"],
                                    "guess": g, "correct": g == r["answer"],
                                    "raw": text}, ensure_ascii=False) + "\n")
        print(f"\n→ {args.out}")
