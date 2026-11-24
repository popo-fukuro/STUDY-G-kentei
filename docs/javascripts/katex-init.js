// 数式（pymdownx.arithmatex の generic 出力）を KaTeX で描画する
document$.subscribe(({ body }) => {
  if (typeof renderMathInElement !== "function") return;
  renderMathInElement(body, {
    delimiters: [
      { left: "$$", right: "$$", display: true },
      { left: "$", right: "$", display: false },
      { left: "\\(", right: "\\)", display: false },
      { left: "\\[", right: "\\]", display: true },
    ],
  });
});
