#!/usr/bin/env python3
"""Flatten the two source files into one self-contained JSONL — one line per question.

`hkjfma_qa.json` holds the questions and `cases.json` holds the charts, split that way because a
chart belongs to a person, not to a question, and up to five questions share one person. Anyone
running an eval has to join them anyway, so this does it once: each line carries the question,
the birth data, and both charts, and nothing else needs to be loaded.

    python scripts/export_jsonl.py            # writes data/fate_bench.jsonl
    python scripts/export_jsonl.py --check    # validate only, no write
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QA = ROOT / "data" / "hkjfma_qa.json"
CASES = ROOT / "data" / "cases.json"
OUT = ROOT / "data" / "fate_bench.jsonl"


def build():
    cases = {c["case_id"]: c for c in json.loads(CASES.read_text(encoding="utf-8"))}
    lines = []
    for q in json.loads(QA.read_text(encoding="utf-8")):
        c = cases[q["case_id"]]
        lines.append({
            "id": q["id"],
            "source": q["source"],
            "year": q["year"],
            "edition": q["edition"],
            "case_id": q["case_id"],
            "question": q["question"],
            "question_en": q.get("question_en"),
            "options": q["options"],
            "num_options": q["num_options"],
            "answer": q["answer"],
            "category": q.get("category"),
            "birth_info": q["birth_info"],
            "resolved_time": c.get("resolved_time"),
            "charts": c.get("charts"),
            "charts_unavailable": c.get("charts_unavailable"),
            "master": q.get("master"),
            "method_used_by_master": q.get("method"),
            "source_url": q["source_url"],
        })
    return lines


def report(lines):
    n_chart = sum(1 for l in lines if l["charts"])
    print(f"{len(lines)} 行 · 有答案 {sum(1 for l in lines if l['answer'])}"
          f" · 有命盘 {n_chart} · 无命盘 {len(lines) - n_chart}")

    problems = [l["id"] for l in lines if not l["answer"] or not l["options"]]
    orphan = [l["id"] for l in lines if l["charts"] is None and not l["charts_unavailable"]]
    for label, bad in (("缺答案或选项", problems), ("无盘且未说明原因", orphan)):
        if bad:
            print(f"⚠ {label}: {bad[:8]}")
    return not (problems or orphan)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    lines = build()
    ok = report(lines)
    if not args.check:
        with OUT.open("w", encoding="utf-8") as f:
            for l in lines:
                f.write(json.dumps(l, ensure_ascii=False) + "\n")
        print(f"\n→ {OUT.relative_to(ROOT)}  ({OUT.stat().st_size // 1024} KB)")
    sys.exit(0 if ok else 1)
