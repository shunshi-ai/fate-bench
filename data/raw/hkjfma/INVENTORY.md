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
| 12th | 2021 | images hosted on a Facebook CDN, not retrievable |
| 17th | 2026 | held June 2026; key not yet published. Question paper is available and cleanly paginated (`第1-5題` … `第36-40題`) — **revisit once the key is posted** |

## The 2018 edition is the most valuable single addition

It is the only edition that is simultaneously:

- **complete** — 40 items, no gaps, with an authoritative handwritten key
- **bilingual** — the organizer published English alongside Chinese, so no translation step is
  needed and none of our wording enters the data
- **method-labelled** — each of the 8 cases records which system the contributing master used:
  子平八字 (BaZi) ×5, 紫微斗數 (Zi Wei Dou Shu) ×2, 奇門遁甲 (Qi Men Dun Jia) ×1

That last field does not exist anywhere else in this corpus and allows stratifying by school.

## Cross-check: MingLi-Bench's 2023 transcription holds up

The 2023 key ([`images/2023_ans_021_01.jpg`](./images/2023_ans_021_01.jpg)) is a primary source for
an edition MingLi-Bench already transcribed, so that transcription could be audited rather than
inherited. It was, along both paths that can fail independently — their scraped source text and
their published `data.json` — and both agree with the organizer's sheet on **40 of 40** items.
Transcribed to [`2023_answer_key.txt`](./2023_answer_key.txt); the check is
[`scripts/crosscheck_2023.py`](../../../scripts/crosscheck_2023.py).
