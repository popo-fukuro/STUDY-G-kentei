# G検定 合格ラボ

G検定（JDLA Deep Learning for GENERAL）合格のための自分専用の学習サイト。
シラバス2024 第1.4版の全55項目・495キーワードを、全28回の講義とQ&Aノートで学ぶ。

- 公開サイト：https://popo-fukuro.github.io/STUDY-G-kentei/
- 作り方・デザインのルール：[CLAUDE.md](CLAUDE.md)

## 構成

| 場所 | 内容 |
|---|---|
| `data/syllabus.yml` | シラバスの全キーワード（元データ） |
| `data/curriculum.yml` | 講義28回の割り当て |
| `scripts/build_tables.py` | カリキュラム表・網羅チェック表の生成と抜け漏れ検査 |
| `docs/` | サイトの中身（MkDocs Material） |
| `templates/` | 講義・Q&Aノートのひな形 |
| `map/` | 試験範囲マップ（データ・画面の部品・生成と検査の道具・調査メモ）。生成物は `docs/map/index.html` |

## ローカルで確認

```bash
pip install -r requirements.txt
python scripts/build_tables.py
mkdocs serve
```

`main` に push すると GitHub Actions がビルドして GitHub Pages に公開する。

解説・図はすべてオリジナル。外部の資料はリンクと出典で紹介している。
