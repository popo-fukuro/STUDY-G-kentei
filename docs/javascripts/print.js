// 印刷・PDF化のときは、折りたたみ（確認テストの答えなど）をすべて開く
window.addEventListener("beforeprint", () => {
  document.querySelectorAll("details").forEach((d) => {
    d.dataset.wasOpen = d.open ? "1" : "0";
    d.open = true;
  });
});
window.addEventListener("afterprint", () => {
  document.querySelectorAll("details").forEach((d) => {
    if (d.dataset.wasOpen === "0") d.open = false;
  });
});
