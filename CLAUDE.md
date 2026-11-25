# G検定 合格ラボ：作業ルール

G検定（JDLA Deep Learning for GENERAL）合格のための学習サイト。MkDocs Material で作り、GitHub Actions で GitHub Pages に自動公開する。
公開URL：https://popo-fukuro.github.io/STUDY-G-kentei/

## 目的

- 市販テキストを使わず、**このサイトの講義資料とQ&Aノートだけで合格する**。講義は「これを読めば合格できる」品質が最優先。
- 見た目は「Canvaで作ったような」整った資料。**文字より図が主役**。サイト全体で色・フォント・アイコン・図のスタイルを統一する。
- スマホで読みやすく、PDFにしても崩れないこと。

## サイトの構成

```
data/syllabus.yml        シラバス2024 第1.4版の全55項目・495キーワード（唯一の元データ）
data/curriculum.yml      講義28回の割り当て（項目ID・目安時間・状態・ページ）
scripts/build_tables.py  カリキュラム表・網羅チェック表・ホームの進み具合を生成し、抜け漏れを検査
docs/index.md            ホーム（進み具合は自動生成ブロック）
docs/guide/              試験ガイド（index.md）・学習計画（study-plan.md）
docs/lectures/           講義。index.md は自動生成のカリキュラム表。講義ページは NN-slug.md
docs/notes/              Q&Aノート。index.md は大項目ごとの一覧（手で更新）
docs/coverage/index.md   網羅チェック表（自動生成。手で編集しない）
docs/quiz/index.md       一問一答
docs/assets/images/      図（lectures/NN/、notes/、common/）
docs/stylesheets/extra.css  デザインシステム（色・部品）
templates/               講義とノートのひな形
docs/map/index.html      試験範囲マップ（自動生成。map/ のデータから作る。手で編集しない）
map/                     試験範囲マップのデータ（data/）・画面の部品（src/）・生成と検査の道具（tools/）・調査メモ（research/）
```

**自動生成ファイル（`docs/lectures/index.md`、`docs/coverage/index.md`、`docs/index.md` の進み具合ブロック）は手で編集しない。** `data/*.yml` を直して `python scripts/build_tables.py` を実行する。CI は `--check` で、生成ファイルが古い・担当キーワードが本文にない・項目の割り当て漏れがある場合に公開を止める。

### 試験範囲マップ（`docs/map/index.html`）

シラバスの全範囲を17分野の放射状の地図で示す単体のHTML。中分類（シラバスの55項目）と用語（全キーワード）は `data/syllabus.yml` から、講義の回は `data/curriculum.yml` から自動で読み込む。

- 直すのは `map/data/*.yml`（分野のまとめ方・各キーワードの1文の説明・関係・試験の情報）と `map/src/` だけ。`docs/map/index.html` は生成物なので直接編集しない。
- **シラバスを改訂したら**、`python map/tools/check.py` が「説明のないキーワード」「どの分野にも入っていない項目」を教えてくれるので、`map/data/fields/*.yml` の `items` と `desc` を直す。
- **講義を公開したら**（`curriculum.yml` を `published` にしたら）、地図の項目からその講義にリンクが張られるので、作り直してコミットする。
- 試験日程などを更新するときは、先に `map/research/` に調査メモ（出典URLと確認日つき）を書き、`map/data/meta.yml` の `created` と `researchMemo` を合わせる。確かめられないことは「未確認」と書く。
- 優先度の根拠は「JDLA公式の例題」「シラバス2024の改訂ポイント」「キーワード数」だけで書き、出題頻度を断定しない。
- 直したら次を実行し、生成物もいっしょにコミットする。
  ```bash
  python map/tools/check.py               # データの整合性・カードの重なり・調査メモとの照合
  python map/tools/build.py               # docs/map/index.html を作り直す
  node map/tools/screenshot.mjs <出力先>   # スクリーンショットと表示の自動チェック（Playwright）
  ```

---

## 講義を作る手順（毎回必ず守る）

持ち主が「次の資料作って」「第〇回を作って」と言ったときに、**1回分だけ**作る。先回りしてまとめて作らない。

1. **担当範囲を確認**：`data/curriculum.yml` でその回の `items` を確認し、`docs/lectures/index.md` の「各回の担当キーワード」で語を全部書き出す。`docs/coverage/index.md` で、前の回やノートで既に扱った語との関係も見る。
2. **調査**：キーワードごとに一次情報を優先して調べる（JDLAのシラバス・例題、原論文、提供元の公式ドキュメント、官公庁の資料）。法律・ガイドライン・生成AI・最新モデルなど変わりやすいものは**必ずWeb検索で最新状況を確認**してから書く。古い知識で書かない。
3. **執筆**：`templates/lecture-template.md` をコピーして `docs/lectures/NN-<英小文字とハイフンのslug>.md`（NN は2桁）を作る。キーワードごとに **定義・仕組み・具体例・似た用語との違い・試験での問われ方** まで書く。**人名・年号・モデル名・数値は特に正確に**（出典で確認したものだけ書く）。
4. **図を描く**：全体像の図は必須。キーワードごとにも図を入れる（下の「図のルール」）。
5. **自己チェック**（全部満たすまで公開しない）
    - [ ] 担当キーワードを**全部**扱ったか（`build_tables.py` が本文を照合する。照合は表記ゆれに甘いので、目でも確認する）
    - [ ] 事実（人名・年号・数値・モデル名・法律の条文や日付）を出典で確かめたか
    - [ ] 前の講義・ノートと矛盾がないか（用語の訳し方・説明のしかたを揃える）
    - [ ] 確認テストの答えと解説が本文と一致しているか
    - [ ] スマホ幅（約400px）で表や図が崩れないか
6. **登録**：`data/curriculum.yml` のその回を `status: published`、`page: lectures/NN-slug.md` に変える。`mkdocs.yml` の `nav` の「講義」に追加する（パートごとの見出しの下に）。
7. **一問一答**：`docs/quiz/index.md` に、その回の重要語の一問一答を追加する。
8. **ホーム**：`docs/index.md` の「最近の更新」の**一番上**に日付付きで追加。学習計画（`docs/guide/study-plan.md`）の記録表も更新。
9. **生成と確認**：`python scripts/build_tables.py` → `mkdocs build --strict` が警告なしで通ることを確認。
10. **公開**：`main` にコミットして push（GitHub Actions が自動公開）。チャットには **要点3〜5行とページのURL** だけ返す。

### 講義の構成（この順番・見出し名で固定）

| # | 見出し | 中身 |
|---|---|---|
| 0 | ヒーローバナー | `g-hero g-hero--pN`。第N回・パート名・テーマ・リード文・チップ（項目ID、目安時間、語数） |
| 1 | 今日のゴール | `g-goal` カード。3〜5行。「説明できる／答えられる／計算できる」で終える |
| 2 | 全体像 | 今日の語の関係を1枚にしたオリジナルSVG＋読み方2〜3行 |
| 3 | 本題 | キーワードごとに `### 語` → `g-kw` カード（ひとことで）→ 仕組み（図）→ 具体例 → 似た用語との違い（`g-compare` 表）→ `point` 囲み（問われ方） |
| 4 | 身近な具体例 | `life` 囲み。今日の語をまとめて日常の話にたとえる |
| 5 | 試験に出るポイントとひっかけ | `point`（必ず覚える）・`trap`（ひっかけ）・`memory`（覚え方） |
| 6 | まとめ：覚えるべき用語 | `g-summary` 表（用語／ひとことで／セットで覚える）。担当キーワードを全部並べる |
| 7 | 確認テスト | 5〜10問。本番と同じ4択（選択肢は1〜4）。`g-quiz` カード＋`??? success` の折りたたみに答えと全選択肢の解説 |
| 8 | 参考資料 | 一次情報の一覧（著者・年・タイトル・URL）。図は転載しない |

- **分量は削らない**。必要な知識は全部入れ、見出し・図・表で読みやすくする。
- **数式は避けずに載せる**が、`formula` 囲みの中で**直感的な意味を先に**言葉で書き、そのあと数式、最後に記号の説明。
- 専門用語は初めて出たところで簡単に説明する。中学生でも追える言葉で。
- 試験の「似た用語の区別」「人名・年号」「計算」を意識して書く。
- フロントマターの `tags` は「講義」「大項目名（シラバス表記）」「頻出」の組み合わせ。既存タグに揃える（`docs/tags.md` で確認）。

---

## Q&Aノートを作る手順

質問されたら、その解説をQ&Aノートとして1ページ作る。一言で済む確認はチャットだけでOK。迷ったら「ページにする？」と聞く。

1. `templates/note-template.md` をもとに `docs/notes/<英小文字とハイフンのslug>.md` を作る。
2. フロントマターの `syllabus`（項目ID）と `keywords`（`data/syllabus.yml` と**同じ表記**のキーワード）を必ず書く。網羅チェック表の「Q&Aノート」列に自動で載る。
3. 型（この順番で固定）：**1 結論をひとことで → 2 身近なたとえ話 → 3 図解（流れはMermaid、構成図・イラストはオリジナルSVG）→ 4 仕組みを①→②→③で（`g-steps`）→ 5 似た用語との比較表（`g-compare`）→ 6 試験での出方とひっかけ → 7 参考になる外部資料（リンクと見どころだけ）→ 8 確認ミニ問題（答えは折りたたみ）**
4. `docs/notes/index.md` の該当する大項目の下にリンクを追加（「まだノートはありません」は消す）。`mkdocs.yml` の `nav` の「Q&Aノート」にも追加。関係する講義ページの末尾（参考資料の前）に「関連ノート」としてリンクしてもよい。
5. ホームの「最近の更新」に追加 → `python scripts/build_tables.py` → `mkdocs build --strict` → `main` に push。チャットには要点3〜5行とURL。

---

## デザインルール

### 配色（`docs/stylesheets/extra.css` の変数だけを使う）

| 役割 | 変数 | 色 | 使いどころ |
|---|---|---|---|
| メイン | `--g-indigo` | `#4F5BD5` | 見出しの帯、リンク、基本のアクセント |
| 相方 | `--g-violet` | `#8B5CF6` | グラデーション、数式の囲み |
| 見出し文字 | `--g-navy` | `#1F2A5C` | 見出し・強調文字 |
| 正解・ゴール | `--g-teal` | `#12A594` | 今日のゴール、まとめ、正解 |
| 試験ポイント | `--g-amber` | `#F5A524` | point 囲み、確認テスト、マーカー |
| 注意・ひっかけ | `--g-coral` | `#F2645A` | trap 囲み、NG例 |
| 補足・具体例 | `--g-sky` | `#2E9BEA` | life 囲み、補足 |
| 覚え方 | `--g-pink` | `#E0457B` | memory 囲み |
| 最新動向 | `--g-steel` | `#3B6E8F` | news 囲み |
| 文字・線 | `--g-ink` `#2B2F3A` ／ `--g-muted` `#6B7280` ／ `--g-line` `#E3E6EF` | | |

淡い背景は各色の `-50`（例：`--g-indigo-50` `#EEF0FF`）。ダークモードは CSS が自動で置き換える。

**パート色**（バナーと図のアクセント）：P1 sky／P2 teal／P3 indigo／P4 violet／P5 coral／P6 amber／P7 steel／P8 green／P9 pink。講義のバナーは `g-hero--p1`〜`g-hero--p9` をパートに合わせる。

### フォント

- 本文：Noto Sans JP（`mkdocs.yml` の `theme.font`）。コード：JetBrains Mono。
- 見出し：M PLUS Rounded 1c（丸ゴシック。CSSで指定済み）。
- 図（SVG）：`font-family="'M PLUS Rounded 1c','Hiragino Sans','Noto Sans JP','Yu Gothic',sans-serif"`。

### 部品（クラス名と用途）

見本は `docs/lectures/style-guide.md`（サイトの「講義 › デザイン見本」）。新しい部品を作りたくなったら、まず既存の部品で表せないか考え、作るなら extra.css と見本ページの両方に追加する。

| 部品 | 書き方 | 用途 |
|---|---|---|
| ヒーローバナー | `<div class="g-hero g-hero--pN" markdown>` | 講義・ガイドの冒頭 |
| チップ | `<span class="g-chip">`（`--teal` `--coral` `--amber` `--sky` `--violet`） | 項目ID・時間・頻出度 |
| 今日のゴール | `<div class="g-goal" markdown>`（1行目がタイトル、続けて箇条書き） | ゴール・結論 |
| キーワードカード | `<div class="g-kw" markdown>` ＋ `g-kw__head`／`g-kw__id`／`g-kw__def` | 本題の各キーワードの頭 |
| 手順 | `<div class="g-steps" markdown>` の中に番号付きリスト | 仕組みを①→②→③で |
| 比較表 | `<div class="g-compare" markdown>` の中に表（1列目が観点） | 似た用語との違い |
| まとめ表 | `<div class="g-summary" markdown>` の中に表 | 覚えるべき用語の一覧 |
| 問題カード | `<div class="g-quiz" markdown>`＋直後に `??? success "答えと解説（タップで開く）"` | 確認テスト |
| 数字カード | `g-stats`／`g-stat` | 統計（生成スクリプトが使用） |
| 図 | `<figure markdown>` ＋ `![説明](パス)` ＋ `<figcaption>図：…</figcaption>` | SVGの図 |

### 囲み（admonition）の使い分け

| 種類 | 用途 | 例 |
|---|---|---|
| `!!! point` | 試験ではこう出る／必ず覚える | 人名・年号・数値 |
| `!!! trap` | ひっかけ注意 | 間違えやすい選択肢 |
| `!!! life` | 身近な具体例・たとえ話 | |
| `!!! formula` | 数式（直感 → 式 → 記号の説明） | |
| `!!! memory` | 覚え方・語呂合わせ | |
| `!!! news` | 最新動向（**確認日を必ず書く**） | 法律・ガイドライン・最新モデル |
| `!!! goal` | 結論 | |
| `!!! info` / `!!! tip` | 補足 | |
| `??? success` | 答えと解説（折りたたみ） | 確認テスト |

1つの節に囲みを3つ以上続けない（読みにくくなる）。

### 図のルール

- **すべてオリジナル**。参考書・Webの図をトレースしない。
- 流れ・手順・時系列は **Mermaid**（`flowchart`、`sequenceDiagram`、`timeline`、`gantt` など）。構成図・概念図・イラスト・グラフは **オリジナルSVG**。
- SVGの置き場所：`docs/assets/images/lectures/NN/<内容>.svg`（講義）、`docs/assets/images/notes/<slug>-<内容>.svg`（ノート）、共通は `common/`。ファイル名は英小文字とハイフン。
- SVGの書き方（`docs/assets/images/common/lecture-flow.svg` が見本）
    - `viewBox="0 0 800 H"`（横800を基準、`width`/`height` 属性は付けない）。スマホでも読めるよう、**文字は14px以上、見出しは18〜22px**。1枚に詰め込みすぎない（要素は8個くらいまで）。
    - **背景を必ず塗る**（角丸24の `#F7F8FC`→`#EEF0FF` のグラデーション、または白）。ダークモードでも読めるようにするため。
    - カードは白・角丸16・薄い影（`feDropShadow` 不透明度0.10）・上に色の帯（高さ8）。番号は色付きの円＋白文字。
    - 色は上の配色表の値だけ。1枚で使うアクセント色は3色まで。矢印は `#9AA2CC`、太さ3。
    - `<title>` と `<desc>`（図の内容を文章で説明）を必ず入れ、`role="img"` と `aria-labelledby` を付ける。
    - 文字がカードからはみ出していないか、`rsvg-convert` などでPNGにして確認する。
- Mermaid は `classDef` で配色表の色に合わせてよい。ノードの文字は短く（10文字前後）。

### 表・数式・その他

- 表は列を増やしすぎない（スマホで4列まで目安）。長い説明は表の外に出す。
- 数式は `$$ … $$`（ブロック）／`\( … \)`（文中）。KaTeX で描画される。
- 強調は `**太字**`、本当に大事な所だけ `==マーカー==`。
- 絵文字は控えめに（チップの ⏱ 程度）。アイコンは Material のアイコン（`:material-…:`）を使う。
- 印刷・PDF：折りたたみは印刷時に自動で開く（`print.js`）。カード・図・表は途中で改ページしないよう CSS 済み。

---

## 正確さのルール

- 内容は JDLA 公式の最新シラバス（現在は **シラバス2024 第1.4版、2026-05-11**）に沿わせる。講義とノートには必ずシラバスの項目IDを紐づける。
- 試験日程・シラバス・法律・ガイドライン・生成AIなどの最新動向は、**書く前に必ずWeb検索で確認**。確認日をページに書く。
- シラバスが改訂されたら：`data/syllabus.yml` を更新 → `data/curriculum.yml` の割り当てを見直す → `build_tables.py` で抜け漏れを確認 → 試験ガイドの改訂履歴を更新。
- 出典は一次情報を優先（JDLA、論文、公式ドキュメント、官公庁）。二次情報しかないときはそう書く。

## 著作権のルール（公開が前提なので厳守）

- 参考書・問題集・Webの**文章・図・問題を写さない**。自分の言葉で書き、図はオリジナルで描く。
- Webの図や画像を保存して載せない。わかりやすい図は「参考資料」にリンクと見どころだけ書く。
  - 例外：ライセンスで再利用が許されているもの（Wikimedia Commons など）は、出典とライセンスを書いて載せてよい。
- JDLA公式の例題などを扱うときは、出典を明記し、問題文をそのまま転載しない（要旨と解説にとどめる）。
- 実在の人物の写真は載せない。

## 書き方・話し方

- サイトの文章は「〜する」「〜だ」調。やさしい言葉で、正確に。
- チャットの返事はスマホで読むので短く（要点3〜5行＋URL）。「もっと詳しく」と言われたら深掘りする。
- 持ち主が間違って覚えていそうなところは遠慮なく指摘する。

## ローカルで確認する

```bash
pip install -r requirements.txt
python scripts/build_tables.py   # 表を生成して抜け漏れを検査
mkdocs serve                     # http://127.0.0.1:8000
mkdocs build --strict            # 警告ゼロを確認
```

GitHub Pages の公開元は、リポジトリの Settings › Pages › Source を「GitHub Actions」にしておく。
