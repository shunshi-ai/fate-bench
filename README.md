<div align="center">

# fate-bench

**Open datasets for Chinese metaphysics — birth charts paired with documented life events.**

[![Data License: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](./LICENSE-DATA)
[![Code License: MIT](https://img.shields.io/badge/Code-MIT-yellow.svg)](./LICENSE-CODE)

English | [中文](./README_zh.md)

</div>

> **Status: work in progress.** This repository is under active construction and is not yet
> ready for general use. Question counts, schema, and file layout will change.

---

## What this is

Most public data about BaZi (八字) and Zi Wei Dou Shu (紫微斗数) is one of two things: birth
charts with no outcomes attached, or interpretations with no verifiable ground truth. Neither
supports evaluation.

This repository collects **birth data paired with documented life outcomes** — the year someone
divorced, started a business, lost a parent, had surgery — as multiple-choice items with a single
recorded correct answer.

Because each record carries a **full birth date, hour, and place**, the same person can be
rendered as a BaZi chart, a Zi Wei Dou Shu chart, or a Western natal chart. The data is not
tied to one system.

## Sources

| Source | Coverage | License / status |
|---|---|---|
| [HKJFMA Global Fortune Teller Competition](https://hkjfma.org) (全球算命師大賽) | 2010–2026, 17 editions | Published publicly by the organizer; cited with attribution |
| [MingLi-Bench](https://github.com/DestinyLinker/MingLi-Bench) (Destiny Linker) | 2022–2025, 160 items | MIT — reused with attribution |

The HKJFMA competition has run annually since 2010. Each edition is authored by a panel of
practising masters who supply a real birth chart along with that person's verified history, then
publish the answer key after the contest closes. Prior work covered the four most recent editions;
this repository works backwards through the earlier ones.

## Current state

Verified as having **both questions and a published answer key**:

| Edition | Year | Items | Options | Answer format |
|---|---|---|---|---|
| 1st | 2010 | 9 | A–E | inline list |
| 2nd | 2011 | 15 | a–e | inline list |
| 3rd | 2012 | 15 | A–D | inline list |
| 4th | 2013 | 16 | A–D | `答案公報` block |
| 13th–16th | 2022–2025 | 160 | A–D | via MingLi-Bench |

Editions whose answer keys are published as **images** (2018, 2019, 2020, 2021, 2023) are pending
transcription. Editions **2014, 2016, and 2017** publish questions and winners but no answer key,
and are excluded.

Nothing here is normalized into a final schema yet — `data/raw/` holds cleaned source text only.

## Notes on the data

- **Option counts vary by edition.** Early editions use five options (A–E), later ones four.
  Random-guess baselines therefore differ (20% vs 25%) and must not be pooled naively.
- **Answer encodings vary.** At least four distinct formats appear across editions: an inline
  answer list, a `（正确答案）` marker on the correct option, a letter appended to the question
  stem, and red-coloured text in the HTML.
- **Some editions embed the master's own chart calculation.** The 2nd edition prints the four
  pillars alongside the birth data (`壬子年 庚戌月 丁酉日 乙巳時`), giving an independent
  human-computed reference for the same birth moment.
- **One item type inverts the task.** The 4th edition asks solvers to infer the *birth hour* from
  the life history, rather than predict events from the chart.
- **Daylight saving is sometimes flagged.** The 4th edition explicitly notes Hong Kong DST for one
  case and states it does not change the resulting double-hour.

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
