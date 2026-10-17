---
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

**[Browse and try every question online (Chinese) →](https://shunshi.ai/zh-tw/fortune-teller-contest)** · Curated by [ShunShi](https://shunshi.ai/en)

335 multiple-choice questions about 71 real people — the year someone divorced, started
a business, lost a parent, was diagnosed with cancer. Each was set by a practising master who
supplied a real person's birth data and that person's verified history; the organizer published
the correct answers after the contest closed, **along with what the human entrants scored**.

## Read this before you use the answers

They are not all of one grade, and the dataset says which is which:

| `answer_provenance` | Items | What it means |
|---|---:|---|
| `official` | 255 | the organizer published the correct answer, on the question page or on an answer sheet transcribed from the photograph |
| `third-party` | 80 | the organizer never published a key for that edition (2021, 2025); the answer comes from another project's transcription, of unstated origin |

The third-party answers are kept because they are otherwise complete and well corroborated — two
projects transcribed each of those editions independently and agree 40/40 — but agreement between
transcribers is evidence of careful transcription, not of ground truth. If you want only answers
the organizer stood behind:

```python
from datasets import load_dataset

ds = load_dataset("shunshi-ai/fate-bench")["train"]
official = ds.filter(lambda r: r["answer_provenance"] == "official")   # 255 items
```

## Configs

| Config | Rows | Contents |
|---|---:|---|
| `questions` *(default)* | 335 | question, options, answer, topic, and the subject's birth data — flat |
| `cases` | 71 | one row per person: birth data plus computed BaZi and Zi Wei charts |

Join on `case_id`. The split exists because the Zi Wei chart nests palaces → stars →
transformations; inlining that into every question makes the dataset viewer unusable.

```python
questions = load_dataset("shunshi-ai/fate-bench", "questions")["train"]
cases      = load_dataset("shunshi-ai/fate-bench", "cases")["train"]
```

## What a chart contains

69 of the 71 people carry both charts. Four pillars alone are a snapshot with no
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

11 editions: 2010, 2011, 2012, 2013, 2018, 2021, 2022, 2023, 2024, 2025, 2026. Eight of them also published what the
human entrants scored — best human results land between 47% and 78% against a 20–25% random
floor. Those figures, with their caveats, are in the
[GitHub repository](https://github.com/shunshi-ai/fate-bench).

## Known limits

- **This is a Chinese dataset; English coverage is partial and is not ours.** All 335 questions
  are in Chinese, Traditional and Simplified both, as each edition printed them. 53 items also
  carry `question_en` — that is **the organizer's own bilingual publication**, not a translation
  made here. The other 282 have no English, and there is no Japanese or Korean. Translate it
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
