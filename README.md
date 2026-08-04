<div align="center">

# fate-bench

**Open dataset of Chinese metaphysics — real birth charts paired with documented life events.**

[![Data License: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](./LICENSE-DATA)
[![Code License: MIT](https://img.shields.io/badge/Code-MIT-yellow.svg)](./LICENSE-CODE)
[![Questions](https://img.shields.io/badge/Questions-255-green.svg)](./data/fate_bench.jsonl)
[![People](https://img.shields.io/badge/People-54-blue.svg)](./data/cases.json)
[![Editions](https://img.shields.io/badge/Editions-2010--2025-orange.svg)](./data/raw/hkjfma/INVENTORY.md)

English | [中文](./README_zh.md)

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

**255 questions · 54 people · every item with an official answer key · seven editions with a
published human score.**

Each record carries a full birth date, hour, and place, so the same person can be rendered as a
BaZi chart, a Zi Wei Dou Shu chart, or a Western natal chart. The data is not tied to one system,
and neither are the questions — they ask what happened to a person, not what a chart says.

## Data

| File | What it holds |
|---|---|
| [`data/fate_bench.jsonl`](./data/fate_bench.jsonl) | **everything, one question per line** — question, answer, birth data and both charts inlined. Start here. |
| [`data/hkjfma_qa.json`](./data/hkjfma_qa.json) | 255 questions — stem, options, answer, birth data, source URL |
| [`data/cases.json`](./data/cases.json) | 54 people — birth data plus computed BaZi and Zi Wei charts |
| [`data/human_baseline.json`](./data/human_baseline.json) | what human masters scored on these same questions |
| [`data/hkjfma_categories.json`](./data/hkjfma_categories.json) | topic label per HKJFMA item, with how each was assigned |
| [`data/raw/hkjfma/`](./data/raw/hkjfma/) | cleaned source text, transcribed answer keys, 76 archived source images |
| [`data/vendor/minglibench/`](./data/vendor/minglibench/) | MingLi-Bench, vendored unmodified under MIT |

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
| [HKJFMA Global Fortune Teller Competition](https://hkjfma.org) (全球算命師大賽) | 2010–2013, 2018 | 95 | published publicly by the organizer; cited with attribution |
| [MingLi-Bench](https://github.com/DestinyLinker/MingLi-Bench) (Destiny Linker) | 2022–2025 | 160 | MIT — reused with attribution |

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
| 13th | 2022 | 40 | 8 | A–D | via MingLi-Bench, audited against the organizer's sheet |
| 14th | 2023 | 40 | 8 | A–D | via MingLi-Bench, audited against the organizer's sheet |
| 15th | 2024 | 40 | 8 | A–D | via MingLi-Bench, audited against the organizer's sheet |
| 16th | 2025 | 40 | 8 | A–D | via MingLi-Bench — no sheet published, unaudited |

An edition is usable only if **both** its questions and its official answer key are public.
Several are not — the full audit, including why each excluded edition was excluded, is in
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
| 16th | 2025 | 40 | A–D | not published | 25% |

Seven of the nine editions in this dataset have one. Best human scores land between 47% and 67%
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
organizer's own tables — two independent sources. The 2023 and 2024 sheets also publish each
finisher's **per-case** score, which is in `human_baseline.json` too.

Full detail, caveats, and provenance in
[`data/human_baseline.json`](./data/human_baseline.json).

## How the ground truth was checked

**Answer keys were verified character by character.** Every edition's parsed answer string was
compared against the organizer's published key — `第一條: 1a, 2e, 3e` for 2010, the `答案公報`
block for 2013, the handwritten answer sheet for 2018. All five match exactly.

**MingLi-Bench's transcription was audited, not inherited.** We hold the organizer's own
handwritten answer sheets for three of the four editions MingLi-Bench covers — 2022, 2023 and
2024. Both their scraped source text and their published `data.json` agree with those sheets on
**120 of 120** items ([`scripts/crosscheck_vendor.py`](./scripts/crosscheck_vendor.py)). The
2025 edition has no published answer sheet, so its 40 items remain unaudited; that is stated
rather than glossed over.

**Charts are computed by third parties.** `lunar-python` for BaZi and `py-iztro` for Zi Wei —
the latter being the same iztro implementation MingLi-Bench uses. Ground truth should not come
from the party publishing the benchmark. Three cases print the contributing master's own
hand-calculated four pillars next to the birth data; all three agree with the computed chart.

**Where the source is incomplete, it is marked, not filled in.** Two of the 54 cases have no
chart: the 2018 case whose birth data the organizer never published, and the 2013 case whose
birth hour is *what the question asks you to infer*.

## Notes on the data

- **Option counts vary by edition.** Early editions use five options (A–E), later ones four.
  Random-guess baselines therefore differ (20% vs 25%) and must not be pooled naively.
  231 items have four options, 24 have five.
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
- **Zi Wei star names come out in Simplified Chinese**, from `py-iztro`, while the questions are
  in Traditional. Nothing is transliterated in either direction.
- **Topic labels come from two different hands.** All 255 items carry a `category` drawn from
  MingLi-Bench's twelve-label taxonomy, but `category_source` says where each came from:
  MingLi-Bench annotated their 160, and the 95 added here were labelled by keyword rules
  (`scripts/categorize.py`) with nine hand-corrections. Run against MingLi-Bench's 160 human
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
python scripts/crosscheck_vendor.py  # audit MingLi-Bench against the primary answer sheets
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

## License

Code under [MIT](./LICENSE-CODE). Compiled data under [CC BY 4.0](./LICENSE-DATA), which does not
extend to the underlying source material — see [SOURCES.md](./data/raw/hkjfma/SOURCES.md).

Curated by [Shunshi.AI](https://shunshi.ai/en).
