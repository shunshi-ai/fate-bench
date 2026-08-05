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
LABELS = ROOT / "data" / "hkjfma_categories.json"

SHICHEN = {"子": (23, 1), "丑": (1, 3), "寅": (3, 5), "卯": (5, 7),
           "辰": (7, 9), "巳": (9, 11), "午": (11, 13), "未": (13, 15),
           "申": (15, 17), "酉": (17, 19), "戌": (19, 21), "亥": (21, 23)}
EDITION = {2010: 1, 2011: 2, 2012: 3, 2013: 4, 2018: 9, 2021: 12}

# 各届的分隔符各写各的：`1)` `問題1,` `問題6 ,` `11 最好的…`、选项 `A)` `A ` `A,` `A2004甲申`
SEP = r"[).、．。:：,，]"
# 一行是题干。分两种版式：
#  · 带 `問題`/`Q`/`第` 前缀 —— 前缀已经足够标明是题干，号码后允许直接接内容
#    （2021 有 `Q7命主已经离婚，第二婚是哪一年？`、`Q24這位1970年出生的游先生…`）
#  · 不带前缀 —— 必须有分隔符或空格，否则选项里的 `1992壬申年,有何特別事情發生?`
#    会被读成第 1992 题
RE_Q_PREFIXED = re.compile(rf"^\s*(?:問題|问题|Q|第)\s*(\d{{1,2}})\s*(?:題|条|條)?"
                           rf"\s*{SEP}?\s*(\S.*)$")
RE_Q_BARE = re.compile(rf"^\s*(\d{{1,2}})\s*(?:題|条|條)?\s*(?:\s*{SEP}\s*|\s+)(\S.*)$")


def match_q(line: str):
    return RE_Q_PREFIXED.match(line) or RE_Q_BARE.match(line)
# 一行是选项。第三个分支放行 `A2004甲申` / `A$9000` —— 字母后直接接非字母内容；
# 用「后面不是字母」挡住 `Between …` 被读成选项 B 这类英文散文。
RE_OPT = re.compile(rf"^\s*([A-Ea-e])(?:\s*{SEP}\s*|\s+|(?=[^A-Za-z\s]))(\S.*)$")
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
    # raw 只留生辰段：窗口尾巴常跨进第一道题，留着会把题干选项混进 provenance 字段
    head = []
    for l in raw.split("\n"):
        if match_q(l) or RE_OPT.match(l):
            break
        head.append(l)
    out = {"raw": " ".join(" ".join(head).split())[:200], "calendar_type": "solar"}

    if m := re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", t):
        out.update(year=int(m.group(1)), month=int(m.group(2)), day=int(m.group(3)))
    elif m := re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", t):
        out.update(year=int(m.group(1)), month=int(m.group(2)), day=int(m.group(3)))
    # 边界用 (?<!\d)/(?!\d) 而不是 \b —— CJK 也算 word 字符，`西元02-…` 的 元|0 之间没有 \b
    elif m := re.search(r"(?<!\d)(\d{1,2})-(\d{1,2})-(\d{4})(?!\d)", t):  # 2011: 西元02-11-1972
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
    # 2021 第二例写作「9時 58分 早上」—— 数字接「時」，与地支时辰（卯時/申時）不会撞
    elif hm := re.search(r"(?<!\d)(\d{1,2})\s*時\s*(\d{1,2})\s*分", t):
        out["clock_hour"], out["clock_minute"] = int(hm.group(1)), int(hm.group(2))
    if "shichen" not in out and "clock_hour" in out:   # 2013 第三例只登了 00:30AM
        h = out["clock_hour"]
        out["shichen"] = next(z for z, (a, b_) in SHICHEN.items()
                              if (a <= h < b_) or (a > b_ and (h >= a or h < b_)))
        out["hour_start"], out["hour_end"] = SHICHEN[out["shichen"]]
        out["shichen_derived_from_clock"] = True

    # 2021 第一、五例把性别写成「1，男性」「男性：台灣出生」，不带「命/造」
    if re.search(r"女命|坤造|坤命|女性|Female|\(女\)|性別\s*[:：]\s*女", t, re.I):
        out["gender"] = "女"
    elif re.search(r"男命|乾造|乾命|男性|Male|\(男\)|性別\s*[:：]\s*男", t, re.I):
        out["gender"] = "男"

    # 出生地优先取紧挨着「出生/出世」的那个地名。命例头里往往还有出题师傅的所在地
    # （`命例提供: 香港 紫微斗數 樂只君老師`），按列表顺序硬取会把它当成命主出生地 ——
    # 2021 第一例「命主於大陸出生」、第八例「廣東潮汕地區出世(少時隨家人移居香港)」都会读错。
    PLACES = ("香港", "澳門", "台灣", "馬來西亞", "新加坡", "美國", "澳洲", "加拿大",
              "英國", "日本", "韓國", "中國大陸", "大陸", "唐山", "廣東潮汕", "廣東",
              "上海", "北京", "國內", "中國", "Hong Kong", "Malaysia", "Taiwan", "Singapore")
    alt = "|".join(PLACES)                       # 长的排前面：廣東潮汕 要先于 廣東
    if m := re.search(rf"({alt})\s*(?:地區)?\s*(?:出生|出世)", t):
        out["location"] = m.group(1)
    elif hits := [(t.index(p), p) for p in PLACES if p in t]:
        out["location"] = min(hits)[1]

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


# 「子平八字」排在「八字」前面 —— 交替按序匹配，反过来会把子平八字截成八字
METHODS = "子平八字|紫微斗數|奇門遁甲|鐵板神數|六壬|八字"
# 2018 把地区和术数写在名字前：`命例問題提供 : 香港 紫微斗數 天盤計算 樂只君師傅`
# 2021 第七例还把往届名次写了进去：`馬來西亞 己亥亞軍,庚子冠軍 紫微斗數 張翊萱老師`
RE_PREFIX = re.compile(rf"^(?:香港青術會代表|香港|台灣|馬來西亞|新加坡|中國|澳門|"
                       rf"{METHODS}|天盤計算|"
                       rf"[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥](?:冠|亞|季)軍[,，]?)\s*")


def strip_provider_prefix(v: str) -> str:
    while (nv := RE_PREFIX.sub("", v)) != v:
        v = nv
    return v.strip()


def read_provider(lines, i, master_pat, method_pat):
    """Read the contributing master (and, for 2018, the divination system) near line i."""
    if not (master_pat or method_pat):
        return None
    master = method = None
    for j in range(max(0, i - 4), min(len(lines), i + 9)):
        if master is None and master_pat and (m := master_pat.search(lines[j])):
            # 允许 master_pat 用分支写多种版式（2021 有一位师傅的署名不带「命例提供:」前缀）
            v = next((g for g in m.groups() if g), "")
            # `問題提供:著名玄學術數師傅:` —— 冒号收尾说明这行只是头衔，名字在下一行
            if v.rstrip().endswith((":", "：")) or not v.strip():
                v = next((lines[k] for k in range(j + 1, min(j + 3, len(lines)))
                          if lines[k].strip()), v)
            master = strip_provider_prefix(v.strip(" ：:，,。.")) or None
        if method is None and method_pat and (m := method_pat.search(lines[j])):
            method = m.group(0)
    return (master, method) if (master or method) else None


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
                "birth_info": birth or {
                    "missing": True,
                    "reason": "the source page publishes this case's questions but not its "
                              "birth data",
                },
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

        # ── 硬边界：出题师傅那一行（`命例問題提供 : …` / `第三條命例 …` / `問題提供:…`）──
        # 必开新命例，即便附近找不到生辰。2018 的陳開通一例正是这种情况：源站只登了
        # 题目没登生辰，若不硬切，Q21-25 会静默继承上一例（马来西亚 1960 男）的盘。
        if case_pat and case_pat.search(ln):
            # 只向前看：向后看会把上一命例选项里的年份读成本例生辰
            b = parse_birth("\n".join(lines[i:i + 8]))
            if seen_first_q or case_i == 0:
                flush()
                case_i += 1
                birth = b if b.get("year") else {}
                seen_first_q = False
            elif b.get("year") and not birth.get("year"):
                birth = b                      # 紧跟在生辰行后的师傅行：补齐，不另开命例
            master, method = read_provider(lines, i, master_pat, method_pat) or (master, method)
            i += 1
            continue

        # ── 软边界：新的生辰行 ──
        # 一个命例的生辰常连着写好几行（`西曆出生於…` / `出生地點…` 各匹配一次），
        # 所以要等本命例至少出过一道题，才允许开下一个命例。
        if RE_BIRTH.search(ln) and len(ln) < 120 and (seen_first_q or case_i == 0):
            b = parse_birth("\n".join(lines[i:i + 6]))
            # 性别常写在生辰行之上（`題目(一)` / `男命` / `出生時間:…`）。只回看取性别，
            # 不回看取日期 —— 上一命例的选项里满是年份，会把生辰读串。
            if b.get("year") and not b.get("gender"):
                if g := parse_birth("\n".join(lines[max(0, i - 4):i])).get("gender"):
                    b["gender"] = g
            if b.get("year"):
                flush()
                case_i += 1
                birth = b
                seen_first_q = False
                if mm := read_provider(lines, i, master_pat, method_pat):
                    master, method = mm
                i += 1
                continue

        # ── 选项 ──
        if cur is not None:
            if m := RE_OPT.match(ln):
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
            if cur["options"] and RE_EN.match(ln) and not match_q(ln):
                last = cur["options"][-1]
                last["text_en"] = (last.get("text_en", "") + " " + ln.strip("() ")).strip()
                i += 1
                continue

        # ── 题干 ──
        if m := match_q(ln):
            n, stem = int(m.group(1)), m.group(2).strip()
            # 不再要求题干非数字开头 —— 半数真题就长成 `1)1992壬申年,有何特別事情發生?`。
            # 误命中（如 2013 的「一生描述」编号列表）由「必须收到 ≥2 个选项」在 flush 里滤掉。
            if 1 <= n <= 60 and len(stem) >= 4:
                flush()
                # 2013 第 16 题写成 `問題16: Question 16:` —— 号码那行只有英文标签，
                # 真正的题干在下一行。不接住就会把 "Question 16:" 当成题干存下来。
                if re.fullmatch(r"(?:Question|Q)\s*\d+\s*[:：]?", stem, re.I):
                    stem = next((l.strip() for l in lines[i + 1:i + 3] if l.strip()), stem)
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


def answers_grid(path):
    """转录的答案表：`1 B   2 C   3 B …`。注释行先剔掉 —— 那里的说明文字可能
    偶然长得像「号码 + 字母」，混进来就是静默错答案。"""
    t = "\n".join(l for l in norm(path.read_text(encoding="utf-8")).splitlines()
                  if not l.lstrip().startswith("#"))
    return {int(q): L for q, L in re.findall(r"\b(\d{1,2})\s+([A-D])\b", t)}


# MingLi-Bench 把 2022–2025 四届的题号连编成 1–160，每届 40 题。分界经两条独立证据确认：
# 一是他们 raw/ 下按年份分开的原文，二是 2022/2023/2024 三届的一手答案表逐题对上
# （scripts/crosscheck_vendor.py）。
MLB_YEARS = [(range(1, 41), 2022, 13), (range(41, 81), 2023, 14),
             (range(81, 121), 2024, 15), (range(121, 161), 2025, 16)]


def read_minglibench():
    p = VENDOR / "data.json"
    if not p.exists():
        return []
    items = list(json.loads(p.read_text(encoding="utf-8")).values())[0]
    out = []
    for q in items:
        year, edition = next(((y, e) for span, y, e in MLB_YEARS
                              if q["question_number"] in span), (None, None))
        b = dict(q.get("birth_info") or {})
        b.setdefault("calendar_type", "solar")
        opts = [{"letter": o["letter"], "text": o["text"]} for o in q["options"]]
        out.append({
            "id": f"mlb_{q['id']}", "source": "minglibench",
            "edition": edition, "year": year,
            "case_id": f"mlb_{q['case_id']}", "case_index": None,
            "question_number": q.get("question_number"),
            "birth_info": b, "question": q["question"], "question_en": None,
            "options": opts, "num_options": len(opts), "answer": q.get("answer"),
            "master": None, "method": None, "category": q.get("category"),
            "category_source": "minglibench" if q.get("category") else None,
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
               case_pat=re.compile(r"第[一二三四五六七八九十]條命例"), ans=answers_2012),
    2013: dict(master_pat=re.compile(r"問題提供\s*[:：]\s*(.*)"),
               case_pat=re.compile(r"問題提供"), ans=answers_2013),
    2018: dict(master_pat=re.compile(r"命例問題提供\s*[:：]\s*(.+)"),
               case_pat=re.compile(r"命例問題提供"),
               method_pat=re.compile(METHODS), ans=None,
               key_file="2018_answer_key.txt"),
    # 2021 的命例头三种版式混用：`命例提供:`、`命例問題提供:`，以及最后一位师傅直接署名
    # `陳俊燊師傅 (子平八字)` 后面挂两个命例。第二个命例只有一行 `坤造:`，靠软边界开出来。
    2021: dict(master_pat=re.compile(r"命例(?:問題)?提供\s*[:：]\s*(.+)"
                                     r"|^(\S{2,8}師傅)\s*\((?:子平八字|紫微斗數)\)"),
               case_pat=re.compile(r"命例(?:問題)?提供\s*[:：]"),
               method_pat=re.compile(METHODS), ans=None,
               key_file="2021_answers_thirdparty.txt"),
}


# 答案的成色不是一回事，不该混在一个 `answer` 字段里假装等价。
# `official` = 主办方自己公布过正确答案（登在题目页上，或另发答案表由本仓库转录存图）。
# `third-party` = 主办方从未公布这一届的答案，答案来自第三方转录，出处未经主办方确认。
# 两种都留着，但打上标记 —— 想只用官方答案的人可以按这个字段过滤。
PROVENANCE = {
    2010: ("official", "printed on the organiser's own question page"),
    2011: ("official", "printed on the organiser's own question page"),
    2012: ("official", "printed on the organiser's own question page"),
    2013: ("official", "printed on the organiser's own question page"),
    2018: ("official", "transcribed from the organiser's answer sheet, archived here as "
                       "images/2018_answers_058.jpg"),
    2022: ("official", "transcribed from the organiser's answer sheet; MingLi-Bench's copy of "
                       "this edition audited against it 40/40"),
    2023: ("official", "transcribed from the organiser's answer sheet; MingLi-Bench's copy of "
                       "this edition audited against it 40/40"),
    2024: ("official", "transcribed from the organiser's answer sheet; MingLi-Bench's copy of "
                       "this edition audited against it 40/40"),
    2021: ("third-party", "the organiser never published a key for this edition — the paper was "
                          "auto-scored through an online form. Answers taken from BaziQA (MIT), "
                          "whose 2022/2023/2024 answers match the official sheets 120/120"),
    2025: ("third-party", "the organiser never published a key for this edition. Answers come "
                          "from MingLi-Bench and are independently corroborated by BaziQA, which "
                          "transcribed the same paper separately — the two agree 40/40"),
}


def collect():
    rows = []
    for year, cfg in CFG.items():
        g = sorted(RAW.glob(f"{year}_questions_*.txt"), key=lambda p: -p.stat().st_size)
        if not g:
            continue
        path = g[0]
        t = body(path)
        if kf := cfg.get("key_file"):
            ak = RAW / kf
            ans = answers_grid(ak) if ak.exists() else {}
        else:
            ans = cfg["ans"](t)
        got = scan(t, source_url(path), year,
                   master_pat=cfg.get("master_pat"), method_pat=cfg.get("method_pat"),
                   case_pat=cfg.get("case_pat"), answers=ans,
                   per_case_numbering=cfg.get("per_case_numbering", False))
        rows += dedupe(got, year)
    rows += read_minglibench()
    for r in rows:
        tier, note = PROVENANCE.get(r["year"], (None, None))
        r["answer_provenance"], r["answer_provenance_note"] = tier, note
    return apply_categories(rows)


def apply_categories(rows):
    """Merge the topic labels produced by scripts/categorize.py.

    They live in their own file rather than being written straight into the question bank —
    otherwise re-running this script would silently wipe them.
    """
    if not LABELS.exists():
        return rows
    labels = json.loads(LABELS.read_text(encoding="utf-8"))["labels"]
    for r in rows:
        if lab := labels.get(r["id"]):
            r["category"], r["category_source"] = lab["category"], lab["source"]
    return rows


def dedupe(got, year):
    """Several pages print the whole paper twice — 2010 repeats it under 「以下紅色者為答案」,
    2013 repeats question 16. Keep the first copy and renumber ids."""
    seen, out = set(), []
    for r in got:
        k = (r["question_number"], r["question"][:40])
        if k in seen:
            continue
        seen.add(k)
        r["id"] = f"hkjfma_{year}_{len(out) + 1:02d}"
        out.append(r)
    return out


def report(rows):
    by = Counter((r["year"], r["source"]) for r in rows)
    print(f"{'year':<7}{'source':<13}{'items':>7}{'answered':>10}{'opts':>9}"
          f"{'cases':>7}{'bilingual':>11}{'category':>10}")
    print("-" * 74)
    for year, src in sorted(by, key=lambda k: (k[0] or 0, k[1])):
        s = [r for r in rows if (r["year"], r["source"]) == (year, src)]
        print(f"{str(year):<7}{src:<13}{len(s):>7}{sum(1 for r in s if r['answer']):>10}"
              f"{str(sorted({r['num_options'] for r in s})):>9}"
              f"{len({r['case_id'] for r in s}):>7}"
              f"{sum(1 for r in s if r.get('question_en')):>11}"
              f"{sum(1 for r in s if r.get('category')):>10}")
    print("-" * 74)
    print(f"{'TOTAL':<20}{len(rows):>7}{sum(1 for r in rows if r['answer']):>10}"
          f"{'':>9}{len({r['case_id'] for r in rows}):>7}"
          f"{sum(1 for r in rows if r.get('question_en')):>11}"
          f"{sum(1 for r in rows if r.get('category')):>10}")

    # 人类基线是手工转录的，题量必须跟解析结果对得上 —— 对不上说明有一边错了
    baseline = json.loads((ROOT / "data" / "human_baseline.json").read_text(encoding="utf-8"))
    drift = [(e["year"], e["items"], n) for e in baseline["editions"]
             if (n := sum(1 for r in rows if r["year"] == e["year"])) != e["items"]]

    # 失败 = 解析出了问题；注记 = 源头本来就这样，报出来但不当失败
    FAIL = (
        ("人类基线题量与题库不符", [f"{y}: 基线 {a} ≠ 题库 {b}" for y, a, b in drift]),
        ("无答案", [r["id"] for r in rows if not r["answer"]]),
        ("选项<4", [r["id"] for r in rows if r["num_options"] < 4]),
        ("题干过短", [r["id"] for r in rows if len(r["question"]) < 4
                  and r["source"] != "minglibench"]),
    )
    NOTE = (
        ("生辰缺失(源站未登，见 INVENTORY)",
         [r["id"] for r in rows if r["birth_info"].get("missing")]),
    )
    for mark, group in (("⚠", FAIL), ("·", NOTE)):
        for label, bad in group:
            if bad:
                print(f"{mark} {label} {len(bad)} 条: {bad[:10]}{' …' if len(bad) > 10 else ''}")
    return not any(bad for _, bad in FAIL)


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
