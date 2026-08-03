#!/usr/bin/env python3
"""Normalize every usable HKJFMA edition into one schema.

Each edition was typeset by hand, in a different year, by a different person. Numbering runs
`1)` in one edition and `問題6:` in the next; options appear as `A)`, `A `, `A.`, `Ａ`, or `a)`;
some editions restart numbering per case and others run 1–40 straight through. A block regex per
edition proved brittle against that, so parsing is a **line-based state machine**: classify each
line as a case header, a question stem, an option, or prose, and assemble from there. Per-edition
differences shrink to a small config.

    python scripts/normalize.py            # writes data/hkjfma_qa.json
    python scripts/normalize.py --check    # validate only, no write
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "hkjfma"
VENDOR = ROOT / "data" / "vendor" / "minglibench"
OUT = ROOT / "data" / "hkjfma_qa.json"

SHICHEN = {"子": (23, 1), "丑": (1, 3), "寅": (3, 5), "卯": (5, 7),
           "辰": (7, 9), "巳": (9, 11), "午": (11, 13), "未": (13, 15),
           "申": (15, 17), "酉": (17, 19), "戌": (19, 21), "亥": (21, 23)}
EDITION = {2010: 1, 2011: 2, 2012: 3, 2013: 4, 2018: 9}

# 一行是题干：可选 問題/Q 前缀 + 号码 + 分隔符 + 实质内容
RE_Q = re.compile(r"^\s*(?:問題|问题|Q|第)?\s*(\d{1,2})\s*(?:題|条|條)?\s*[).、．:：]\s*(\S.*)$")
# 一行是选项：单个字母 + 分隔符或空格 + 内容
RE_OPT = re.compile(r"^\s*([A-Ea-e])\s*[).、．：:]?\s+?(\S.*)$")
RE_OPT_TIGHT = re.compile(r"^\s*([A-Ea-e])\s*[).、．：:]\s*(\S.*)$")
RE_BIRTH = re.compile(
    r"(西曆|西元|阳历|陽曆|公曆)?\s*出生|出生於|出生時間|出生日期|"
    r"[男女]命\s*[:：]|坤造|乾造|坤命|乾命")
RE_EN = re.compile(r"^\s*(?:Question\s+\d+|Male|Female|Which|What|How|In\s+which|"
                   r"\(|[A-Z][a-z]+[ ,])")


def norm(s: str) -> str:
    """NFKC — full-width Ａ and ｂ must compare equal to their ASCII forms."""
    return unicodedata.normalize("NFKC", s)


def body(path: Path) -> str:
    t = norm(path.read_text(encoding="utf-8")).split("\n\n", 1)[-1]
    return t.replace('entry-content">', "").strip()


def source_url(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# http"):
            return line[2:].strip()
    return ""


def parse_birth(raw: str) -> dict:
    t = norm(raw)
    out = {"raw": " ".join(raw.split())[:200], "calendar_type": "solar"}

    if m := re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", t):
        out.update(year=int(m.group(1)), month=int(m.group(2)), day=int(m.group(3)))
    elif m := re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", t):
        out.update(year=int(m.group(1)), month=int(m.group(2)), day=int(m.group(3)))
    elif m := re.search(r"\b(\d{1,2})-(\d{1,2})-(\d{4})\b", t):   # 2011: 西元02-11-1972
        out.update(year=int(m.group(3)), month=int(m.group(2)), day=int(m.group(1)))
    elif m := re.search(r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
                        r"[a-z]*\s+(\d{4})", t):
        mo = "JanFebMarAprMayJunJulAugSepOctNovDec".index(m.group(2)) // 3 + 1
        out.update(year=int(m.group(3)), month=mo, day=int(m.group(1)))

    if s := re.search(r"([子丑寅卯辰巳午未申酉戌亥])\s*時", t):
        out["shichen"] = s.group(1)
        out["hour_start"], out["hour_end"] = SHICHEN[s.group(1)]
    if hm := re.search(r"(\d{1,2})\s*[:：]\s*(\d{2})", t):
        out["clock_hour"], out["clock_minute"] = int(hm.group(1)), int(hm.group(2))

    if re.search(r"女命|坤造|坤命|Female|\(女\)", t, re.I):
        out["gender"] = "女"
    elif re.search(r"男命|乾造|乾命|Male|\(男\)", t, re.I):
        out["gender"] = "男"

    for place in ("香港", "澳門", "台灣", "馬來西亞", "新加坡", "美國", "澳洲", "加拿大",
                  "英國", "日本", "韓國", "中國大陸", "唐山", "廣東", "上海", "北京",
                  "國內", "中國", "Hong Kong", "Malaysia", "Taiwan", "Singapore"):
        if place in t:
            out["location"] = place
            break

    # 出题师傅自己算好的四柱 —— 独立的人工排盘参照
    P = r"[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]"
    if p := re.search(rf"({P}年\s*{P}月\s*{P}日(?:\s*{P}時)?)", t):
        out["pillars_stated_by_master"] = " ".join(p.group(1).split())
    if lu := re.search(r"農曆|农历|(?:陰曆)([^\n,，。]{0,24})", t):
        if lu.lastindex:
            out["lunar_note"] = lu.group(1).strip()
    return out


def split_bilingual(s: str):
    """2013/2018 print `中文 (English)`. Split on a trailing paren holding real words."""
    s = s.strip()
    m = re.search(r"\(([^()]*[A-Za-z]{3}[^()]*)\)\s*$", s)
    if m and len(m.group(1)) > 6:
        return s[:m.start()].strip(), m.group(1).strip()
    return s, None


def scan(text, url, year, *, master_pat=None, method_pat=None, case_pat=None,
         answers=None, per_case_numbering=False):
    """Walk the lines once, emitting one record per question."""
    lines = [l.rstrip() for l in text.split("\n")]
    rows, case_i, birth = [], 0, {}
    master = method = None
    cur = None                              # 正在收集的题
    seen_first_q = False

    def flush():
        nonlocal cur
        if cur and len(cur["options"]) >= 2:
            qn = cur["n"]
            key = (case_i, qn) if per_case_numbering else qn
            q_zh, q_en = split_bilingual(cur["q"])
            rows.append({
                "id": f"hkjfma_{year}_{len(rows) + 1:02d}",
                "source": "hkjfma",
                "edition": EDITION.get(year),
                "year": year,
                "case_id": f"hkjfma_{year}_c{case_i or 1}",
                "case_index": case_i or 1,
                "question_number": qn,
                "birth_info": birth,
                "question": q_zh,
                "question_en": q_en,
                "options": cur["options"],
                "num_options": len(cur["options"]),
                "answer": (answers or {}).get(key),
                "master": master,
                "method": method,
                "source_url": url,
            })
        cur = None

    i = 0
    while i < len(lines):
        ln = lines[i]
        if not ln:
            i += 1
            continue

        # ── 命例头：新的生辰行 ──
        if (case_pat and case_pat.search(ln)) or (RE_BIRTH.search(ln) and len(ln) < 120):
            ctx = "\n".join(lines[i:i + 6])
            b = parse_birth(ctx)
            if b.get("year"):
                flush()
                case_i += 1
                birth = b
                seen_first_q = False
                blob = "\n".join(lines[max(0, i - 4):i + 8])
                if master_pat and (m := master_pat.search(blob)):
                    master = m.group(1).strip(" ：:，,。.")
                if method_pat and (m := method_pat.search(blob)):
                    method = m.group(0)
                i += 1
                continue

        # ── 选项 ──
        if cur is not None:
            m = RE_OPT.match(ln) or RE_OPT_TIGHT.match(ln)
            if m:
                letter, txt = m.group(1).upper(), m.group(2).strip()
                # 与已有字母连续才算（挡掉 "A trip to..." 这类英文散文）
                n_opt = len(cur["options"])
                if n_opt < 5 and letter == "ABCDE"[n_opt]:
                    zh, en = split_bilingual(txt)
                    o = {"letter": letter, "text": zh}
                    if en:
                        o["text_en"] = en
                    cur["options"].append(o)
                    i += 1
                    continue
            # 选项的续行（英文对照另起一行）
            if cur["options"] and RE_EN.match(ln) and not RE_Q.match(ln):
                last = cur["options"][-1]
                last["text_en"] = (last.get("text_en", "") + " " + ln.strip("() ")).strip()
                i += 1
                continue

        # ── 题干 ──
        if m := RE_Q.match(ln):
            n, stem = int(m.group(1)), m.group(2).strip()
            plausible = (1 <= n <= 60) and len(stem) >= 4 and not stem[0].isdigit()
            if plausible:
                flush()
                cur = {"n": n, "q": stem, "options": []}
                seen_first_q = True
                i += 1
                continue

        # 题干的英文对照行
        if cur is not None and not cur["options"] and RE_EN.match(ln):
            cur["q"] += f" ({ln.strip('() ')})"
        i += 1

    flush()
    return rows


# ── answer keys ───────────────────────────────────────────────────────────────

def answers_2010(t):
    CN = "一二三四五六七八九十"
    out = {}
    for cn, seq in re.findall(r"第([一二三四五六七八九十])條\s*[:：]\s*"
                              r"((?:\s*\d+\s*[a-eA-E]\s*[,，]?)+)", t):
        for qn, L in re.findall(r"(\d+)\s*([a-eA-E])", seq):
            out[(CN.index(cn) + 1, int(qn))] = L.upper()
    return out


def answers_2011(t):
    tail = t[t.rfind("下載:"):] if "下載:" in t else t[len(t) // 2:]
    return {int(q): L.upper()
            for q, L in re.findall(r"(\d{1,2})\s*[).、．]\s*([a-eA-E])(?!\w)", tail)}


def answers_2012(t):
    return {int(q): L.upper() for q, L in re.findall(r"^\s*(\d{1,2})\s+([A-D])\s*$",
                                                     t, re.M)}


def answers_2013(t):
    if "答案公報" not in t:
        return {}
    return {int(q): L for q, L in re.findall(r"(\d{1,2})\s*([A-D])\b",
                                            t[t.index("答案公報"):])}


def answers_2018(path):
    return {int(q): L for q, L in
            re.findall(r"\b(\d{1,2})\s+([A-D])\b", norm(path.read_text(encoding="utf-8")))}


def read_minglibench():
    p = VENDOR / "data.json"
    if not p.exists():
        return []
    items = list(json.loads(p.read_text(encoding="utf-8")).values())[0]
    out = []
    for q in items:
        b = dict(q.get("birth_info") or {})
        b.setdefault("calendar_type", "solar")
        opts = [{"letter": o["letter"], "text": o["text"]} for o in q["options"]]
        out.append({
            "id": f"mlb_{q['id']}", "source": "minglibench",
            "edition": None, "year": None,
            "case_id": f"mlb_{q['case_id']}", "case_index": None,
            "question_number": q.get("question_number"),
            "birth_info": b, "question": q["question"], "question_en": None,
            "options": opts, "num_options": len(opts), "answer": q.get("answer"),
            "master": None, "method": None, "category": q.get("category"),
            "source_url": "https://github.com/DestinyLinker/MingLi-Bench",
        })
    return out


# ── driver ────────────────────────────────────────────────────────────────────

CFG = {
    2010: dict(master_pat=re.compile(r"由(.{2,14}?)提供"),
               case_pat=re.compile(r"第[一二三四五六七八九十]條題目"),
               per_case_numbering=True, ans=answers_2010),
    2011: dict(case_pat=re.compile(r"題目\([一二三四五六七八九十]\)"), ans=answers_2011),
    2012: dict(master_pat=re.compile(r"出題者\s*[:：]\s*(\S+)"),
               case_pat=re.compile(r"第[一二三四五六七八九十]條命例題目"), ans=answers_2012),
    2013: dict(master_pat=re.compile(r"問題提供\s*[:：]\s*(\S+)"), ans=answers_2013),
    2018: dict(master_pat=re.compile(r"命例問題提供\s*[:：]\s*(.+)"),
               method_pat=re.compile(r"子平八字|紫微斗數|奇門遁甲|鐵板神數|六壬"),
               ans=None),
}


def collect():
    rows = []
    for year, cfg in CFG.items():
        g = sorted(RAW.glob(f"{year}_questions_*.txt"), key=lambda p: -p.stat().st_size)
        if not g:
            continue
        path = g[0]
        t = body(path)
        if year == 2018:
            ak = RAW / "2018_answer_key.txt"
            ans = answers_2018(ak) if ak.exists() else {}
        else:
            ans = cfg["ans"](t)
        rows += scan(t, source_url(path), year,
                     master_pat=cfg.get("master_pat"), method_pat=cfg.get("method_pat"),
                     case_pat=cfg.get("case_pat"), answers=ans,
                     per_case_numbering=cfg.get("per_case_numbering", False))
    rows += read_minglibench()
    return rows


def report(rows):
    by = Counter(r["year"] or "minglibench" for r in rows)
    print(f"{'edition':<13}{'items':>7}{'answered':>10}{'opts':>9}{'cases':>7}{'bilingual':>11}")
    print("-" * 57)
    for k in sorted(by, key=lambda x: (x == "minglibench", str(x))):
        s = [r for r in rows if (r["year"] or "minglibench") == k]
        print(f"{str(k):<13}{len(s):>7}{sum(1 for r in s if r['answer']):>10}"
              f"{str(sorted({r['num_options'] for r in s})):>9}"
              f"{len({r['case_id'] for r in s}):>7}"
              f"{sum(1 for r in s if r.get('question_en')):>11}")
    print("-" * 57)
    print(f"{'TOTAL':<13}{len(rows):>7}{sum(1 for r in rows if r['answer']):>10}")

    ok = True
    for label, bad in (
        ("无答案", [r["id"] for r in rows if not r["answer"]]),
        ("选项<4", [r["id"] for r in rows if r["num_options"] < 4]),
        ("生辰缺年", [r["id"] for r in rows if not r["birth_info"].get("year")]),
        ("题干过短", [r["id"] for r in rows if len(r["question"]) < 6]),
    ):
        if bad:
            ok = False
            print(f"⚠ {label} {len(bad)} 条: {bad[:10]}{' …' if len(bad) > 10 else ''}")
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    rows = collect()
    ok = report(rows)
    if not args.check:
        OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n→ {OUT.relative_to(ROOT)}  ({len(rows)} 条)")
    sys.exit(0 if ok else 1)
