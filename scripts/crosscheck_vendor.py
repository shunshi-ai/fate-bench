#!/usr/bin/env python3
"""Audit MingLi-Bench's transcription against the organizer's own answer sheets.

MingLi-Bench covers 2022–2025 and this repository reuses all 160 of its items. Rather than
inherit those answers on trust, we hold the organizer's published answer sheet — a photograph of
a handwritten grid — for three of those four editions, so they can be checked outright.

Two comparisons run per edition, because they can fail independently:

    raw   — the answer marked inline in their scraped source text
    json  — the `answer` field in the dataset they publish

2025 has no answer sheet on hkjfma.org, so those 40 items remain unaudited. That is stated
rather than papered over.

    python scripts/crosscheck_vendor.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "hkjfma"
VENDOR = ROOT / "data" / "vendor" / "minglibench"

# MingLi-Bench numbers 2022–2025 straight through 1–160, forty per edition.
SPANS = {2022: 1, 2023: 41, 2024: 81, 2025: 121}
AUDITABLE = (2022, 2023, 2024)


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
    for year in AUDITABLE:
        ours = primary(year)
        if len(ours) != 40:
            sys.exit(f"{year} 答案表只解析出 {len(ours)} 题，应为 40")
        print(f"{year} 第{ {2022: 13, 2023: 14, 2024: 15}[year] }屆")
        for label, theirs in (("raw", from_raw(year)), ("json", from_json(year))):
            ok, complete = compare(label, theirs, ours)
            clean &= ok
            if not complete and label == "raw":
                print("           （他们的原文里这些题没标答案，不算不一致）")
    print(f"\n2025 第16屆 40 题未审计 —— hkjfma.org 没有公布该届答案表。")
    print("✅ 有一手答案的三届全部核对无误。" if clean else "❌ 有出入，需人工复核答案表照片。")
    sys.exit(0 if clean else 1)
