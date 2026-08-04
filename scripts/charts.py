#!/usr/bin/env python3
"""Render every case's birth moment as a BaZi chart and a Zi Wei Dou Shu chart.

The questions are system-agnostic — they ask what happened to a person, not what a chart says.
So the charts are derived here rather than transcribed, and deliberately by **third-party**
libraries (`lunar-python`, `py-iztro`, the same iztro implementation MingLi-Bench uses) rather
than by our own engine. Ground truth should not come from the party publishing the benchmark.

Two editions print the master's own four pillars next to the birth data. Those are treated as
an assertion the pipeline must satisfy: if a computed chart disagrees with what the contributing
master wrote by hand, that is reported, not silently overwritten.

    python scripts/charts.py            # writes data/cases.json
    python scripts/charts.py --check    # validate only, no write
"""
import argparse
import json
import sys
from pathlib import Path

from lunar_python import Solar
from py_iztro import Astro

ROOT = Path(__file__).resolve().parent.parent
QA = ROOT / "data" / "hkjfma_qa.json"
OUT = ROOT / "data" / "cases.json"

SHICHEN_SPAN = {"子": (23, 1), "丑": (1, 3), "寅": (3, 5), "卯": (5, 7),
                "辰": (7, 9), "巳": (9, 11), "午": (11, 13), "未": (13, 15),
                "申": (15, 17), "酉": (17, 19), "戌": (19, 21), "亥": (21, 23)}


def resolve_hour(b: dict):
    """Return (hour, minute, how). Any instant inside a double-hour yields the same hour pillar,
    so a midpoint is exact — except 子時, which straddles midnight and therefore changes the *day*
    pillar depending on which side of it the birth fell."""
    if (h := b.get("clock_hour") if "clock_hour" in b else b.get("hour")) is not None:
        return h, b.get("clock_minute", b.get("minute", 0)) or 0, "stated"
    if z := b.get("shichen"):
        start, _ = SHICHEN_SPAN[z]
        if z == "子":
            # 只知道「子時」时无法判断在子夜哪一侧，日柱因此有歧义 —— 标出来，不猜
            return 0, 0, "midpoint of 子時 (ambiguous: day pillar depends on side of midnight)"
        return start + 1, 0, f"midpoint of {z}時"
    return None, None, "unknown"


def time_index(hour: int) -> int:
    """iztro 的时辰序号：0=早子時, 1=丑, …, 11=亥, 12=晚子時。"""
    return (hour + 1) // 2


def bazi(y, m, d, hh, mi, gender=None):
    """Four pillars, plus the things a practitioner would actually reason with.

    The pillars alone are not a usable chart. Nearly every question here is "in which year did X
    happen", and that is answered off the **decade luck cycles** (大運) — without them the chart is
    a snapshot with no time axis. The ten gods (十神) are the relational labels practitioners think
    in; hidden stems (藏干) carry the rest.
    """
    s = Solar.fromYmdHms(y, m, d, hh, mi, 0)
    lunar = s.getLunar()
    e = lunar.getEightChar()
    out = {
        "pillars": {"year": e.getYear(), "month": e.getMonth(),
                    "day": e.getDay(), "hour": e.getTime()},
        "day_master": e.getDayGan(),
        "lunar": str(lunar).replace("　", " "),
        "ten_gods": {
            "year": e.getYearShiShenGan(), "month": e.getMonthShiShenGan(),
            "day": "日主", "hour": e.getTimeShiShenGan(),
        },
        "hidden_stem_gods": {
            "year": e.getYearShiShenZhi(), "month": e.getMonthShiShenZhi(),
            "day": e.getDayShiShenZhi(), "hour": e.getTimeShiShenZhi(),
        },
        "nayin": {"year": e.getYearNaYin(), "month": e.getMonthNaYin(),
                  "day": e.getDayNaYin(), "hour": e.getTimeNaYin()},
    }
    if gender in ("男", "女"):
        yun = e.getYun(1 if gender == "男" else 0)
        out["luck_cycles"] = {
            "starts": yun.getStartSolar().toYmd(),
            "direction": "順行" if yun.isForward() else "逆行",
            # 第一段是童限（起运前），没有干支，留着但标出来
            "cycles": [{"ganzhi": c.getGanZhi() or None,
                        "years": [c.getStartYear(), c.getEndYear()],
                        "ages": [c.getStartAge(), c.getEndAge()]}
                       for c in yun.getDaYun()],
        }
    return out


def ziwei(y, m, d, hh, gender):
    chart = Astro().by_solar(f"{y}-{m}-{d}", time_index(hh), gender)
    return {
        "soul": chart.soul, "body": chart.body,
        "five_elements_class": chart.five_elements_class,
        "palaces": [
            {
                "name": p.name,
                "branch": p.earthly_branch,
                "stem": p.heavenly_stem,
                "is_body_palace": p.is_body_palace,
                # 大限：这一宫管哪个年龄段。跟八字的大運同一个作用 —— 给命盘一条时间轴
                "decadal_ages": list(p.decadal.range) if p.decadal else None,
                "major_stars": [
                    {"name": s.name, "brightness": s.brightness or None,
                     "mutagen": s.mutagen or None} for s in p.major_stars
                ],
                "minor_stars": [
                    {"name": s.name, "brightness": s.brightness or None,
                     "mutagen": s.mutagen or None} for s in p.minor_stars
                ],
                "adjective_stars": [s.name for s in p.adjective_stars],
                "changsheng12": p.changsheng12,
            }
            for p in chart.palaces
        ],
    }


def build():
    rows = json.loads(QA.read_text(encoding="utf-8"))
    cases, order = {}, []
    for r in rows:
        if r["case_id"] not in cases:
            order.append(r["case_id"])
            cases[r["case_id"]] = {
                "case_id": r["case_id"], "source": r["source"], "year": r["year"],
                "edition": r["edition"], "master": r.get("master"),
                "method_used_by_master": r.get("method"),
                "birth_info": r["birth_info"], "question_ids": [],
                "source_url": r["source_url"],
            }
        cases[r["case_id"]]["question_ids"].append(r["id"])

    out, skipped, mismatches = [], [], []
    for cid in order:
        c = cases[cid]
        b = c["birth_info"]
        if b.get("missing") or not b.get("year"):
            c["charts"] = None
            c["charts_unavailable"] = b.get("reason", "no birth date in the source")
            skipped.append(cid)
            out.append(c)
            continue

        hh, mi, how = resolve_hour(b)
        c["resolved_time"] = {"hour": hh, "minute": mi, "source": how,
                              "timezone": "as published (no true-solar-time correction applied)"}
        charts = {}
        if hh is None:
            c["charts"] = None
            # 2013 第四例的题目本身就是「推出生时辰」，缺时辰是题面而非缺陷
            c["charts_unavailable"] = "birth hour unknown — for this case it is what the question asks"
            skipped.append(cid)
            out.append(c)
            continue

        charts["bazi"] = bazi(b["year"], b["month"], b["day"], hh, mi, b.get("gender"))
        if g := b.get("gender"):
            charts["ziwei"] = ziwei(b["year"], b["month"], b["day"], hh, g)
        c["charts"] = charts

        # 验真闸：拿师傅手排的四柱比对
        if stated := b.get("pillars_stated_by_master"):
            ours = " ".join(f"{v}{u}" for v, u in
                            zip(charts["bazi"]["pillars"].values(), "年月日時"))
            want = " ".join(stated.split())
            c["pillars_match_master"] = (ours == want)
            if ours != want:
                mismatches.append((cid, want, ours))
        out.append(c)

    return out, skipped, mismatches


def report(cases, skipped, mismatches):
    charted = [c for c in cases if c.get("charts")]
    checked = [c for c in cases if "pillars_match_master" in c]
    print(f"命例 {len(cases)} 个 · 已排盘 {len(charted)} · 跳过 {len(skipped)}")
    print(f"  八字 {sum(1 for c in charted if 'bazi' in c['charts'])}"
          f" · 紫微 {sum(1 for c in charted if 'ziwei' in c['charts'])}")
    print(f"  与师傅手排四柱比对 {len(checked)} 例，"
          f"一致 {sum(1 for c in checked if c['pillars_match_master'])}")
    for cid in skipped:
        c = next(x for x in cases if x["case_id"] == cid)
        print(f"  ⊘ {cid}: {c['charts_unavailable']}")
    for cid, want, ours in mismatches:
        print(f"  ❌ {cid} 师傅手排 {want} ≠ 本脚本 {ours}")
    return not mismatches


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    cases, skipped, mismatches = build()
    ok = report(cases, skipped, mismatches)
    if not args.check:
        OUT.write_text(json.dumps(cases, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n→ {OUT.relative_to(ROOT)}  ({len(cases)} 个命例)")
    sys.exit(0 if ok else 1)
