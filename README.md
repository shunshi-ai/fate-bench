<div align="center">

# fate-bench

**Open dataset of Chinese metaphysics — real birth charts paired with documented life events.**

[![Data License: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](./LICENSE-DATA)
[![Code License: MIT](https://img.shields.io/badge/Code-MIT-yellow.svg)](./LICENSE-CODE)
[![Questions](https://img.shields.io/badge/Questions-335-green.svg)](./data/fate_bench.jsonl)
[![People](https://img.shields.io/badge/People-71-blue.svg)](./data/cases.json)
[![Editions](https://img.shields.io/badge/Editions-2010--2026-orange.svg)](./data/raw/hkjfma/INVENTORY.md)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-fate--bench-yellow.svg)](https://huggingface.co/datasets/shunshi-ai/fate-bench)

English | [中文](./README_zh.md) · **[Browse and try every question online (Chinese) →](https://shunshi.ai/zh-tw/fortune-teller-contest)**

</div>

---

## What this is

Most public data about BaZi (八字) and Zi Wei Dou Shu (紫微斗数) is one of two things: birth charts
with nothing attached, or interpretations with nothing to check them against. Neither is much use
as data.

This is **birth data paired with documented life outcomes** — the year someone divorced, started a
business, lost a parent, was diagnosed with cancer — recorded as multiple-choice items with a
single correct answer, published by the party that knew the answer in advance.

The source is an annual competition that has run since 2010. Practising fortune tellers enter in
public, under their own names, for a trophy; each edition is set by a panel of masters who supply
a real person's birth data and that person's verified history, and the organizer publishes the
answer key after the contest closes — **along with what the entrants scored**.

**335 questions · 71 people · eleven editions, 2010–2026 · eight of them with a published human
score.**

Answers are not all of one grade and the data says which is which. 255 items carry the
organizer's own published answer (`answer_provenance: "official"`); 80 come from a third-party
transcription of two editions the organizer answered but never published a key for
(`"third-party"`). Filter on that field if you only want the first kind.

Each record carries a full birth date, hour, and place, so the same person can be rendered as a
BaZi chart, a Zi Wei Dou Shu chart, or a Western natal chart. The data is not tied to one system,
and neither are the questions — they ask what happened to a person, not what a chart says.

## Data

| File | What it holds |
|---|---|
| [`data/fate_bench.jsonl`](./data/fate_bench.jsonl) | **everything, one question per line** — question, answer, birth data and both charts inlined. Start here. |
| [`data/hkjfma_qa.json`](./data/hkjfma_qa.json) | 335 questions — stem, options, answer, birth data, source URL |
| [`data/cases.json`](./data/cases.json) | 71 people — birth data plus computed BaZi and Zi Wei charts |
| [`data/human_baseline.json`](./data/human_baseline.json) | what human masters scored on these same questions |
| [`data/hkjfma_categories.json`](./data/hkjfma_categories.json) | topic label per HKJFMA item, with how each was assigned |
| [`data/raw/hkjfma/`](./data/raw/hkjfma/) | cleaned source text, transcribed answer keys, 79 archived source images |
| [`data/vendor/minglibench/`](./data/vendor/minglibench/) | MingLi-Bench, vendored unmodified under MIT |
| [`data/vendor/baziqa/`](./data/vendor/baziqa/) | BaziQA's five contest files, vendored so the audit runs offline |

```json
{
  "id": "hkjfma_2011_01",
  "year": 2011, "edition": 2, "case_id": "hkjfma_2011_c1",
  "birth_info": {
    "year": 1972, "month": 11, "day": 2, "shichen": "巳",
    "gender": "男", "location": "中國大陸",
    "pillars_stated_by_master": "壬子年 庚戌月 丁酉日 乙巳時"
  },
  "question": "1976丙辰年,唐山大地震中六親情況?",
  "options": [{"letter": "A", "text": "父親在地震中死亡"}, "…"],
  "answer": "A",
  "num_options": 5
}
```

### What a chart contains

`cases.json` does not stop at the four pillars. Four pillars alone are a snapshot with no time
axis, and most questions here are *"in which year did X happen"* — which is read off the decade
luck cycles. So each case carries what a practitioner would actually work from:

| BaZi | Zi Wei Dou Shu |
|---|---|
| four pillars, day master | twelve palaces with stem and branch |
| ten gods (十神) per pillar | major stars with brightness and the four transformations (四化) |
| hidden-stem gods (藏干十神) | minor and adjective stars, 長生十二神 |
| na yin (納音) | body palace, soul and body stars, five-elements class |
| **decade luck cycles (大運)** — ganzhi, year range, age range, direction, start date | **decadal age range (大限) per palace** |

```json
"luck_cycles": {
  "starts": "1974-08-02", "direction": "順行",
  "cycles": [{"ganzhi": "辛亥", "years": [1974, 1983], "ages": [3, 12]}, "…"]
}
```

## Sources

| Source | Coverage | Items | License / status |
|---|---|---:|---|
| [HKJFMA Global Fortune Teller Competition](https://hkjfma.org) (全球算命師大賽) | 2010–2013, 2018, **2021**, **2026** | 175 | published publicly by the organizer; cited with attribution. 2021 and 2026 transcribed here from the organizer's question images |
| [MingLi-Bench](https://github.com/DestinyLinker/MingLi-Bench) (Destiny Linker) | 2022–2025 | 160 | MIT — reused with attribution |
| [BaziQA](https://github.com/ChenJiangxi/BaziQA) (Chen & Liu) | 2021 answers only | — | MIT per its README; supplies the 40 answers for an edition the organizer never keyed |

The competition has run annually since 2010. Each edition is authored by a panel of practising
masters who supply a real birth chart along with that person's verified history, then publish the
answer key after the contest closes. Prior work covered the four most recent editions; this
repository works backwards through the earlier ones.

| Edition | Year | Items | Cases | Options | Answer key |
|---:|---|---:|---:|:---:|---|
| 1st | 2010 | 9 | 3 | A–E | text |
| 2nd | 2011 | 15 | 3 | a–e | text |
| 3rd | 2012 | 15 | 3 | A–D | text |
| 4th | 2013 | 16 | 4 | A–D | text |
| 9th | 2018 | 40 | 9 | A–D | transcribed from the published photograph |
| 12th | 2021 | 40 | **9** | A–D | ⚠ third-party — the organizer never published one |
| 13th | 2022 | 40 | 8 | A–D | via MingLi-Bench, audited against the organizer's sheet |
| 14th | 2023 | 40 | 8 | A–D | via MingLi-Bench, audited against the organizer's sheet |
| 15th | 2024 | 40 | 8 | A–D | via MingLi-Bench, audited against the organizer's sheet |
| 16th | 2025 | 40 | 8 | A–D | ⚠ third-party — no sheet published |
| 17th | 2026 | 40 | 8 | A–D | transcribed from the published photograph |

2021 is the one edition with nine cases from eight contributing masters: the last, 陳俊燊師傅,
submitted two people rather than one (three questions on one, two on the other). Splitting five
questions per master would attach the wrong birth chart to two of them.

An edition is usable only if its questions **and** a correct answer for every item are public.
Several fail that and are excluded; two pass it only through a third party and are marked rather
than excluded. The full audit — every edition, why each was kept or dropped — is in
[data/raw/hkjfma/INVENTORY.md](./data/raw/hkjfma/INVENTORY.md).

The **9th edition (2018)** is the most valuable single addition. It is complete, the organizer
published it **bilingually in Chinese and English** — so no translation of ours enters the data —
and each case records **which system the contributing master used** (子平八字 ×6, 紫微斗數 ×2,
奇門遁甲 ×1). That field exists nowhere else in this corpus and makes it possible to stratify
by school.

## The human baseline

These questions were not written for a benchmark. They were written for a contest that practising
masters entered under their own names, for a trophy, with the answers sealed until it closed. The
organizer published the winners' scores — so unlike almost any other dataset in this domain, there
is a documented answer to "how well do humans actually do at this?"

| Edition | Year | Items | Options | Best human score | Random |
|---:|---|---:|:---:|---|---:|
| 1st | 2010 | 9 | A–E | **6 / 9** (66.7%) | 20% |
| 2nd | 2011 | 15 | a–e | **8 / 15** (53.3%) | 20% |
| 3rd | 2012 | 15 | A–D | **8 / 15** (53.3%) | 25% |
| 4th | 2013 | 16 | A–D | not published | 25% |
| 9th | 2018 | 40 | A–D | **19 / 40** (47.5%) | 25% |
| 13th | 2022 | 40 | A–D | **21 / 40** (52.5%) | 25% |
| 14th | 2023 | 40 | A–D | **21 / 40** (52.5%) | 25% |
| 15th | 2024 | 40 | A–D | **26 / 40** (65.0%) | 25% |
| 17th | 2026 | 40 | A–D | **31 / 40** (77.5%) | 25% |
| 12th | 2021 | 40 | A–D | not published | 25% |
| 16th | 2025 | 40 | A–D | not published | 25% |

Eight of the eleven editions in this dataset have one. Best human scores land between 47% and 78%
against a 20–25% floor — above chance in every edition that published results, and well short of
solved in all of them.

Read these as a **ceiling, not an average**. Only the top finishers' scores were published; the
mean over all entrants is unknown for every edition, and entrant counts are mostly unpublished, so
a top score from a large field is not comparable to the same score from a small one.

Two details matter if you plan to compare a model against these. From the 9th edition on, the
official ranking is diving-style — each entrant's best and worst case are dropped, leaving 30 of
40 questions — so the 2018 champions' *official* result is 15/30 while their raw 40-question total
is 19. The column above is the raw figure, the one comparable to running a model over this dataset.
A consequence the organizer spells out on the 2022 sheet: **the highest raw total is not
necessarily the champion** — in 2022 the best raw score belonged to a runner-up. And option counts
differ by edition, so the random-guess floor moves.

For 2022–2025 the questions come via MingLi-Bench while these scores are transcribed from the
organizer's own tables — two independent sources. The 2023, 2024 and 2026 sheets also publish each
finisher's **per-case** score, which is in `human_baseline.json` too.

Full detail, caveats, and provenance in
[`data/human_baseline.json`](./data/human_baseline.json).

## How the ground truth was checked

**Answer keys were verified character by character.** Every edition's parsed answer string was
compared against the organizer's published key — `第一條: 1a, 2e, 3e` for 2010, the `答案公報`
block for 2013, the handwritten answer sheets for 2018 and 2026. All six match exactly.

**Third-party transcriptions were audited, not inherited.** Two other projects transcribe this
competition — MingLi-Bench (2022–2025) and BaziQA (2021–2025) — and this dataset reuses answers
from both. We hold the organizer's own handwritten answer sheets for three of those editions:
2022, 2023 and 2024. Against those sheets, MingLi-Bench's scraped source text, MingLi-Bench's
published `data.json`, BaziQA's files and this repository's own parse all agree on **120 of 120**
items ([`scripts/crosscheck_vendor.py`](./scripts/crosscheck_vendor.py)).

**Two editions cannot be audited at all, and are labelled instead.** For 2021 and 2025 the
organizer published no answer sheet, so nothing can establish that those 80 answers are *correct*
— only that two independent transcribers agree, which they do 40/40 on each. Agreement is
evidence of careful transcription, not of ground truth. Those items carry
`answer_provenance: "third-party"` so they can be excluded in one filter.

**Charts are computed by third parties.** `lunar-python` for BaZi and `py-iztro` for Zi Wei —
the latter being the same iztro implementation MingLi-Bench uses. Ground truth should not come
from the party publishing the benchmark. Three cases print the contributing master's own
hand-calculated four pillars next to the birth data; all three agree with the computed chart.

**Where the source is incomplete, it is marked, not filled in.** Two of the 71 cases have no
chart: the 2018 case whose birth data the organizer never published, and the 2013 case whose
birth hour is *what the question asks you to infer*.

**Typos in the source are reproduced, not silently fixed.** The 2021 paper misprints 壬寅 as
「王寅」 (Q18) and 髮妻 as 「法妻」 (Q5). Both are kept as printed, so the transcription stays
checkable against the archived images; both are recorded in the inventory.

## Notes on the data

- **Option counts vary by edition.** Early editions use five options (A–E), later ones four.
  Random-guess baselines therefore differ (20% vs 25%) and must not be pooled naively.
  311 items have four options, 24 have five.
- **One case can span a variable number of questions.** The 2018 edition is not 8 cases of 5:
  one contributing master supplied two different people, splitting his block 2 + 3.
- **Times are as published.** No true-solar-time correction is applied. Where only a double-hour
  (時辰) is given, the midpoint is used — exact for the hour pillar, since any instant inside a
  double-hour yields the same one. 子時 is the exception: it straddles midnight, so the *day*
  pillar is ambiguous. `resolved_time.source` says which case you are looking at.
- **Some editions embed the master's own chart calculation.** The 2nd edition prints the four
  pillars alongside the birth data (`壬子年 庚戌月 丁酉日 乙巳時`), giving an independent
  human-computed reference for the same birth moment.
- **One item type inverts the task.** The 4th edition asks solvers to infer the *birth hour* from
  the life history, rather than predict events from the chart.
- **Five items cannot be answered from this data at all.** The organizer printed that case's
  birth data on the paper but never on the web page, so the 2018 entrants had it and we do not.
  They keep their answer key and are flagged `birth_info.missing`; anything scoring this dataset
  should drop them, since using them means working from less than the humans had.
- **The dataset is Chinese. English coverage is partial and is not ours.** All 335 questions are
  in Chinese — Traditional and Simplified both appear, as printed by each edition; nothing is
  converted in either direction. 53 items also carry `question_en`, and those are **the
  organizer's own bilingual publication** (all 16 of the 4th edition, 37 of the 9th), not a
  translation made here. The remaining 282 have no English, and there is no Japanese or Korean.
  If you need the whole set in one language you will have to translate it yourself — which also
  means any translation error is yours to own, not silently baked into the ground truth.
- **Zi Wei star names come out in Simplified Chinese**, from `py-iztro`, while the questions are
  in Traditional. Nothing is transliterated in either direction.
- **Topic labels come from two different hands.** 334 of the 335 items carry a `category` drawn
  from MingLi-Bench's twelve-label taxonomy, but `category_source` says where each came from:
  MingLi-Bench annotated their 160, and the 175 added here were labelled by keyword rules
  (`scripts/categorize.py`) with fifteen hand-corrections. Run against MingLi-Bench's 160 human
  labels, those rules reproduce the human choice **76%** of the time — treat per-topic slices as
  approximate, not as one annotator's consistent judgement. One item is deliberately left
  unlabelled: the 2013 question that asks you to infer the birth hour is about the chart itself,
  not about any facet of a life.

## Reproducing

```bash
pip install lunar-python py-iztro

python scripts/normalize.py       # source text  → data/hkjfma_qa.json
python scripts/charts.py          # birth data   → data/cases.json
python scripts/categorize.py      # topic labels    → data/hkjfma_categories.json
python scripts/export_jsonl.py    # join everything → data/fate_bench.jsonl
python scripts/crosscheck_vendor.py  # audit both third-party sources against the answer sheets
```

Every script takes `--check` to validate without writing.

## Ethics and scope

These records describe real people, identified only by birth data and gender — no names. They are
published here as they were published by the competition organizer.

This is released as a **cultural and evaluative resource**. Including a record makes no claim that
the recorded outcome was correctly predicted, nor any claim about the predictive validity of the
systems involved.

## Related

- [`shunshi-ai/east-asian-celebrity-bazi`](https://huggingface.co/datasets/shunshi-ai/east-asian-celebrity-bazi)
  — 2,284 public figures with computed year/month/day pillars
- [`shunshi-ai/bazi-reader-mcp`](https://github.com/shunshi-ai/bazi-reader-mcp)
  — open-source sexagenary calendar engine

Other transcriptions of the same competition, both reused here with attribution:

- [`DestinyLinker/MingLi-Bench`](https://github.com/DestinyLinker/MingLi-Bench) — 2022–2025, 160 items
- [`ChenJiangxi/BaziQA`](https://github.com/ChenJiangxi/BaziQA) — 2021–2025, plus a paper
  ([arXiv:2602.12889](https://arxiv.org/abs/2602.12889))

## License

Code under [MIT](./LICENSE-CODE). Compiled data under [CC BY 4.0](./LICENSE-DATA), which does not
extend to the underlying source material — see [SOURCES.md](./data/raw/hkjfma/SOURCES.md).

Curated by [Shunshi.AI](https://shunshi.ai/en).
