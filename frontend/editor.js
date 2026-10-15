//🔹 블록 A: 상태 변수 & IME 플래그

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

// 🔹 블록 B: 초성 변환 (JS 버전)

const CHOSUNG = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ',
                 'ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'];

// 한글 → 초성 변환 (백엔드와 동일한 588 공식)
function getChosung(str) {
  let result = "";
  for (const ch of str) {
    const code = ch.charCodeAt(0);
    if (code >= 0xAC00 && code <= 0xD7A3) {
      result += CHOSUNG[Math.floor((code - 0xAC00) / 588)];
    } else {
      result += ch;
    }
  }
  return result;
}

// 초성만으로 이뤄졌는지 판별
function isChosungOnly(str) {
  return str.length > 0 && [...str].every(ch => CHOSUNG.includes(ch));
}

// 검색: 초성 or 접두 매칭
function searchLearners(query) {
  if (!query) return [];
  if (isChosungOnly(query)) {
    return LEARNERS.filter(l => getChosung(l.name).startsWith(query));
  }
  return LEARNERS.filter(l => l.name.startsWith(query));
}

// 🔹 블록 C: 입력 감지 & 드롭다운 표시

// @ 뒤 토큰 추출용 정규식 (커서 직전 텍스트에서)
const TRIGGER_RE = /@([가-힣ㄱ-ㅎa-zA-Z]*)$/;

function getTextBeforeCursor() {
  const sel = window.getSelection();
  if (sel.rangeCount === 0) return "";
  const range = sel.getRangeAt(0);
  // 커서 위치까지의 텍스트만 추출
  const preRange = range.cloneRange();
  preRange.selectNodeContents(editor);
  preRange.setEnd(range.endContainer, range.endOffset);
  return preRange.toString();
}

function handleInput() {
  if (isComposing) return;   // 조합 중이면 보류

  const textBefore = getTextBeforeCursor();
  const match = textBefore.match(TRIGGER_RE);

  if (match) {
    const query = match[1];          // @ 뒤 글자
    candidates = searchLearners(query);
    if (candidates.length > 0) {
      activeIndex = 0;
      showDropdown();
      return;
    }
  }
  hideDropdown();
}

editor.addEventListener("input", handleInput);


// 🔹 블록 D: 드롭다운 렌더링 & 커서 좌표 배치

function showDropdown() {
  // 커서 좌표 획득 → 드롭다운을 그 아래에 배치
  const range = window.getSelection().getRangeAt(0);
  const rect = range.getBoundingClientRect();

  dropdown.innerHTML = candidates
    .map((l, i) =>
      `<li class="${i === activeIndex ? 'active' : ''}" data-id="${l.id}">
         👤 ${l.name}
       </li>`)
    .join("");

  dropdown.classList.remove("hidden");
  dropdown.style.left = `${rect.left + window.scrollX}px`;

  // 뷰포트 하단 넘침 시 위로 flip (가림 방지)
  const dropHeight = dropdown.offsetHeight;
  if (rect.bottom + dropHeight > window.innerHeight) {
    dropdown.style.top = `${rect.top + window.scrollY - dropHeight}px`;
  } else {
    dropdown.style.top = `${rect.bottom + window.scrollY}px`;
  }

  // 마우스 클릭으로도 선택 가능
  dropdown.querySelectorAll("li").forEach((li, i) => {
    li.addEventListener("mousedown", (e) => {
      e.preventDefault();   // 포커스 뺏김 방지
      selectCandidate(i);
    });
  });
}

function hideDropdown() {
  dropdown.classList.add("hidden");
  candidates = [];
}


// 🔹 블록 E: 키보드 네비게이션 & 칩 삽입 (⭐가장 중요)

editor.addEventListener("keydown", (e) => {
  // --- 드롭다운 열린 상태의 키 제어 ---
  if (!dropdown.classList.contains("hidden")) {
    if (e.key === "ArrowDown") {
      e.preventDefault();  // 커서 이동으로 새지 않게
      activeIndex = (activeIndex + 1) % candidates.length;
      showDropdown();
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      activeIndex = (activeIndex - 1 + candidates.length) % candidates.length;
      showDropdown();
    } else if (e.key === "Enter" || e.key === "Tab") {
      e.preventDefault();  // 줄바꿈/포커스이동 막기
      selectCandidate(activeIndex);
    } else if (e.key === "Escape") {
      hideDropdown();
    }
  }
  // --- 칩 통삭제: 커서 바로 앞이 칩이면 한 번에 삭제 ---
  if (e.key === "Backspace") {
    const sel = window.getSelection();
    if (sel.rangeCount === 0) return;
    const range = sel.getRangeAt(0);

    // 커서가 접혀있고(선택영역 없음) 텍스트 노드 맨 앞일 때만 검사
    if (range.collapsed) {
      const node = range.startContainer;
      const offset = range.startOffset;

      // 커서 바로 앞 노드를 찾는다
      let prev = null;
      if (node.nodeType === Node.TEXT_NODE && offset === 0) {
        prev = node.previousSibling;        // 텍스트 맨 앞 → 이전 형제
      } else if (node === editor && offset > 0) {
        prev = editor.childNodes[offset - 1]; // editor 직속 자식 중 앞 노드
      }

      // 앞 노드가 칩이면 통째로 제거
      if (prev && prev.nodeType === Node.ELEMENT_NODE &&
          prev.classList.contains("chip")) {
        e.preventDefault();
        prev.remove();
      }
    }
  }
});   // ← keydown 리스너 끝 (블록 E 전체 종료)


// 🔹 블록 F: 칩 렌더링 & 삽입 (selectCandidate)

function selectCandidate(index) {
  const learner = candidates[index];
  if (!learner) return;

  const sel = window.getSelection();
  const range = sel.getRangeAt(0);

  // 1) 커서 앞에서 "@쿼리" 길이만큼 되돌아가 선택 → 삭제 대상 지정
  const textBefore = getTextBeforeCursor();
  const match = textBefore.match(TRIGGER_RE);
  if (!match) return;

  const triggerLen = match[0].length;   // "@홍길" 전체 길이
  const node = range.startContainer;
  const endOffset = range.startOffset;

  // 텍스트 노드 안에서 @쿼리 구간만 지운다
  if (node.nodeType === Node.TEXT_NODE) {
    const startOffset = endOffset - triggerLen;
    range.setStart(node, Math.max(0, startOffset));
    range.setEnd(node, endOffset);
    range.deleteContents();   // "@홍길" 제거
  }

  // 2) 칩 엘리먼트 생성
  const chip = document.createElement("span");
  chip.className = "chip";
  chip.contentEditable = "false";       // 칩 내부는 편집 불가
  chip.dataset.id = learner.id;         // 저장 시 사용할 ID
  chip.dataset.name = learner.name;
  chip.textContent = `@${learner.name}`;

  // 3) 칩 삽입 + 뒤에 공백(띄어쓰기) 추가
  range.insertNode(chip);
  const space = document.createTextNode("\u00A0");  // non-breaking space
  chip.after(space);

  // 4) 커서를 공백 뒤로 이동 (연속 입력 가능하게)
  const newRange = document.createRange();
  newRange.setStartAfter(space);
  newRange.collapse(true);
  sel.removeAllRanges();
  sel.addRange(newRange);

  hideDropdown();
}


// 🔹 블록 G: 저장용 직렬화 (Streamlit 연동 준비)

// 에디터 내용 → 저장용 텍스트로 직렬화
function serializeEditor() {
  let result = "";
  editor.childNodes.forEach(node => {
    if (node.nodeType === Node.TEXT_NODE) {
      result += node.textContent;
    } else if (node.nodeType === Node.ELEMENT_NODE &&
               node.classList.contains("chip")) {
      // 칩 → [@이름] 형태로 (id도 함께 보관 가능)
      result += `[@${node.dataset.name}]`;
    }
  });
  return result;
}

// 선택된 학습자 ID 목록도 함께 추출
function getSelectedIds() {
  return [...editor.querySelectorAll(".chip")]
    .map(chip => chip.dataset.id);
}
