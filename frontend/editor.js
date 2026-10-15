const editor = document.getElementById("editor");
const dropdown = document.getElementById("dropdown");

let activeIndex = 0;      // 드롭다운에서 현재 선택된 항목 번호
let candidates = [];      // 현재 검색 결과 목록
let isComposing = false;  // ⭐ 한글 IME 조합 중 여부

// IME 조합 시작/끝 감지 (한글 입력 깨짐 방지의 핵심!)
editor.addEventListener("compositionstart", () => { isComposing = true; });
editor.addEventListener("compositionend", () => {
  isComposing = false;
  handleInput();   // 조합 완료된 시점에 다시 검색
});
