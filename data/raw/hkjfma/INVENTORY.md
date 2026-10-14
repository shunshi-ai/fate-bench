# Inventory — what survives the answer-key check

An edition is usable only if the questions **and** a correct answer for every item are public.
Many editions publish questions and a winners table but never a key; those are excluded outright.
Every row below was verified by opening the source, not by trusting the page title — several
pages titled "答案及得獎名單" contain no answer key at all.

Answers are not all of one grade, and the dataset does not pretend otherwise. Every item carries
`answer_provenance`:

- **`official`** — the organizer published the correct answer, either on the question page itself
  or on a separate answer sheet transcribed here from the photograph. 255 items.
- **`third-party`** — the organizer never published a key for that edition; the answer comes from
  another project's transcription, of unstated origin. 80 items (2021, 2025). Kept because they
  are otherwise complete and well-corroborated, flagged so they can be filtered out.

## Usable

| Edition | Year | Items | Cases | Options | Questions | Answer key | Notes |
|---:|---|---:|---:|:---:|---|---|---|
| 1st | 2010 | 9 | 3 | A–E | text | official — text, `第一條: 1a, 2e, 3e` | whole paper printed twice on the page |
| 2nd | 2011 | 15 | 3 | a–e | text | official — text, full-width letters mixed in | **prints the master's own four pillars** |
| 3rd | 2012 | 15 | 3 | A–D | text | official — text, `1 C 2 B …` | |
| 4th | 2013 | 16 | 4 | A–D | text | official — text, `答案公報` | one item inverts the task (infer birth hour); HK DST noted |
| 9th | 2018 | 40 | 9 | A–D | text, **bilingual zh+en** | official — image → [`2018_answer_key.txt`](./2018_answer_key.txt) | **each case labels its method**; see the two findings below |
| 12th | 2021 | 40 | 9 | A–D | **images → [`2021_questions_023.txt`](./2021_questions_023.txt)** | ⚠ third-party → [`2021_answers_thirdparty.txt`](./2021_answers_thirdparty.txt) | 8 masters but **9 subjects** — the last submitted two cases |
| 13th–15th | 2022–2024 | 120 | 24 | A–D | via MingLi-Bench | official — answer sheets audited here, 120/120 | |
| 16th | 2025 | 40 | 8 | A–D | via MingLi-Bench | ⚠ third-party — no sheet published | two projects transcribed it independently and agree 40/40 |
| 17th | 2026 | 40 | 8 | A–D | **images → [`2026_questions_transcribed.txt`](./2026_questions_transcribed.txt)** | official — image → [`2026_answer_key.txt`](./2026_answer_key.txt) | key and results were **added to the June question page in August**, not posted separately — see below |

**Total: 335 items, 71 cases, 2010–2026 across 11 editions.**

Each edition with an official key had its parsed answer string compared character by character
against the organizer's published key. All match exactly.

### The 2021 questions are transcribed here from the organizer's own images

Unlike 2022–2025, this edition's text does not come from another project. It is transcribed from
the nine images this repository archives (`images/2021_q_023_01.jpg` … `_09.jpg`), which makes the
questions a primary source even though the answers are not. Two typographic errors in the
original are reproduced verbatim rather than silently corrected — Q18's 「王寅大運」 should read
壬寅, and Q5's 「法妻」 should read 髮妻. Correcting them would make the transcription
unverifiable against the images.

The transcription was then checked against BaziQA's independent copy of the same paper: every
number in every stem and option was compared (digits survive the traditional/simplified split,
so they are the reliable comparison surface). The only four differences are places where the
source repeats 「這位1970年出生的游先生」 and BaziQA abbreviates it away.

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

## 2026: the key was added to the question page, not posted

The 17th edition's question paper went up on 2026-06-21. When this repository first archived it
(2026-08-03) the page held only the paper, so 2026 was parked as "no key yet". The organizer then
**edited that same page**: a handwritten 正確答案 sheet on 2026-08-08 and the results table on
2026-08-10 (WordPress `modified` 2026-08-10). No new post was created, so a check of the post list
by title shows nothing. **To look for a newly published key, re-open the original question page
or compare its `modified` date (`/wp-json/wp/v2/posts?search=…&_fields=date,modified,title`) —
do not rely on the list of post titles.** The 2025 page follows the same pattern.

Transcription notes: Q31–Q34 print their stems on two lines (a red heading over a red question);
they are joined with 「：」 so the line parser keeps both halves. Wording is otherwise as printed,
including the simplified characters in Q26/Q29/Q30, 「紫微鬥數」 in case 6, and the Cantonese 「嘅」
in Q36. Case 4 gives only a range (`上午 5-6 點`), which falls inside 卯時, so the hour is recorded
as 卯 with no clock time. Case 8 states no birthplace; the 台灣 on the next line is the
contributing master's location and is not used as one.

As a check on the computed chart, Q36's options were written by the contributing master from the
chart itself — 「日主庚金」「戌為火庫」「亥水」 — and the computed pillars (庚午 day, 戊戌 month,
丁亥 hour) agree.

## Two corrections about 2021

**It is not unreachable.** An earlier pass recorded the 2021 question paper as hosted on a
Facebook CDN and therefore not retrievable. That was wrong, and wrong in an avoidable way — the
filenames merely *look* like Facebook exports
(`192170775_10222464528615607_..._n.jpg`); the files themselves sit on
`hkjfma.org/wp-content/uploads/2021/06/` like every other year's.

**It is now in the dataset, on third-party answers.** This inventory previously excluded the
edition for the other reason: no key was ever published, and the standard here was that an item
without a recorded correct answer is not a dataset item. That standard is unchanged for the
*organizer's* answers — what changed is that a second project, BaziQA, publishes answers for it,
and their transcription of the three editions we *can* audit is exact (120/120). So the 40 items
are included with `answer_provenance: "third-party"` rather than left on the floor. The cover
page explains why no key exists: the paper was answered through an AllCounted web form under
「自動計分制」, so the correct answers stayed with the organizer.

## Editions whose questions are archived but which stay out of the dataset

2014, 2017 and 2020 all have a readable question paper and no answer, from any source. The
papers are kept under `images/` so that, if a key surfaces, transcription is the only remaining
step. They are deliberately **not** in `hkjfma_qa.json`: an item without a recorded correct
answer is not a dataset item, and the response distributions that exist for some editions are not
a substitute (see 2019 above).

## The 2018 edition is the most valuable single addition

It is the only edition that is simultaneously:

- **complete** — 40 items, no gaps, with an authoritative handwritten key
- **bilingual** — the organizer published English alongside Chinese, so no translation step is
  needed and none of our wording enters the data
- **method-labelled** — each of the 8 cases records which system the contributing master used:
  子平八字 (BaZi) ×5, 紫微斗數 (Zi Wei Dou Shu) ×2, 奇門遁甲 (Qi Men Dun Jia) ×1

That last field does not exist anywhere else in this corpus and allows stratifying by school.

## Cross-check: both third-party transcriptions hold up

Two other projects transcribe this competition — [MingLi-Bench][ml] (2022–2025) and
[BaziQA][bq] (2021–2025). This repository reuses answers from both, so neither is taken on trust.
The organizer published a handwritten answer sheet for three editions, which makes those
transcriptions auditable outright:

| Edition | Year | Answer sheet | MingLi raw | MingLi `data.json` | BaziQA | This repo |
|---:|---|---|---|---|---|---|
| 13th | 2022 | [`images/2022_ans_022_01.jpg`](./images/2022_ans_022_01.jpg) | 40/40 | 40/40 | 40/40 | 40/40 |
| 14th | 2023 | [`images/2023_ans_021_01.jpg`](./images/2023_ans_021_01.jpg) | 40/40 | 40/40 | 40/40 | 40/40 |
| 15th | 2024 | [`images/2024_ans_015_01.jpeg`](./images/2024_ans_015_01.jpeg) | 40/40 | 40/40 | 40/40 | 40/40 |

Transcribed to `2022_answer_key.txt`, `2023_answer_key.txt`, `2024_answer_key.txt`; the check is
[`scripts/crosscheck_vendor.py`](../../../scripts/crosscheck_vendor.py). **120 of 120 agree, all
four ways.**

For 2021 and 2025 there is no sheet to check against, so nothing can establish that the answers
are *right* — only that two independent transcribers agree, which they do 40/40 on each. That is
evidence of careful transcription, not of ground truth, and the distinction is kept in the data
(`answer_provenance: "third-party"`) rather than blurred in prose.

BaziQA's five contest files are vendored under
[`../../vendor/baziqa/`](../../vendor/baziqa/) so the audit runs offline; see the
[NOTE](../../vendor/baziqa/NOTE.md) there for what was deliberately not taken from it and why.

[ml]: https://github.com/DestinyLinker/MingLi-Bench
[bq]: https://github.com/ChenJiangxi/BaziQA

## Results tables (the human baseline)

Separate from the answer keys, the organizer publishes what the winners scored. Those are
transcribed into [`../../human_baseline.json`](../../human_baseline.json). Sources:

| Year | Image | What it gives |
|---|---|---|
| 2018 | `images/2018_ans_058_02.jpg` | totals, dropped-high/low, final scores, regions |
| 2022 | `images/2022_ans_022_02.jpg` | same, plus a note that the top raw total was *not* the champion |
| 2023 | `images/2023_ans_021_02/03/04.jpg` | same, plus **per-case** scores for the champions |
| 2024 | `images/2024_ans_015_02.jpeg` | same, plus per-case scores |
| 2026 | `images/2026_ans_001_02.jpeg` | same, plus per-case scores; highest human score in the corpus (31/40). The screenshot crops the case-9 column — derived as total minus cases 2–8, and for all 15 finishers that reproduces the published final score |

2010–2012 publish theirs as prose on the question page. 2013, 2021 and 2025 publish none — for
2021 the site holds only two pages, both the call for entries, and neither carries results.

That leaves 2021 and 2025 as the two editions with neither an official answer key nor a human
score: 80 of the 335 items. Both are usable and both are marked.
