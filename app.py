# app.py
import json
import streamlit as st
from streamlit_searchbox import st_searchbox
from db import load_dictionary, add_issue
from fuzzy_match import search_candidates
from parser import extract_markers, find_new_keywords, build_log_json

# ── 페이지 설정 ──────────────────────────────────────────
st.set_page_config(page_title="운영기록 작성", layout="wide")
st.title("📝 퍼실리테이터 운영기록 작성")

# ── 사전 로드 ────────────────────────────────────────────
@st.cache_data
def get_dictionary():
    return load_dictionary()

def refresh_dictionary():
    st.cache_data.clear()
    return load_dictionary()

dictionary = get_dictionary()

# ── Session State 초기화 ─────────────────────────────────
if "selected_names" not in st.session_state:
    st.session_state.selected_names = []      # 선택 확정된 이름 칩 목록
if "pending_keywords" not in st.session_state:
    st.session_state.pending_keywords = []
if "ignored_keywords" not in st.session_state:
    st.session_state.ignored_keywords = []
if "saved_log" not in st.session_state:
    st.session_state.saved_log = None

# ── [영역 1] 학습자 태그 ─────────────────────────────────
st.subheader("1️⃣ 학습자 태그")

# 퍼지매칭 검색 함수 (searchbox에 직접 연결)
def search_names(query: str) -> list[str]:
    """
    searchbox가 호출하는 검색 함수
    - 빈 쿼리 → 전체 목록 반환
    - 쿼리 있음 → 퍼지매칭 결과 반환
    """
    if not query:
        return dictionary["names"]
    return search_candidates(query, dictionary["names"])

# searchbox: 드롭다운 자동완성 입력창
searched_name = st_searchbox(
    search_names,
    placeholder="이름 입력 (초성/오타 가능) — 선택하면 아래 칩에 추가됩니다",
    key="name_searchbox",
    clear_on_submit=True,      # 선택 후 입력창 자동 초기화
    rerun_on_update=True,      # 입력마다 즉시 재실행 (실시간 드롭다운)
)

# 선택된 이름 → 칩 목록에 추가 (중복 방지)
if searched_name and searched_name not in st.session_state.selected_names:
    st.session_state.selected_names.append(searched_name)

# 칩 렌더링 + 개별 삭제 버튼
if st.session_state.selected_names:
    st.caption("선택된 학습자 (❌ 클릭으로 제거)")
    chip_cols = st.columns(len(st.session_state.selected_names))

    for i, name in enumerate(st.session_state.selected_names):
        with chip_cols[i]:
            # 칩 스타일: 이름 + 삭제 버튼을 하나의 컨테이너로
            if st.button(
                f"👤 {name}  ✕",
                key=f"chip_{name}_{i}",
                help=f"{name} 제거",
                use_container_width=True,
            ):
                st.session_state.selected_names.remove(name)
                st.rerun()
else:
    st.caption("선택된 학습자 없음")

# ── [영역 2] 운영기록 작성 ───────────────────────────────
st.subheader("2️⃣ 운영기록 작성")
st.caption("이슈 키워드는 `[@키워드]` 형태로 입력하세요. 예: `[@결석]`, `[@건강문제]`")

raw_text = st.text_area(
    "운영기록",
    height=200,
    placeholder="예: 오늘 홍길동님 [@결석] 처리 부탁드립니다. 사유는 [@건강문제] 입니다.",
    key="raw_text",
)

# ── [영역 3] 신규 키워드 감지 ────────────────────────────
if raw_text:
    new_keywords = find_new_keywords(raw_text, dictionary["issues"])
    pending = [
        kw for kw in new_keywords
        if kw not in st.session_state.ignored_keywords
    ]

    if pending:
        st.subheader("3️⃣ 신규 키워드 감지")

        for kw in pending:
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.warning(f'⚠️ **`{kw}`** 는 등록되지 않은 이슈 키워드입니다.')
            with col2:
                if st.button("✅ 추가하기", key=f"add_{kw}"):
                    add_issue(kw)
                    dictionary = refresh_dictionary()
                    st.success(f"✅ '{kw}' 사전에 추가됐습니다!")
                    st.rerun()
            with col3:
                if st.button("❌ 무시하기", key=f"ignore_{kw}"):
                    st.session_state.ignored_keywords.append(kw)
                    st.rerun()

# ── [영역 4] 저장 ────────────────────────────────────────
st.subheader("4️⃣ 저장")

col_save, _ = st.columns([1, 3])
with col_save:
    save_clicked = st.button("💾 저장하기", type="primary", use_container_width=True)

if save_clicked:
    if not st.session_state.selected_names and not raw_text.strip():
        st.error("❌ 학습자 태그 또는 운영기록을 입력해주세요.")
    else:
        # 미처리 신규 키워드 검증
        remaining_new = find_new_keywords(raw_text, dictionary["issues"])
        unhandled = [
            kw for kw in remaining_new
            if kw not in st.session_state.ignored_keywords
        ]

        if unhandled:
            st.error(f"❌ 미등록 키워드: {unhandled} → 추가 또는 무시 처리 후 저장하세요.")
        else:
            log_data = build_log_json(
                selected_names=st.session_state.selected_names,
                raw_text=raw_text,
                issue_dict=dictionary["issues"],
            )
            st.session_state.saved_log = log_data

            # data/logs/ 에 JSON 파일 저장
            from pathlib import Path
            log_dir = Path("data/logs")
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"{log_data['log_id']}.json"
            log_file.write_text(
                json.dumps(log_data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            st.success(f"✅ 저장 완료!  `{log_data['log_id']}`")
            st.balloons()

# 저장 결과 미리보기
if st.session_state.saved_log:
    with st.expander("📄 저장된 JSON 확인", expanded=True):
        st.json(st.session_state.saved_log)

# ── 디버깅용 사전 상태 ───────────────────────────────────
with st.expander("🔍 현재 사전 상태"):
    st.json(dictionary)
