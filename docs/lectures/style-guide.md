---
title: デザイン見本
description: 講義・Q&Aノートで使う部品の見本。デザインを揃えるための確認用ページ（学習内容ではない）。
hide:
  - navigation
---

<div class="g-hero g-hero--p3" markdown>
<span class="g-hero__eyebrow">第N回 ｜ パート名（見本）</span>

# デザイン見本

講義とQ&Aノートで使う部品をまとめたページ。**学習内容ではなく、見た目を揃えるための見本**。
部品の書き方は `templates/` と `CLAUDE.md` を見る。

<div class="g-chips">
<span class="g-chip">T00 項目名</span>
<span class="g-chip">⏱ 目安60分</span>
<span class="g-chip">キーワード00語</span>
</div>
</div>

## 講義1回分の流れ

すべての講義はこの順番で並べる。

<figure markdown>
![講義1回分の流れ。ゴール、全体像、本題、具体例、試験ポイント、まとめ、確認テスト、参考資料の8ステップ](../assets/images/common/lecture-flow.svg)
<figcaption>図：講義1回分の流れ（オリジナルSVGの見本）</figcaption>
</figure>

## パートごとのバナー色

<div class="g-hero g-hero--mini g-hero--p1" markdown><span class="g-hero__eyebrow">P1</span> AIの全体像と歴史</div>
<div class="g-hero g-hero--mini g-hero--p2" markdown><span class="g-hero__eyebrow">P2</span> 機械学習</div>
<div class="g-hero g-hero--mini g-hero--p3" markdown><span class="g-hero__eyebrow">P3</span> ディープラーニングの基礎</div>
<div class="g-hero g-hero--mini g-hero--p4" markdown><span class="g-hero__eyebrow">P4</span> ディープラーニングの要素技術</div>
<div class="g-hero g-hero--mini g-hero--p5" markdown><span class="g-hero__eyebrow">P5</span> ディープラーニングの応用例</div>
<div class="g-hero g-hero--mini g-hero--p6" markdown><span class="g-hero__eyebrow">P6</span> 社会実装と数理・統計</div>
<div class="g-hero g-hero--mini g-hero--p7" markdown><span class="g-hero__eyebrow">P7</span> AIに関する法律と契約</div>
<div class="g-hero g-hero--mini g-hero--p8" markdown><span class="g-hero__eyebrow">P8</span> AI倫理・AIガバナンス</div>
<div class="g-hero g-hero--mini g-hero--p9" markdown><span class="g-hero__eyebrow">P9</span> 総仕上げ</div>

## 今日のゴール

<div class="g-goal" markdown>
この回が終わったら、こう言えればOK

- ゴールは3〜5行
- 「説明できる」「答えられる」「計算できる」で終える
- 試験で問われる形に合わせる
</div>

## キーワードカード

### サンプル用語

<div class="g-kw" markdown>
<div class="g-kw__head">サンプル用語<span class="g-kw__id">T00</span></div>

<p class="g-kw__def"><strong>ひとことで：</strong>定義を1文で書く場所。ここだけ読めば意味がわかるように。</p>
</div>

**仕組み**：直感的な説明 → 図 → くわしい説明の順に書く。

## 手順（①→②→③）

<div class="g-steps" markdown>

1. **ステップ1**：最初に起きること
2. **ステップ2**：次に起きること
3. **ステップ3**：結果

</div>

## 流れ図（Mermaid）

```mermaid
flowchart LR
  A([データ]) --> B[学習] --> C[(モデル)] --> D([予測])
```

## 数式

!!! formula "数式で見ると"
    先に「何を表しているか」を言葉で書いてから、数式を載せる。例：平均は「全部足して個数で割る」。

    $$
    \bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i
    $$

## 囲みの種類

!!! goal "goal：ゴール・結論"
    結論やゴールを示すとき。

!!! point "point：試験ではこう出る"
    出題パターン・必ず覚える数値や名前。

!!! trap "trap：ひっかけ注意"
    間違えやすい選択肢と理由。

!!! life "life：身近な具体例"
    日常のたとえ話。

!!! memory "memory：覚え方"
    語呂合わせ・セットで覚えるコツ。

!!! news "news：最新動向"
    法律・ガイドライン・モデルの最新情報（確認日を書く）。

!!! info "info：補足"
    本筋から外れる補足。

## 比較表（似た用語との違い）

<div class="g-compare" markdown>

| | 用語A | 用語B |
|---|---|---|
| ひとことで | 〇〇する | △△する |
| 目的 | | |
| 例 | | |

</div>

## まとめ表

<div class="g-summary" markdown>

| 用語 | ひとことで | セットで覚える |
|---|---|---|
| 用語A | 定義 | 用語B |

</div>

## 確認テスト

<div class="g-quiz" markdown>
**問1** 見本の問題文。最も適切なものを1つ選べ。

1. 選択肢
2. 選択肢
3. 選択肢
4. 選択肢
</div>

??? success "答えと解説（タップで開く）"
    **正解：2**

    - 1：違う理由
    - 2：正しい理由
    - 3：違う理由
    - 4：違う理由

## チップと強調

<div class="g-chips">
<span class="g-chip">indigo</span>
<span class="g-chip g-chip--teal">teal</span>
<span class="g-chip g-chip--coral">coral</span>
<span class="g-chip g-chip--amber">amber</span>
<span class="g-chip g-chip--sky">sky</span>
<span class="g-chip g-chip--violet">violet</span>
</div>

文中の==マーカー強調==は、本当に大事な所だけに使う。
