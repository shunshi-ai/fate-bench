#!/usr/bin/env python3
"""Assign a topic label to the 95 HKJFMA items, using MingLi-Bench's existing taxonomy.

MingLi-Bench labels all 160 of its items with one of twelve topics; the 95 items added by this
repository had none, so "accuracy by topic" could only be computed over part of the dataset.

The labels here are produced by **keyword rules, not a model**. A wrong label is worse than no
label — it silently biases any per-topic analysis — so the process has to be inspectable and
reproducible, and every labelled row records `category_source` so the two halves of the dataset
are never mistaken for one annotator's work.

Two things make the rules honest rather than guesswork:

*   The signal is usually in the **options**, not the stem. `此命1996年发生何事？` is labelled
    健康 by MingLi-Bench because its options are all illnesses. Rules therefore score the stem
    and the options together, weighting the stem higher.
*   MingLi-Bench's 160 labelled items are a **free validation set**. Running these rules against
    them measures how often the rules reproduce a human annotator's choice before they are
    applied to anything unlabelled.

    python scripts/categorize.py            # report agreement, write labels
    python scripts/categorize.py --check    # report only
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QA = ROOT / "data" / "hkjfma_qa.json"
LABELS = ROOT / "data" / "hkjfma_categories.json"

# MingLi-Bench 的十二类，原样沿用，不自造分类
RULES = {
    "官非": r"官非|刑事|訴訟|诉讼|坐牢|判刑|入獄|入狱|警察|三合會|法庭|吃官司|被捕",
    "灾劫": r"凶劫|災劫|灾劫|地震|大難|遇難|遇难|溺死|火災|火灾|被劫|打劫|被殺|被杀|謀殺|谋杀|詐騙|诈骗|呃錢",
    "子女": r"子女|兒子|儿子|女兒|女儿|生仔|生產|生产|懷孕|怀孕|小孩|孩子|嬰|婴|BB|一胎|頭胎|头胎|流產|流产|得子|生男|生女",
    "婚姻": r"結婚|结婚|婚姻|離婚|离婚|夫妻|妻子|丈夫|配偶|再婚|拍拖|男友|女友|男朋友|女朋友|情人|桃花|出嫁|娶|third|第三者|同性戀|同性恋|感情|單身|单身|盛女|包養|包养",
    "家庭": r"父母|父親|父亲|母親|母亲|家境|出身|兄弟|姐妹|六親|六亲|祖父|祖母|家庭|仙逝|過身|过身|遺產|遗产|舅父|養大|养大|弟弟|妹妹",
    "学业": r"學歷|学历|畢業|毕业|大學|大学|中學|中学|讀書|读书|升學|升学|學業|学业|輟學|辍学|碩士|硕士|博士|小學|小学|留學|留学|會考|会考|高考|獎學金|奖学金|進修|进修|中三|中五|中七|預科|预科",
    "事业": r"工作|職業|职业|事業|事业|創業|创业|生意|升職|升职|轉工|转工|失業|失业|打工|公司|辭職|辞职|開除|开除|經營|经营|老闆|老板|醫生|医生|會計|会计|經紀|经纪|主婦|主妇|DJ|監製|监制|從事|从事|就業|就业|散工|義工|义工",
    "财运": r"財|财|錢|钱|收入|月薪|年薪|薪金|破財|破财|保險金|保险金|投資|投资|發財|发财|富裕|貧窮|贫穷|經濟|经济|物業|物业|買樓|买楼|賣樓|卖楼|六合彩|中獎|中奖|身家|儲蓄|储蓄|破產|破产|理財|理财|純利",
    "健康": r"病|手術|手术|癌|健康|中風|中风|住院|醫院|医院|死亡|過世|去世|身亡|受傷|受伤|殘|残|失明|折斷|折断|骨折|自殺|自杀|車禍|车祸|意外|肺炎|肝炎|腫瘤|肿瘤|潰瘍|溃疡|沙士|新冠|開刀|开刀|重病|災病",
    "性格": r"性格|個性|个性|脾氣|脾气|為人|为人|品性|特質|特质|內向|内向|外向|口才|自閉|自闭|隨和|随和|克勤|揮霍|挥霍|善於交際|善于交际",
    "外貌": r"身材|外貌|相貌|樣貌|长相|容貌|高矮|胖瘦|身高|體型|体型",
    "运势": r"運程|运程|大運|大运|流年運|運勢|运势|歲運|岁运|最好的大運|運最好|运最好",
}
COMPILED = {k: re.compile(v) for k, v in RULES.items()}

# 逐条看过 95 题后，规则判错的写死在这里。多数是关键词命中了选项里的次要元素，
# 而题目问的是另一件事。
OVERRIDES = {
    "hkjfma_2010_01": "灾劫",   # 男朋友被謀殺；命中「男朋友」判婚姻，实际问的是横死
    "hkjfma_2011_02": "运势",   # 何年移民定居；对齐 MingLi 把「哪个岁运搬迁」归运势
    "hkjfma_2011_12": "家庭",   # 母親於2010年的遭遇；选项全是病伤，但问的是母亲
    "hkjfma_2011_14": "家庭",   # 弟妹同年身亡原因；与上一题(判家庭)同一命例同一件事
    "hkjfma_2012_14": "健康",   # 大病/斷腳/破產/流亡；只命中「破產」被判财运
    "hkjfma_2018_11": "事业",   # 警界际遇与处事方式；命中「出身」被判家庭
    "hkjfma_2018_12": "外貌",   # 對自己儀表的要求
    "hkjfma_2018_13": "家庭",   # 哪個大限喪父
    "hkjfma_2018_40": "婚姻",   # 現今狀況：孤獨/佛堂/丈夫子女同住/同居
}

# 唯一一条十二类都套不上的：2013 第 16 题反过来考「从人生经历推出生时辰」，
# 问的是命盘本身而不是人生的某个侧面。留空，不硬塞一个类。
NO_CATEGORY = {"hkjfma_2013_16"}

STEM_WEIGHT = 3   # 题干里的词比选项里的更能定题意


def classify(row):
    stem = row["question"]
    opts = " ".join(o["text"] for o in row["options"])
    score = Counter()
    for cat, pat in COMPILED.items():
        score[cat] = STEM_WEIGHT * len(pat.findall(stem)) + len(pat.findall(opts))
    best, n = score.most_common(1)[0]
    return best if n else None


def validate(rows):
    """How often do the rules reproduce MingLi-Bench's human label?"""
    labelled = [r for r in rows if r["source"] == "minglibench" and r.get("category")]
    hit = [r for r in labelled if classify(r) == r["category"]]
    print(f"对照 MingLi-Bench 的 {len(labelled)} 条人工标注：规则复现 {len(hit)} 条 "
          f"({len(hit) / len(labelled):.0%})")
    miss = Counter((r["category"], classify(r)) for r in labelled if classify(r) != r["category"])
    for (truth, got), n in miss.most_common(8):
        print(f"    人工 {truth} → 规则 {got}   ×{n}")
    return len(hit) / len(labelled)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    rows = json.loads(QA.read_text(encoding="utf-8"))
    agreement = validate(rows)

    # 选 HKJFMA 的行，而不是「category 为空的行」—— 后者在标签已并回题库后会变成空集，
    # 脚本就不再可重复运行了。MingLi-Bench 的标注原样保留，不覆盖。
    todo = [r for r in rows if r["source"] != "minglibench" and r["id"] not in NO_CATEGORY]
    labels = {r["id"]: OVERRIDES.get(r["id"]) or classify(r) for r in todo}
    hand = sum(1 for i in labels if i in OVERRIDES)
    print(f"\n待标注 {len(todo)} 条 · 规则判定 {len(labels) - hand} · 人工改判 {hand} "
          f"· 有意留空 {len(NO_CATEGORY)}")
    print("   " + "  ".join(f"{k}:{v}" for k, v in
                            Counter(v for v in labels.values() if v).most_common()))
    unlab = [i for i, v in labels.items() if not v]
    if unlab:
        print(f"⚠ 未能判定: {unlab}")

    if not args.check:
        # 写成独立的标签文件，由 normalize.py 合并 —— 直接改 hkjfma_qa.json 的话，
        # 下一次跑 normalize 就会把标签冲掉，两个脚本变成有顺序依赖。
        out = {i: {"category": v,
                   "source": "hand-labelled (this repo)" if i in OVERRIDES
                             else "rule-based (this repo)"}
               for i, v in sorted(labels.items()) if v}
        LABELS.write_text(json.dumps(
            {"about": f"Topic labels for the {len(out)} HKJFMA items, produced by "
                      f"scripts/categorize.py. MingLi-Bench's own labels are not repeated here; "
                      f"normalize.py takes those straight from the vendored data. Measured "
                      f"agreement between these rules and MingLi-Bench's human annotator: "
                      f"{agreement:.0%}.",
             "labels": out}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n→ {LABELS.relative_to(ROOT)}  ({len(out)} 条)")
        print("   记得再跑一次 scripts/normalize.py 把标签并进题库")
    sys.exit(0 if not unlab else 1)
