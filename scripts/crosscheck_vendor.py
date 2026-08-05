#!/usr/bin/env python3
"""Audit third-party transcriptions against the organizer's own answer sheets.

Two other projects transcribe the same competition. This repository reuses answers from both, so
neither is taken on trust: for 2022, 2023 and 2024 we hold the organizer's published answer sheet
— a photograph of a handwritten grid — and can check them outright.

    MingLi-Bench   2022–2025, 160 items, all reused here
    BaziQA         2021–2025; the 2021 answers are reused here, and 2025 corroborates MingLi's

For MingLi-Bench two comparisons run per edition, because they can fail independently:

    raw   — the answer marked inline in their scraped source text
    json  — the `answer` field in the dataset they publish

Two editions have no answer sheet on hkjfma.org and therefore cannot be audited at all — 2021
and 2025. What is checked for those is weaker and stated as such: that two independent
transcribers agree with each other. Items from both carry `answer_provenance: "third-party"`.

    python scripts/crosscheck_vendor.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "hkjfma"
VENDOR = ROOT / "data" / "vendor" / "minglibench"
BAZIQA = ROOT / "data" / "vendor" / "baziqa"
QA = ROOT / "data" / "hkjfma_qa.json"

# MingLi-Bench numbers 2022–2025 straight through 1–160, forty per edition.
SPANS = {2022: 1, 2023: 41, 2024: 81, 2025: 121}
AUDITABLE = (2022, 2023, 2024)
EDITION_NO = {2021: 12, 2022: 13, 2023: 14, 2024: 15, 2025: 16}


def from_baziqa(year):
    """BaziQA nests questions under each subject; flattening in file order gives 1..40.

    Their 2021 file lists nine subjects for eight contributing masters — the last master
    submitted two cases. The flattened order still matches the printed paper.
    """
    d = json.loads((BAZIQA / f"contest8_{year}.json").read_text(encoding="utf-8"))
    out, n = {}, 0
    for p in (x for x in d if "questions" in x):
        for q in p["questions"]:
            n += 1
            out[n] = q["answer"].strip().upper()
    return out


def ours(year):
    """Our own question bank, renumbered 1..40 within the edition."""
    rows = [r for r in json.loads(QA.read_text(encoding="utf-8"))
            if r["year"] == year and r["answer"]]
    rows.sort(key=lambda r: r["question_number"])
    return {i: r["answer"] for i, r in enumerate(rows, 1)}


def primary(year):
    """Our transcription of the organizer's answer sheet, as `{1..40: letter}`."""
    text = (RAW / f"{year}_answer_key.txt").read_text(encoding="utf-8")
    body = "\n".join(l for l in text.splitlines() if not l.startswith("#"))
    return {int(n): L for n, L in re.findall(r"\b(\d{1,2})\s+([A-D])\b", body)}


def from_raw(year):
    """Their source text marks the answer two different ways, depending on the year:

        2022/2023   the correct option carries a trailing `（正确答案）`
        2024/2025   the letter is appended to the question stem instead

    Option letters are mixed case in places (`c.与友人合伙投资…`); that is the real typography,
    not a typo, so matching is case-insensitive.
    """
    out, cur = {}, None
    for line in (l.strip() for l in (VENDOR / "raw" / f"{year}.txt").read_text().splitlines()):
        if m := re.match(r"^(?:Q\s*)?(\d{1,3})\s*[.、．]?\s*(.*)$", line):
            n, rest = int(m.group(1)), m.group(2)
            if 1 <= n <= 40:
                cur = n
                # 判据是「字母紧跟在全角字符后」，不是题干长度 —— `12 什么时候结婚？A`
                # 只有七个字，用长度阈值会把它漏掉。
                if tail := re.search(r"(?<=[^\x00-\x7F])([A-Da-d])\s*$", rest):
                    out[n] = tail.group(1).upper()
                continue
        if cur and (m := re.match(r"^([A-Da-d])\s*[.、．]?\s*", line)) and "正确答案" in line:
            out[cur] = m.group(1).upper()
    return out


def from_json(year):
    items = list(json.loads((VENDOR / "data.json").read_text()).values())[0]
    lo = SPANS[year]
    return {q["question_number"] - lo + 1: q["answer"]
            for q in items if lo <= q["question_number"] < lo + 40}


def compare(label, theirs, ours):
    missing = [n for n in ours if n not in theirs]
    diff = [(n, ours[n], theirs[n]) for n in sorted(ours) if n in theirs and theirs[n] != ours[n]]
    print(f"    {label:<6} {len(ours) - len(missing) - len(diff)}/{len(ours)} 一致"
          + (f"  未收录 {missing}" if missing else "")
          + (f"  ❌ 不一致 {diff}" if diff else ""))
    return not diff, not missing


if __name__ == "__main__":
    clean = True

    print("A. 对主办方一手答案表（可判真伪）")
    for year in AUDITABLE:
        key = primary(year)
        if len(key) != 40:
            sys.exit(f"{year} 答案表只解析出 {len(key)} 题，应为 40")
        print(f"  {year} 第{EDITION_NO[year]}屆")
        for label, theirs in (("ML raw", from_raw(year)), ("ML json", from_json(year)),
                              ("BaziQA", from_baziqa(year)), ("本仓库", ours(year))):
            ok, complete = compare(label, theirs, key)
            clean &= ok
            if not complete and label == "ML raw":
                print("           （他们的原文里这些题没标答案，不算不一致）")

    # 这两届主办方没公布答案，比不了真伪，只能比「两家独立转录是否互相印证」。
    # 一致只说明转录稳定，不等于答案正确 —— 措辞上不能混。
    print("\nB. 无官方答案表的两届（只能比互证，不能判真伪）")
    for year, holder in ((2021, "BaziQA→本仓库"), (2025, "MingLi→本仓库")):
        a, b = from_baziqa(year), ours(year)
        common = sorted(set(a) & set(b))
        same = [n for n in common if a[n] == b[n]]
        mark = "○" if len(same) == len(common) else "❌"
        print(f"  {mark} {year} 第{EDITION_NO[year]}屆 {holder}："
              f"BaziQA 与本仓库 {len(same)}/{len(common)} 一致"
              f"{'' if len(same) == len(common) else ' —— 有出入，需人工复核'}")
        if len(same) != len(common):
            print(f"      {[(n, b[n], a[n]) for n in common if a[n] != b[n]]}")
            clean = False

    print("\n✅ 有一手答案的三届，四方全部核对无误。" if clean
          else "\n❌ 有出入，需人工复核答案表照片。")
    print("   2021/2025 两届主办方从未公布答案表，上面 B 段只是互证，"
          "不构成官方认证（数据里标 answer_provenance=third-party）。")
    sys.exit(0 if clean else 1)
