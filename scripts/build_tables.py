#!/usr/bin/env python3
"""カリキュラム表・網羅チェック表を data/*.yml から作り直し、抜け漏れを検査する。

使い方:
  python scripts/build_tables.py          # 生成ファイルを書き換える＋検査結果を表示
  python scripts/build_tables.py --check  # 書き換えずに検査だけ（CI用）。問題があれば終了コード1

検査する内容:
  1. シラバスの全項目が、どれか1つの講義に割り当てられているか（重複・未割り当てなし）
  2. 公開済み（status: published）の講義ページに、担当キーワードが全部書かれているか
  3. Q&Aノートのフロントマター（syllabus / keywords）がシラバスに存在するか
  4. 生成ファイル（docs/lectures/index.md など）が最新か（--check のとき）
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DOCS = ROOT / "docs"
CURRICULUM_MD = DOCS / "lectures" / "index.md"
COVERAGE_MD = DOCS / "coverage" / "index.md"
HOME_MD = DOCS / "index.md"
NOTES_DIR = DOCS / "notes"

GEN_NOTE = "<!-- この部分は scripts/build_tables.py が自動生成する。手で編集しない。 -->"
PART_ICONS = {
    "P1": ":material-history:",
    "P2": ":material-chart-scatter-plot:",
    "P3": ":material-brain:",
    "P4": ":material-puzzle-outline:",
    "P5": ":material-rocket-launch-outline:",
    "P6": ":material-briefcase-outline:",
    "P7": ":material-scale-balance:",
    "P8": ":material-shield-account-outline:",
    "P9": ":material-flag-checkered:",
}


# ---------- 読み込み ----------

def load_yaml(path: Path):
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_syllabus():
    syl = load_yaml(DATA / "syllabus.yml")
    items = []  # 記載順
    for field in syl["fields"]:
        for cat in field["categories"]:
            for it in cat["items"]:
                items.append({
                    "id": it["id"],
                    "name": it["name"],
                    "keywords": it["keywords"],
                    "category": cat["name"],
                    "field": field["name"],
                    "field_id": field["id"],
                })
    return syl, items


def read_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm = yaml.safe_load(m.group(1)) if m else {}
    body = text[m.end():] if m else text
    return (fm or {}), body


# ---------- 照合 ----------

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).lower()
    return re.sub(r"[\s　\-‐－_・/]", "", s)  # 長音「ー」は消さない（「キー」が何にでも一致してしまうため）


def variants(kw: str, aliases: dict) -> list[list[str]]:
    """キーワードが本文にあるとみなす条件のリスト。各要素は「全部含まれていればOK」の語のリスト。"""
    out = [[kw]]
    base = re.sub(r"\s*[（(].*?[)）]\s*", "", kw).strip()
    if base and base != kw:
        out.append([base])
    inner = re.findall(r"[（(](.*?)[)）]", kw)
    for x in inner:
        out.append([x])
    if "・" in base:
        out.append([p for p in base.split("・") if p])
    for a in aliases.get(kw, []):
        out.append([a])
    return out


def keyword_in(text_n: str, kw: str, aliases: dict) -> bool:
    return any(all(norm(p) in text_n for p in cond) for cond in variants(kw, aliases))


# ---------- 集計 ----------

def collect_notes(items_by_id):
    """docs/notes/**/*.md のフロントマターから、ノートとキーワードの対応を集める。"""
    notes = []
    problems = []
    for p in sorted(NOTES_DIR.rglob("*.md")):
        if p.name == "index.md":
            continue
        fm, _ = read_frontmatter(p)
        rel = p.relative_to(DOCS).as_posix()
        title = fm.get("title", p.stem)
        syl_ids = fm.get("syllabus") or []
        kws = fm.get("keywords") or []
        for sid in syl_ids:
            if sid not in items_by_id:
                problems.append(f"ノート {rel}: syllabus に存在しない項目ID {sid}")
        all_kws = {k for it in items_by_id.values() for k in it["keywords"]}
        for k in kws:
            if k not in all_kws:
                problems.append(f"ノート {rel}: keywords の「{k}」がシラバスにない（表記を data/syllabus.yml に合わせる）")
        notes.append({"path": rel, "title": title, "syllabus": syl_ids, "keywords": kws,
                      "date": str(fm.get("date", ""))})
    return notes, problems


def analyse():
    syl, items = load_syllabus()
    aliases = syl.get("aliases") or {}
    items_by_id = {it["id"]: it for it in items}
    cur = load_yaml(DATA / "curriculum.yml")
    parts = {p["id"]: p["name"] for p in cur["parts"]}
    lectures = cur["lectures"]

    problems: list[str] = []
    warnings: list[str] = []

    # 1. 割り当て
    owner: dict[str, int] = {}
    for lec in lectures:
        for iid in lec.get("items", []):
            if iid not in items_by_id:
                problems.append(f"第{lec['number']}回: 存在しない項目ID {iid}")
            elif iid in owner:
                problems.append(f"項目 {iid} が第{owner[iid]}回と第{lec['number']}回に重複して割り当てられている")
            else:
                owner[iid] = lec["number"]
    for it in items:
        if it["id"] not in owner:
            problems.append(f"項目 {it['id']} {it['name']} がどの講義にも割り当てられていない")

    # 2. 公開済み講義の本文チェック
    covered: dict[tuple[str, str], int] = {}  # (item_id, kw) -> lecture no
    for lec in lectures:
        if lec.get("status") != "published":
            continue
        page = lec.get("page")
        if not page or not (DOCS / page).exists():
            problems.append(f"第{lec['number']}回: status が published なのにページ {page} が見つからない")
            continue
        _, body = read_frontmatter(DOCS / page)
        body_n = norm(body)
        for iid in lec.get("items", []):
            for kw in items_by_id[iid]["keywords"]:
                if keyword_in(body_n, kw, aliases):
                    covered[(iid, kw)] = lec["number"]
                else:
                    problems.append(f"第{lec['number']}回（{page}）に担当キーワード「{kw}」（{iid}）が見当たらない")

    # 3. ノート
    notes, note_problems = collect_notes(items_by_id)
    problems += note_problems

    return {
        "syl": syl, "items": items, "items_by_id": items_by_id, "parts": parts,
        "lectures": lectures, "owner": owner, "covered": covered, "notes": notes,
        "problems": problems, "warnings": warnings,
    }


# ---------- 生成 ----------

def lec_link(lec, from_dir: str) -> str:
    label = f"第{lec['number']}回"
    if lec.get("status") == "published" and lec.get("page"):
        target = Path(lec["page"]).relative_to(from_dir).as_posix() if lec["page"].startswith(from_dir + "/") \
            else "../" + lec["page"]
        return f"[{label}]({target})"
    return label


def fmt_minutes(m: int) -> str:
    h, mm = divmod(m, 60)
    if h and mm:
        return f"{h}時間{mm}分"
    if h:
        return f"{h}時間"
    return f"{mm}分"


def build_curriculum(a) -> str:
    items_by_id = a["items_by_id"]
    lectures = a["lectures"]
    total_min = sum(l["minutes"] for l in lectures)
    total_kw = sum(len(it["keywords"]) for it in a["items"])
    published = sum(1 for l in lectures if l.get("status") == "published")
    days = -(-total_min // 30)

    out = []
    out.append("---\ntitle: 講義カリキュラム\nhide:\n  - toc\n---\n")
    out.append("# 講義カリキュラム\n")
    out.append(GEN_NOTE + "\n")
    out.append('<div class="g-stats" markdown>\n')
    out.append(f'<div class="g-stat"><span class="g-stat__num">{len(lectures)}</span><span class="g-stat__label">回の講義</span></div>')
    out.append(f'<div class="g-stat"><span class="g-stat__num">{len(a["items"])}</span><span class="g-stat__label">シラバス項目</span></div>')
    out.append(f'<div class="g-stat"><span class="g-stat__num">{total_kw}</span><span class="g-stat__label">キーワード</span></div>')
    out.append(f'<div class="g-stat"><span class="g-stat__num">約{round(total_min / 60)}h</span><span class="g-stat__label">学習時間の目安</span></div>')
    out.append("\n</div>\n")
    out.append(
        f"シラバス{a['syl']['meta']['version']}版（{a['syl']['meta']['version_date']}）の全{len(a['items'])}項目・"
        f"{total_kw}キーワードを、全{len(lectures)}回に**重複なく**割り当てている。"
        f"1日30分なら約{days}日（講義を読む＋確認テスト）。公開済み：**{published}/{len(lectures)}回**。\n"
    )
    out.append('!!! tip "進め方"\n'
               '    - 講義は「次の資料作って」と言われたときに1回ずつ作る。\n'
               '    - 目安時間は「講義を読む＋確認テスト」。1日30分なら、60分の回は2日、120分の回は4日で進める。\n'
               '    - キーワードごとの担当回と進み具合は [網羅チェック表](../coverage/index.md) で確認できる。\n')

    cur_part = None
    for lec in lectures:
        if lec["part"] != cur_part:
            cur_part = lec["part"]
            pmins = sum(l["minutes"] for l in lectures if l["part"] == cur_part)
            icon = PART_ICONS.get(cur_part, "")
            out.append(f"\n## {icon} {a['parts'][cur_part]}\n")
            out.append(f'<p class="g-part-meta">この部の目安：{fmt_minutes(pmins)}</p>\n')
            out.append("| 回 | テーマ | 担当するシラバス項目 | 語数 | 目安 | 状態 |")
            out.append("|:-:|---|---|:-:|:-:|:-:|")
        if lec.get("review"):
            item_txt = "全範囲（総復習）"
            nkw = "—"
        else:
            item_txt = "<br>".join(f"`{i}` {items_by_id[i]['name']}" for i in lec["items"])
            nkw = str(sum(len(items_by_id[i]["keywords"]) for i in lec["items"]))
        status = "✅ 公開" if lec.get("status") == "published" else "⬜ 未作成"
        out.append(f"| {lec_link(lec, 'lectures')} | **{lec['title']}**<br><small>{lec['focus']}</small> | "
                   f"{item_txt} | {nkw} | {fmt_minutes(lec['minutes'])} | {status} |")

    out.append("\n## 各回の担当キーワード\n")
    out.append("タップで開く。講義を作るときは、ここに並ぶ語を**1つ残らず**扱う。\n")
    for lec in lectures:
        if lec.get("review"):
            continue
        kws_lines = []
        for i in lec["items"]:
            it = items_by_id[i]
            kws_lines.append(f"    - **{i} {it['name']}**：" + "、".join(it["keywords"]))
        n = sum(len(items_by_id[i]["keywords"]) for i in lec["items"])
        out.append(f'??? note "第{lec["number"]}回 {lec["title"]}（{n}語）"')
        out.extend(kws_lines)
        out.append("")
    return "\n".join(out) + "\n"


def build_coverage(a) -> str:
    items = a["items"]
    owner = a["owner"]
    covered = a["covered"]
    lectures_by_no = {l["number"]: l for l in a["lectures"]}
    meta = a["syl"]["meta"]

    # ノート索引 (item_id, kw) -> [notes]
    note_map: dict[tuple[str, str], list] = {}
    for n in a["notes"]:
        for k in n["keywords"]:
            for it in items:
                if k in it["keywords"] and (not n["syllabus"] or it["id"] in n["syllabus"]):
                    note_map.setdefault((it["id"], k), []).append(n)

    total = sum(len(it["keywords"]) for it in items)
    done = len(covered)
    pct = round(done * 100 / total) if total else 0
    noted = len(note_map)

    out = []
    out.append("---\ntitle: 網羅チェック表\nhide:\n  - toc\n---\n")
    out.append("# 網羅チェック表\n")
    out.append(GEN_NOTE + "\n")
    out.append(
        f"JDLA「G検定 試験出題範囲（シラバス2024）」**第{meta['version']}版（{meta['version_date']}）**の"
        f"全キーワードと、それを扱った講義・Q&Aノートの対応表。"
        f"（シラバス確認日：{meta['checked_on']}／出典：[JDLA シラバス配布ページ]({meta['source_url']})）\n"
    )
    out.append('<div class="g-stats" markdown>\n')
    out.append(f'<div class="g-stat"><span class="g-stat__num">{total}</span><span class="g-stat__label">キーワード</span></div>')
    out.append(f'<div class="g-stat"><span class="g-stat__num">{done}</span><span class="g-stat__label">講義で学習済み</span></div>')
    out.append(f'<div class="g-stat"><span class="g-stat__num">{pct}%</span><span class="g-stat__label">網羅率</span></div>')
    out.append(f'<div class="g-stat"><span class="g-stat__num">{noted}</span><span class="g-stat__label">ノートあり</span></div>')
    out.append("\n</div>\n")
    out.append(f'<div class="g-progress" style="--p:{pct}%"><span></span></div>\n')
    out.append('!!! info "見かた"\n'
               '    - **担当**：その語を扱う予定の講義回。講義が公開されるとリンクになる。\n'
               '    - **講義**：✅＝公開済みの講義本文で扱った（スクリプトで本文を照合して確認）／⬜＝まだ。\n'
               '    - **Q&Aノート**：その語を解説したノートへのリンク。\n'
               '    - 同じ語が複数の項目に出てくるもの（勾配消失問題、事前学習、PoC など）は、シラバスどおり項目ごとに数えている。\n'
               '    - シラバスの明らかな誤記は正式名に直して載せている（例：RandAugument → RandAugment）。\n')

    # 分野別の進み具合
    out.append("## 分野ごとの進み具合\n")
    out.append("| 大項目 | 項目 | 語数 | 学習済み | 網羅率 |")
    out.append("|---|:-:|:-:|:-:|:-:|")
    cats = []
    for it in items:
        key = (it["field"], it["category"])
        if key not in cats:
            cats.append(key)
    for f, c in cats:
        its = [it for it in items if it["category"] == c and it["field"] == f]
        n = sum(len(it["keywords"]) for it in its)
        d = sum(1 for it in its for k in it["keywords"] if (it["id"], k) in covered)
        out.append(f"| {c}（{f}） | {len(its)} | {n} | {d} | {round(d * 100 / n)}% |")
    out.append("")

    cur_field = None
    cur_cat = None
    for it in items:
        if it["field"] != cur_field:
            cur_field = it["field"]
            out.append(f"\n## {cur_field}\n")
        if it["category"] != cur_cat:
            cur_cat = it["category"]
            out.append(f"\n### {cur_cat}\n")
            out.append("| 項目 | キーワード | 担当 | 講義 | Q&Aノート |")
            out.append("|---|---|:-:|:-:|---|")
        lec_no = owner.get(it["id"])
        lec = lectures_by_no.get(lec_no) if lec_no else None
        for idx, kw in enumerate(it["keywords"]):
            item_cell = f"`{it['id']}` {it['name']}" if idx == 0 else ""
            lec_cell = lec_link(lec, "coverage") if lec else "**未割当**"
            done_cell = "✅" if (it["id"], kw) in covered else "⬜"
            notes = note_map.get((it["id"], kw), [])
            note_cell = "<br>".join(f"[{n['title']}](../{n['path']})" for n in notes)
            out.append(f"| {item_cell} | {kw} | {lec_cell} | {done_cell} | {note_cell} |")
    return "\n".join(out) + "\n"


def build_home_progress(a) -> str:
    total = sum(len(it["keywords"]) for it in a["items"])
    done = len(a["covered"])
    pct = round(done * 100 / total) if total else 0
    pub = sum(1 for l in a["lectures"] if l.get("status") == "published")
    n_lec = len(a["lectures"])
    return (
        f"{GEN_NOTE}\n"
        f'<div class="g-progress-card" markdown>\n'
        f'<div class="g-progress-card__row"><span>講義</span><strong>{pub} / {n_lec} 回</strong></div>\n'
        f'<div class="g-progress" style="--p:{round(pub * 100 / n_lec)}%"><span></span></div>\n'
        f'<div class="g-progress-card__row"><span>キーワード網羅</span><strong>{done} / {total} 語（{pct}%）</strong></div>\n'
        f'<div class="g-progress" style="--p:{pct}%"><span></span></div>\n'
        f'<div class="g-progress-card__row"><span>Q&Aノート</span><strong>{len(a["notes"])} ページ</strong></div>\n'
        f"</div>\n"
    )


def replace_block(text: str, start: str, end: str, new: str) -> str:
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pat.search(text):
        raise SystemExit(f"マーカー {start} が {HOME_MD} に見つからない")
    return pat.sub(lambda _: f"{start}\n{new}{end}", text)


def main():
    check_only = "--check" in sys.argv
    a = analyse()
    outputs = {
        CURRICULUM_MD: build_curriculum(a),
        COVERAGE_MD: build_coverage(a),
    }
    home = HOME_MD.read_text(encoding="utf-8")
    outputs[HOME_MD] = replace_block(home, "<!-- progress:start -->", "<!-- progress:end -->",
                                     build_home_progress(a))

    stale = []
    for path, content in outputs.items():
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        if old != content:
            stale.append(path.relative_to(ROOT).as_posix())
            if not check_only:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

    total = sum(len(it["keywords"]) for it in a["items"])
    print(f"シラバス：{len(a['items'])}項目／{total}キーワード（項目×キーワードの組）")
    print(f"講義：{len(a['lectures'])}回（公開済み {sum(1 for l in a['lectures'] if l.get('status') == 'published')}回）")
    print(f"講義で学習済みのキーワード：{len(a['covered'])}／{total}")
    print(f"Q&Aノート：{len(a['notes'])}ページ")

    problems = list(a["problems"])
    if check_only and stale:
        problems += [f"生成ファイルが古い：{s}（python scripts/build_tables.py を実行して commit する）" for s in stale]
    elif stale:
        print("更新したファイル：" + "、".join(stale))

    if problems:
        print("\n❌ 問題があります：")
        for p in problems:
            print("  - " + p)
        sys.exit(1)
    print("\n✅ 抜け漏れ・重複なし")


if __name__ == "__main__":
    main()
