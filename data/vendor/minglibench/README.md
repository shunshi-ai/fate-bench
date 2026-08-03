# Vendored: MingLi-Bench

Verbatim copy of the data files from
[**DestinyLinker/MingLi-Bench**](https://github.com/DestinyLinker/MingLi-Bench),
released under the **MIT License** (see [LICENSE](./LICENSE)).

Vendored at commit-time from the repository's `main` branch, August 2026.

| File | Contents |
|---|---|
| `data.json` | 160 normalized multiple-choice items, 32 cases, HKJFMA editions 13–16 (2022–2025) |
| `fortune_api_results.json` | Pre-computed BaZi and Zi Wei charts, keyed by `case_id` (computed with [iztro](https://github.com/SylarLong/iztro)) |
| `raw/2022–2025.txt` | The source transcriptions the JSON was normalized from |

## Why vendored rather than linked

Reproducibility. This repository's normalized output merges these items with editions 1–12, and a
merge is only auditable if the exact input is pinned. Upstream has not been pushed since
2026-05-09; if it moves or disappears, the merge remains verifiable.

## Known format variation in the upstream raw files

The four raw files do not share one answer encoding:

- `2022.txt`, `2023.txt`, `2025.txt` — correct option marked inline with `（正确答案）`
- `2024.txt` — correct letter appended to the question stem (`1.下列哪一个描述…？B`)

Any parser reading `raw/` directly must handle both. `data.json` has already normalized this away.

## Attribution

If you use this material, cite the original:

> MingLi-Bench — Destiny Linker — https://github.com/DestinyLinker/MingLi-Bench

Questions and answer keys within it originate from the HKJFMA Global Fortune Teller Competition;
see [../../raw/hkjfma/SOURCES.md](../../raw/hkjfma/SOURCES.md).
