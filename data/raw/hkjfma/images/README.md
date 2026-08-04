# Source images

Archived from hkjfma.org. Several editions publish their question papers and answer keys only as
photographs, not as text. These are kept so that any transcription in this repository can be
checked against the original — and because the source site is unstable (its footer currently
carries injected spam links, a sign it has been compromised at some point).

Filenames: `{year}_{q|ans}_{page}_{index}.jpg`, where `page` matches the entry in
[`../_pages_index.json`](../_pages_index.json), which records the source URL for each.

## What each set actually contains

Verified by reading them. Titles on the source pages are not reliable — a page titled
"答案及得獎名單" may contain no answer key at all.

| Set | Images | Contents | Usable answer key? |
|---|---|---|---|
| `2018_q_046_*` | 7 | question paper | — (questions) |
| `2018_ans_058_*` | 2 | **complete answer key** (01) and the results table (02) | ✅ |
| `2019_ans_055_*` | 12 | winners table + AllCounted analytics screenshots: full option text and how many entrants picked each option. **No correct answer is marked** — checked image by image | ❌ |
| `2019_q_056_*` | 10 | question paper, as screenshots of the same survey tool | — (questions) |
| `2020_q_024_*`, `2020_q_049_*` | 8 + 9 | question paper, clean and legible (two URLs, same content) | — (questions) |
| `2020_ans_048_*` | 2 | **winners list only — no answer key** | ❌ |
| `2021_q_023_*` | 9 | question paper (phone screenshots, 640×1136); image 01 is the call for entries, 02–09 are the 8 cases | — (questions) |
| `2022_ans_022_*` | 2 | **complete answer key** (01) and the results table (02) | ✅ |
| `2023_ans_021_*` | 4 | **complete answer key** (01), 40 items handwritten in a grid grouped by case with each contributing master named; results tables with per-case scores (02–04) | ✅ |
| `2024_ans_015_*` | 2 | **complete answer key** (01) and the results table as an Excel screenshot with per-case scores (02) | ✅ |
| `2026_q_*` | 8 | question paper, one image per 5 questions, high resolution and cleanly typeset | — (questions) |

The 2022/2023/2024 keys matter even though MingLi-Bench already covers those editions: they are
the primary source, so that transcription can be audited rather than trusted. It was — 120/120,
see [`scripts/crosscheck_vendor.py`](../../../scripts/crosscheck_vendor.py).

## Reading them

The images are legible at their published resolution (roughly 540×960 to 976×1024). No OCR
preprocessing was needed; they were transcribed by reading directly.
