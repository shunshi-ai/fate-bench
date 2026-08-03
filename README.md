<div align="center">

# fate-bench

**Open datasets for Chinese metaphysics — birth charts paired with documented life events.**

[![Data License: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](./LICENSE-DATA)
[![Code License: MIT](https://img.shields.io/badge/Code-MIT-yellow.svg)](./LICENSE-CODE)

English | [中文](./README_zh.md)

</div>

## What this is

Most public data about BaZi (八字) and Zi Wei Dou Shu (紫微斗数) is one of two things: birth
charts with no outcomes attached, or interpretations with no verifiable ground truth. Neither
supports evaluation.

This repository collects **birth data paired with documented life outcomes** — the year someone
divorced, started a business, lost a parent, was diagnosed with cancer — as multiple-choice items
with a single recorded correct answer, published by the party that knew the answer in advance.

**255 questions across 54 people, every one with an official answer key.**

Because each record carries a full birth date, hour, and place, the same person can be rendered
as a BaZi chart, a Zi Wei Dou Shu chart, or a Western natal chart. The data is not tied to one
system — and neither are the questions, which ask what happened to a person, not what a chart says.

## Data

| File | What it holds |
|---|---|
| [`data/hkjfma_qa.json`](./data/hkjfma_qa.json) | 255 questions — stem, options, answer, birth data, source URL |
| [`data/cases.json`](./data/cases.json) | 54 people — birth data plus computed BaZi and Zi Wei charts |
| [`data/raw/hkjfma/`](./data/raw/hkjfma/) | cleaned source text, transcribed answer keys, 46 archived source images |
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
| 13th–16th | 2022–2025 | 160 | 32 | A–D | via MingLi-Bench |

An edition is usable only if **both** its questions and its official answer key are public.
Several are not — the full audit, including why each excluded edition was excluded, is in
[data/raw/hkjfma/INVENTORY.md](./data/raw/hkjfma/INVENTORY.md).

The **9th edition (2018)** is the most valuable single addition. It is complete, the organizer
published it **bilingually in Chinese and English** — so no translation of ours enters the data —
and each case records **which system the contributing master used** (子平八字 ×6, 紫微斗數 ×2,
奇門遁甲 ×1). That field exists nowhere else in this corpus and makes it possible to stratify
by school.

## How the ground truth was checked

**Answer keys were verified character by character.** Every edition's parsed answer string was
compared against the organizer's published key — `第一條: 1a, 2e, 3e` for 2010, the `答案公報`
block for 2013, the handwritten answer sheet for 2018. All five match exactly.

**MingLi-Bench's transcription was audited, not inherited.** We hold the organizer's own
handwritten answer sheet for 2023, an edition MingLi-Bench already covers. Both their scraped
source text and their published `data.json` agree with it on **40 of 40** items
([`scripts/crosscheck_2023.py`](./scripts/crosscheck_2023.py)).

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
- **Zi Wei star names come out in Simplified Chinese**, from `py-iztro`, while the questions are
  in Traditional. Nothing is transliterated in either direction.

## Reproducing

```bash
pip install lunar-python py-iztro

python scripts/normalize.py       # source text  → data/hkjfma_qa.json
python scripts/charts.py          # birth data   → data/cases.json
python scripts/crosscheck_2023.py # audit MingLi-Bench against the primary key
```

Add `--check` to `normalize.py` or `charts.py` to validate without writing.

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
