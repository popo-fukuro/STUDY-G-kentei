"""地図のデータを読み込み、描画用の形にそろえる共通モジュール。

元データ
  - data/syllabus.yml     シラバスの項目とキーワード（中分類・小分類の名前はここから取る）
  - data/curriculum.yml   講義28回の割り当て（項目ごとの講義の回とページ）
  - map/data/*.yml        地図だけの情報（分野のまとめ方、各キーワードの1文の説明、関係、試験の情報）
"""
from __future__ import annotations

import math
import re
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]          # map/
REPO = ROOT.parent
DATA = ROOT / "data"


def _load(path: Path):
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_syllabus() -> dict:
    """項目ID → {id, name, category, area, keywords} の辞書（シラバスの記載順）。"""
    syl = _load(REPO / "data" / "syllabus.yml")
    items = {}
    for field in syl["fields"]:
        for cat in field["categories"]:
            for it in cat["items"]:
                items[it["id"]] = {
                    "id": it["id"], "name": it["name"], "category": cat["name"],
                    "area": field["name"], "keywords": list(it["keywords"]),
                }
    return {"meta": syl["meta"], "items": items}


def load_curriculum() -> dict:
    """項目ID → {number, title, status, page}。"""
    cur = _load(REPO / "data" / "curriculum.yml")
    out = {}
    for lec in cur["lectures"]:
        for iid in lec.get("items", []):
            out[iid] = {"number": lec["number"], "title": lec["title"],
                        "status": lec.get("status", "planned"), "page": lec.get("page")}
    return out


def parse_extra(raw, field_id: str, item_id: str, index: int) -> dict:
    if not isinstance(raw, list) or len(raw) < 2:
        raise ValueError(f"{field_id}/{item_id} の追加用語 {index + 1} の形が不正です: {raw!r}")
    opts = raw[2] if len(raw) > 2 and isinstance(raw[2], dict) else {}
    return {"name": str(raw[0]), "desc": str(raw[1]), "sup": bool(opts.get("sup", True)),
            "aka": [str(a) for a in opts.get("aka", [])], "note": opts.get("note")}


def load_all() -> dict:
    meta = _load(DATA / "meta.yml")
    domains = _load(DATA / "domains.yml")
    rel = _load(DATA / "relations.yml")
    tables = _load(DATA / "tables.yml")
    syl = load_syllabus()
    lectures = load_curriculum()
    aliases = _load(REPO / "data" / "syllabus.yml").get("aliases", {}) or {}
    fields = []
    problems: list[str] = []
    for p in sorted((DATA / "fields").glob("*.yml")):
        f = _load(p)
        f["_file"] = p.name
        desc = f.get("desc", {}) or {}
        used_keys = set()
        subs = []
        for iid in f.get("items", []):
            it = syl["items"].get(iid)
            if it is None:
                problems.append(f"[{p.name}] シラバスにない項目ID: {iid}")
                continue
            terms = []
            for i, kw in enumerate(it["keywords"]):
                key = f"{iid}:{kw}" if f"{iid}:{kw}" in desc else kw
                text = desc.get(key)
                if text is None:
                    problems.append(f"[{p.name}] {iid}「{kw}」の説明がありません")
                    text = ""
                used_keys.add(key)
                terms.append({"id": f"{iid}-{i + 1}", "name": kw, "desc": str(text), "sup": False,
                              "aka": list(aliases.get(kw, [])), "note": None})
            for j, raw in enumerate((f.get("extra", {}) or {}).get(iid, [])):
                t = parse_extra(raw, f["id"], iid, j)
                t["id"] = f"{iid}-x{j + 1}"
                terms.append(t)
            lec = lectures.get(iid)
            subs.append({
                "id": iid, "name": it["name"],
                "short": (f.get("subShort", {}) or {}).get(iid, it["name"]),
                "category": it["category"], "area": it["area"],
                "lecture": lec, "terms": terms,
            })
        for k in desc:
            if k not in used_keys:
                problems.append(f"[{p.name}] 説明があるのにシラバスの担当項目にない語: {k}")
        f["subs"] = subs
        f.pop("desc", None)
        f.pop("extra", None)
        fields.append(f)
    fields.sort(key=lambda x: x["order"])
    return {
        "meta": meta, "domains": domains, "fields": fields,
        "themes": rel["themes"], "relations": rel["relations"], "tables": tables,
        "syllabus": syl, "_problems": problems,
    }


# ---------- 文字数・色・配置の計算（check.py と build.py の両方で使う） ----------

def zen_len(s: str) -> float:
    """全角を1、半角を0.5として数えた長さ。"""
    return sum(1.0 if unicodedata.east_asian_width(ch) in ("F", "W", "A") else 0.5 for ch in s)


def _lin(c: float) -> float:
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def card_height(layout: dict, n_subs: int) -> float:
    return layout["cardHeader"] + layout["cardPad"] + layout["cardRow"] * n_subs + layout["cardFooter"]


def card_rects(data: dict) -> list[dict]:
    """各大分類カードの中心と矩形（app.js と同じ式）。"""
    lay = data["meta"]["layout"]
    n = len(data["fields"])
    c = lay["size"] / 2
    out = []
    for i, f in enumerate(data["fields"]):
        ang = math.radians(lay["startAngle"] + 360 * i / n)
        cx, cy = c + lay["radius"] * math.cos(ang), c + lay["radius"] * math.sin(ang)
        w, h = lay["cardWidth"], card_height(lay, len(f["subs"]))
        out.append({"id": f["id"], "cx": cx, "cy": cy, "x": cx - w / 2, "y": cy - h / 2, "w": w, "h": h})
    return out


EX_RE = re.compile(r"例題Q(\d+)")


def exam_refs(text: str) -> list[str]:
    """文章中の「例題Q7」を ID（Q7）の一覧にする。"""
    return [f"Q{m.group(1)}" for m in EX_RE.finditer(text or "")]
