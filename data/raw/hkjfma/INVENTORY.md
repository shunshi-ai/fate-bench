# Inventory — what survives the answer-key check

An edition is usable only if **both** the questions and the official answer key are public.
Many editions publish questions and a winners table but never the key; those are excluded
outright. Every row below was verified by opening the source, not by trusting the page title —
several pages titled "答案及得獎名單" contain no answer key at all.

## Usable

| Edition | Year | Items | Cases | Options | Questions | Answer key | Notes |
|---:|---|---:|---:|:---:|---|---|---|
| 1st | 2010 | 9 | 3 | A–E | text | text, `第一條: 1a, 2e, 3e` | whole paper printed twice on the page |
| 2nd | 2011 | 15 | 3 | a–e | text | text, full-width letters mixed in | **prints the master's own four pillars** |
| 3rd | 2012 | 15 | 3 | A–D | text | text, `1 C 2 B …` | |
| 4th | 2013 | 16 | 4 | A–D | text | text, `答案公報` | one item inverts the task (infer birth hour); HK DST noted |
| 9th | 2018 | 40 | 9 | A–D | text, **bilingual zh+en** | image → [`2018_answer_key.txt`](./2018_answer_key.txt) | **each case labels its method**; see the two findings below |
| 13th–16th | 2022–2025 | 160 | 32 | A–D | via MingLi-Bench | via MingLi-Bench | 2023 key audited here — 40/40 |

**Total: 255 items, 54 cases, 2010–2025. Every item carries an official answer.**

Each edition's parsed answer string was compared character by character against the organizer's
published key. All five match exactly.

## Two things about 2018 that only reading the source revealed

**It is 9 cases, not 8 × 5.** 鄭智恆師傅 contributed *two different people* under one provider
heading — a 1994 man (Q1–2) and a 1973 woman (Q3–5). Assuming one case per master would attach
five questions to the wrong birth chart.

**陳開通師傅's case (Q21–25) has no birth data.** The organizer published the questions but never
the chart; it is absent from the page's HTML, not lost in extraction, and the 7 images on that
page are the masters' portraits, not the paper. Those 5 items are kept, with
`birth_info.missing = true` — they carry an answer but cannot be charted. Any parser that treats
the provider line as decoration will silently let them inherit the preceding case's chart
(the Malaysian 1960 man), which is worse than leaving them blank.

## Excluded, with reason

| Edition | Year | Why |
|---:|---|---|
| 5th | 2014 | 35 questions published, **no answer key ever posted** |
| 6th | 2015 | no question paper on the site |
| 7th | 2016 | winners and scores only |
| 8th | 2017 | 35 questions published, no key. (Red text on that page marks *question stems*, not answers — an easy misread.) |
| 10th | 2019 | key never posted. The page titled "答案,得獎名單及統計資料" holds a winners table and AllCounted survey screenshots showing per-option response counts. Response distribution is **not** ground truth — on this material the majority is frequently wrong. |
| 11th | 2020 | question paper is legible, but both images on the "答案及得獎名單" page are winners tables. No key. |
| 12th | 2021 | question paper archived here (9 images), **no answer key ever posted** — the whole site has only two 2021 pages, both the call for entries |
| 17th | 2026 | held June 2026; question paper archived here (8 images, `第1-5題` … `第36-40題`), key not yet published — **revisit** |

## A correction: 2021 was not unreachable

An earlier pass here recorded the 2021 question paper as hosted on a Facebook CDN and therefore
not retrievable. That was wrong, and wrong in an avoidable way — the filenames merely *look*
like Facebook exports (`192170775_10222464528615607_..._n.jpg`); the files themselves sit on
`hkjfma.org/wp-content/uploads/2021/06/` like every other year's. They are archived here now.

The edition still cannot be used, but for the other reason: no answer key was ever published.

## Editions whose questions are archived but which stay out of the dataset

2014, 2017, 2020, 2021 and 2026 all have a readable question paper and no published answer key.
The papers are kept under `images/` so that, if the organizer ever posts a key, transcription is
the only remaining step. They are deliberately **not** in `hkjfma_qa.json`: an item without a
recorded correct answer is not a benchmark item, and the response distributions that exist for
some editions are not a substitute (see 2019 above).

## The 2018 edition is the most valuable single addition

It is the only edition that is simultaneously:

- **complete** — 40 items, no gaps, with an authoritative handwritten key
- **bilingual** — the organizer published English alongside Chinese, so no translation step is
  needed and none of our wording enters the data
- **method-labelled** — each of the 8 cases records which system the contributing master used:
  子平八字 (BaZi) ×5, 紫微斗數 (Zi Wei Dou Shu) ×2, 奇門遁甲 (Qi Men Dun Jia) ×1

That last field does not exist anywhere else in this corpus and allows stratifying by school.

## Cross-check: MingLi-Bench's transcription holds up

MingLi-Bench covers 2022–2025. The organizer published a handwritten answer sheet for three of
those four editions, so those transcriptions could be audited rather than inherited:

| Edition | Year | Answer sheet | Their raw text | Their `data.json` |
|---:|---|---|---|---|
| 13th | 2022 | [`images/2022_ans_022_01.jpg`](./images/2022_ans_022_01.jpg) | 40/40 | 40/40 |
| 14th | 2023 | [`images/2023_ans_021_01.jpg`](./images/2023_ans_021_01.jpg) | 40/40 | 40/40 |
| 15th | 2024 | [`images/2024_ans_015_01.jpeg`](./images/2024_ans_015_01.jpeg) | 40/40 | 40/40 |
| 16th | 2025 | none published | — | — |

Transcribed to `2022_answer_key.txt`, `2023_answer_key.txt`, `2024_answer_key.txt`; the check is
[`scripts/crosscheck_vendor.py`](../../../scripts/crosscheck_vendor.py). **120 of 120 agree.**
The 2025 edition's 40 items are the only ones in this dataset with neither an independent audit
nor a human baseline.

## Results tables (the human baseline)

Separate from the answer keys, the organizer publishes what the winners scored. Those are
transcribed into [`../../human_baseline.json`](../../human_baseline.json). Sources:

| Year | Image | What it gives |
|---|---|---|
| 2018 | `images/2018_ans_058_02.jpg` | totals, dropped-high/low, final scores, regions |
| 2022 | `images/2022_ans_022_02.jpg` | same, plus a note that the top raw total was *not* the champion |
| 2023 | `images/2023_ans_021_02/03/04.jpg` | same, plus **per-case** scores for the champions |
| 2024 | `images/2024_ans_015_02.jpeg` | same, plus per-case scores; highest human score in the corpus (26/40) |

2010–2012 publish theirs as prose on the question page. 2013 and 2025 publish none.
