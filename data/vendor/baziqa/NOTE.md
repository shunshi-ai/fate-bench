# BaziQA — vendored copy

Upstream: <https://github.com/ChenJiangxi/BaziQA> @ `8ea8222f8bd8ef8a6f1a5fb012344935a66e7686`
Paper: Chen & Liu, *BaziQA-Benchmark* — <https://arxiv.org/abs/2602.12889>

Only the five `contest8_*.json` files are copied here. They are what
`scripts/crosscheck_vendor.py` audits, so keeping them in-tree makes that audit reproducible
without network access. `celebrity50_zh.json` is **not** copied — see below.

## Why this repository holds a copy at all

BaziQA transcribes the same competition this dataset is built from (HKJFMA, 全球算命師大賽),
covering 2021–2025. Two of those editions matter here:

- **2021** — the organiser never published an answer key for it. The 40 questions in this
  dataset are transcribed from the organiser's own question images
  (`data/raw/hkjfma/images/2021_q_023_*.jpg`), but the **answers** come from BaziQA. They are
  flagged `answer_provenance: "third-party"` in `hkjfma_qa.json`.
- **2025** — likewise no official key. This dataset's answers come from MingLi-Bench;
  BaziQA transcribed the same paper independently and the two agree 40/40.

The reason for trusting BaziQA's transcription at all is measurable rather than assumed: for
2022, 2023 and 2024 this repository holds the organiser's own answer sheets as photographs, and
BaziQA's answers match them **120/120**. That is what `crosscheck_vendor.py` re-checks on every
run. It establishes that they transcribe accurately; it does **not** establish where their 2021
answers came from, which they do not state.

## Licence

The README carries an MIT badge and an explicit grant ("使用 / 修改 / 分发 / 私用"). Note that
the repository ships **no `LICENSE` file** — the README's own `[LICENSE](../LICENSE)` link is
broken as of the pinned commit. The stated intent is unambiguous, so the files are redistributed
here with attribution, but the gap is recorded rather than glossed over.

## What was deliberately left out

`celebrity50_zh.json` — 50 public figures with categorised life events. Not used, because
**44 of the 50 birth times are `12:00`**, the conventional placeholder for "time unknown", while
every record carries `"approximate": false`. An hour that is actually unknown but marked exact is
worse than a missing one: it silently corrupts the hour pillar in BaZi and the whole 命宮 in
Zi Wei, and nothing downstream can tell. Charts built on it would look valid and be wrong.

## A transcription bug worth knowing about

In `contest8_2021.json` the ninth subject (`female_19670827_P034`) carries two questions whose
`question_id` is prefixed `P033-Q39` / `P033-Q40` — the previous subject's id. The split itself
is correct: the last contributing master, 陳俊燊師傅, submitted **two** cases (three questions on
one person, two on the other), which is why that edition has eight masters but nine subjects.
Only the id prefix is wrong. This repository re-derives case grouping from the organiser's
images, so the bug does not propagate here.
