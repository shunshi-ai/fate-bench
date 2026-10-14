#!/usr/bin/env python3
"""Build the Hugging Face upload from the canonical files.

The repository's own artefact, `data/fate_bench.jsonl`, inlines each question's full BaZi and
Zi Wei charts. That is convenient for a local script and hostile to the HF dataset viewer: the
Zi Wei chart alone nests palaces → stars → mutagens, and a viewer that cannot infer the schema
shows nothing at all — which on HF means the dataset looks empty to everyone browsing it.

So the upload is split in two, one row per thing rather than one row per join:

    questions.jsonl   335 rows — what an evaluation actually reads. Flat.
    cases.jsonl        71 rows — one person, both charts. Nested, but only here.

`case_id` joins them. Nothing is dropped; it is the same data, shaped for the viewer.

    python scripts/export_hf.py            # writes hf/
    python scripts/export_hf.py --check    # validate only, no write
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QA = ROOT / "data" / "hkjfma_qa.json"
CASES = ROOT / "data" / "cases.json"
OUT = ROOT / "hf"

# 题目表刻意不带命盘 —— 见模块 docstring
Q_FIELDS = ["id", "source", "year", "edition", "case_id", "question_number", "question",
            "question_en", "options", "num_options", "answer", "answer_provenance",
            "answer_provenance_note", "category", "category_source", "master", "method",
            "source_url"]


def build():
    rows = json.loads(QA.read_text(encoding="utf-8"))
    cases = json.loads(CASES.read_text(encoding="utf-8"))

    questions = []
    for r in rows:
        q = {k: r.get(k) for k in Q_FIELDS}
        b = r.get("birth_info") or {}
        # 生辰在两张表里都留一份 —— 只想跑题目的人不该被迫再 join 一次
        q["birth_year"], q["birth_month"], q["birth_day"] = (b.get("year"), b.get("month"),
                                                             b.get("day"))
        q["birth_shichen"] = b.get("shichen")
        q["birth_gender"], q["birth_location"] = b.get("gender"), b.get("location")
        q["birth_data_missing"] = bool(b.get("missing"))
        questions.append(q)

    return questions, cases


def card(questions, cases):
    n = len(questions)
    prov = Counter(q["answer_provenance"] for q in questions)
    years = sorted({q["year"] for q in questions})
    charted = sum(1 for c in cases if c.get("charts"))
    en = sum(1 for q in questions if q.get("question_en"))
    return f"""---
license: cc-by-4.0
language:
  - zh
task_categories:
  - multiple-choice
  - question-answering
size_categories:
  - n<1K
tags:
  - bazi
  - ziwei-doushu
  - chinese-metaphysics
  - astrology
  - evaluation
  - reasoning
configs:
  - config_name: questions
    default: true
    data_files:
      - split: train
        path: questions.jsonl
  - config_name: cases
    data_files:
      - split: train
        path: cases.jsonl
---

# fate-bench

**Real birth charts paired with documented life events**, from a fortune-telling competition that
has run annually since 2010.

{n} multiple-choice questions about {len(cases)} real people — the year someone divorced, started
a business, lost a parent, was diagnosed with cancer. Each was set by a practising master who
supplied a real person's birth data and that person's verified history; the organizer published
the correct answers after the contest closed, **along with what the human entrants scored**.

## Read this before you use the answers

They are not all of one grade, and the dataset says which is which:

| `answer_provenance` | Items | What it means |
|---|---:|---|
| `official` | {prov['official']} | the organizer published the correct answer, on the question page or on an answer sheet transcribed from the photograph |
| `third-party` | {prov['third-party']} | the organizer never published a key for that edition (2021, 2025); the answer comes from another project's transcription, of unstated origin |

The third-party answers are kept because they are otherwise complete and well corroborated — two
projects transcribed each of those editions independently and agree 40/40 — but agreement between
transcribers is evidence of careful transcription, not of ground truth. If you want only answers
the organizer stood behind:

```python
from datasets import load_dataset

ds = load_dataset("shunshi-ai/fate-bench")["train"]
official = ds.filter(lambda r: r["answer_provenance"] == "official")   # {prov['official']} items
```

## Configs

| Config | Rows | Contents |
|---|---:|---|
| `questions` *(default)* | {n} | question, options, answer, topic, and the subject's birth data — flat |
| `cases` | {len(cases)} | one row per person: birth data plus computed BaZi and Zi Wei charts |

Join on `case_id`. The split exists because the Zi Wei chart nests palaces → stars →
transformations; inlining that into every question makes the dataset viewer unusable.

```python
questions = load_dataset("shunshi-ai/fate-bench", "questions")["train"]
cases      = load_dataset("shunshi-ai/fate-bench", "cases")["train"]
```

## What a chart contains

{charted} of the {len(cases)} people carry both charts. Four pillars alone are a snapshot with no
time axis, and most questions here ask *"in which year did X happen"* — read off the decade luck
cycles. So each case carries what a practitioner would actually work from:

| BaZi | Zi Wei Dou Shu |
|---|---|
| four pillars, day master | twelve palaces with stem and branch |
| ten gods (十神) per pillar | major stars with brightness and the four transformations (四化) |
| hidden-stem gods (藏干十神) | minor and adjective stars, 長生十二神 |
| na yin (納音) | body palace, soul and body stars, five-elements class |
| **decade luck cycles (大運)** | **decadal age range (大限) per palace** |

Charts are computed by third-party libraries — `lunar-python` and `py-iztro` — not by the party
publishing this dataset. Three cases print the contributing master's own hand-calculated four
pillars next to the birth data; all three agree with the computed chart.

## Coverage

{len(years)} editions: {', '.join(str(y) for y in years)}. Eight of them also published what the
human entrants scored — best human results land between 47% and 78% against a 20–25% random
floor. Those figures, with their caveats, are in the
[GitHub repository](https://github.com/shunshi-ai/fate-bench).

## Known limits

- **This is a Chinese dataset; English coverage is partial and is not ours.** All {n} questions
  are in Chinese, Traditional and Simplified both, as each edition printed them. {en} items also
  carry `question_en` — that is **the organizer's own bilingual publication**, not a translation
  made here. The other {n - en} have no English, and there is no Japanese or Korean. Translate it
  yourself if you need one language throughout; that way any translation error stays yours rather
  than being baked into the ground truth.
- **Two cases have no chart.** One is the 2018 case whose birth data the organizer never
  published; the other is the 2013 case whose birth hour is *what the question asks you to infer*.
- **Five questions cannot be answered from this data at all** — the organizer printed that case's
  birth data on the paper but not on the web page, so the human entrants had it and you do not.
  They carry `birth_data_missing: true`. Drop them before scoring.
- **Option counts vary by edition** — early editions use five options, later ones four. Random
  baselines therefore differ (20% vs 25%) and should not be pooled naively.
- **Times are as published.** No true-solar-time correction. Where only a double-hour (時辰) is
  given, the midpoint is used — exact for the hour pillar, ambiguous for the day pillar in 子時.
- **Topic labels come from two hands** — see `category_source`. The rule-based labels reproduce
  the human annotator's choice 76% of the time, so treat per-topic slices as approximate.

## Source, licence, ethics

Source: the HKJFMA Global Fortune Teller Competition (全球算命師大賽), published openly by the
organizer. Two other transcriptions of the same competition are reused with attribution —
[MingLi-Bench](https://github.com/DestinyLinker/MingLi-Bench) and
[BaziQA](https://github.com/ChenJiangxi/BaziQA), both MIT.

These records describe real people, identified only by birth data and gender — no names, exactly
as the organizer published them. Released as a cultural and evaluative resource: including a
record makes no claim that the outcome was correctly predicted, nor any claim about the
predictive validity of the systems involved.

Compiled data under CC BY 4.0, which does not extend to the underlying source material.
Full provenance, the per-edition audit, and the build scripts are on
[GitHub](https://github.com/shunshi-ai/fate-bench).

Curated by [Shunshi.AI](https://shunshi.ai/en).
"""


def report(questions, cases):
    prov = Counter(q["answer_provenance"] for q in questions)
    print(f"questions.jsonl  {len(questions)} 行 · 有答案 {sum(1 for q in questions if q['answer'])}"
          f" · official {prov['official']} / third-party {prov['third-party']}")
    print(f"cases.jsonl      {len(cases)} 行 · 有盘 {sum(1 for c in cases if c.get('charts'))}")
    ok = True
    # 闸一：两张表必须能 join 上，孤儿 case_id 会让 cases config 形同虚设
    if orphan := {q["case_id"] for q in questions} - {c["case_id"] for c in cases}:
        print(f"  ❌ questions 里有 {len(orphan)} 个 case_id 在 cases 里找不到: {sorted(orphan)[:5]}")
        ok = False
    # 闸二：每题都要有 provenance，漏标等于把第三方答案伪装成官方
    if blank := [q["id"] for q in questions if not q["answer_provenance"]]:
        print(f"  ❌ {len(blank)} 题没有 answer_provenance: {blank[:5]}")
        ok = False
    # 闸三：题目表不能夹带命盘 —— 夹带了 viewer 就打不开，等于白发
    if leaked := [k for k in questions[0] if "chart" in k or k == "birth_info"]:
        print(f"  ❌ 题目表混进了嵌套字段: {leaked}")
        ok = False
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    questions, cases = build()
    ok = report(questions, cases)
    if not args.check:
        OUT.mkdir(exist_ok=True)
        for name, rows in (("questions", questions), ("cases", cases)):
            p = OUT / f"{name}.jsonl"
            p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                         encoding="utf-8")
            print(f"→ {p.relative_to(ROOT)}  ({p.stat().st_size // 1024} KB)")
        (OUT / "README.md").write_text(card(questions, cases), encoding="utf-8")
        print(f"→ hf/README.md")
    sys.exit(0 if ok else 1)
