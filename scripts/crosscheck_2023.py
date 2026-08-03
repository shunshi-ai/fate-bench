#!/usr/bin/env python3
"""Audit MingLi-Bench's 2023 transcription against the primary answer key.

MingLi-Bench covers 2022–2025 and this repository reuses it. Rather than inherit those answers
on trust, we hold the organizer's own answer sheet for one of those editions — the handwritten
grid photographed at `images/2023_ans_021_01.jpg` — so that edition can be checked outright.

Two comparisons run, because they can fail independently:

    raw   — the answer markers `（正确答案）` in their scraped source text
    json  — the `answer` field in the dataset they publish

    python scripts/crosscheck_2023.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY = ROOT / "data" / "raw" / "hkjfma" / "2023_answer_key.txt"
VENDOR = ROOT / "data" / "vendor" / "minglibench"

# MingLi-Bench numbers 2022–2025 straight through 1–160; 2023 occupies 41–80.
SPAN = range(41, 81)


def primary():
    """Our transcription of the organizer's answer sheet, as `{1..40: letter}`."""
    text = KEY.read_text(encoding="utf-8")
    body = "\n".join(l for l in text.splitlines() if not l.startswith("#"))
    return {int(n): L for n, L in re.findall(r"\b(\d{1,2})\s+([A-D])\b", body)}


def from_raw():
    """Their source text marks the right option inline with `（正确答案）`."""
    out, cur = {}, None
    for line in (l.strip() for l in (VENDOR / "raw" / "2023.txt").read_text().splitlines()):
        if m := re.match(r"^Q\s*(\d{1,2})", line):
            cur = int(m.group(1))
        # 选项字母大小写混排：`c.与友人合伙投资…（正确答案）` 是真实写法，不是笔误
        elif cur and (m := re.match(r"^([A-Da-d])\s*[.、．]?\s*", line)) and "正确答案" in line:
            out[cur] = m.group(1).upper()
    return out


def from_json():
    items = list(json.loads((VENDOR / "data.json").read_text()).values())[0]
    return {q["question_number"] - SPAN.start + 1: q["answer"]
            for q in items if q["question_number"] in SPAN}


def compare(name, theirs, ours):
    missing = [n for n in ours if n not in theirs]
    diff = [(n, ours[n], theirs[n]) for n in sorted(ours) if n in theirs and theirs[n] != ours[n]]
    agree = len(ours) - len(missing) - len(diff)
    print(f"{name:<6} {agree}/{len(ours)} 一致"
          + (f"  未收录 {missing}" if missing else "")
          + (f"  不一致 {diff}" if diff else ""))
    return not (missing or diff)


if __name__ == "__main__":
    ours = primary()
    if len(ours) != 40:
        sys.exit(f"答案表只解析出 {len(ours)} 题，应为 40")
    ok = all([compare("raw", from_raw(), ours), compare("json", from_json(), ours)])
    print("\n" + ("✅ MingLi-Bench 的 2023 转录经一手答案表核对无误。"
                  if ok else "❌ 有出入，需人工复核答案表照片。"))
    sys.exit(0 if ok else 1)
