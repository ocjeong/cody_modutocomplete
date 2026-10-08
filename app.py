# app.py
import json
import streamlit as st
from db import load_dictionary, add_issue
from fuzzy_match import search_candidates
from parser import extract_markers, find_new_keywords, build_log_json

# ── 페이지 설정 ──────────────────────────────────────────
st.set_page_config(page_title="운영기록 작성", layout="wide")
st.title("📝 퍼실리테이터 운영기록 작성")

# ── 사전 로드 (캐싱) ─────────────────────────────────────
@st.cache_data
def get_dictionary():
    return load_dictionary()

# 신규 키워드 추가 후 캐시 갱신용
def refresh_dictionary():
    st.cache_data.clear()
    return load_dictionary()

dictionary = get_dictionary()

# ── Session State 초기화 ─────────────────────────────────
# 신규 키워드 처리 상태를 저장 (버튼 클릭해도 상태 유지)
if "pending_keywords" not in st.session_state:
    st.session_state.pending_keywords = []   # 등록 대기 중인 신규 키워드
if "ignored_keywords" not in st.session_state:
    st.session_state.ignored_keywords = []   # 이번 세션에서 무시한 키워드
if "saved_log" not in st.session_state:
    st.session_state.saved_log = None        # 마지막 저장 결과

# ── [영역 1] 학습자 태그 (Chip UI) ───────────────────────
st.subheader("1️⃣ 학습자 태그")

name_query = st.text_input(
    "이름 검색 (초성/오타 가능)",
    placeholder="예: ㅎㄱㄷ 또는 홍길동",
    key="name_query"
)

# 퍼지 매칭으로 후보 추천
name_candidates = (
    search_candidates(name_query, dictionary["names"])
    if name_query
    else dictionary["names"]   # 입력 없으면 전체 목록 표시
)

selected_names = st.multiselect(
    "학습자 선택 (칩으로 고정됩니다)",
    options=name_candidates,
    placeholder="위 검색창에서 찾은 후 선택하세요"
)

# 이름 검색 결과 없을 때 안내
if name_query and not name_candidates:
    st.warning("⚠️ 일치하는 학습자가 없습니다. 이름은 마스터 DB에서만 추가 가능합니다.")

# ── [영역 2] 운영기록 작성 ───────────────────────────────
st.subheader("2️⃣ 운영기록 작성")
st.caption("이슈 키워드는 `[@키워드]` 형태로 입력하세요. 예: `[@결석]`, `[@건강문제]`")

raw_text = st.text_area(
    "운영기록",
    height=200,
    placeholder="예: 오늘 홍길동님 [@결석] 처리 부탁드립니다. 사유는 [@건강문제] 입니다.",
    key="raw_text"
)

# ── [영역 3] 신규 키워드 감지 및 등록 알림 ───────────────
if raw_text:
    new_keywords = find_new_keywords(raw_text, dictionary["issues"])

    # 무시 목록과 이미 처리된 것 제외
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
                    dictionary = refresh_dictionary()   # 캐시 갱신
                    st.success(f"✅ '{kw}' 사전에 추가됐습니다!")
                    st.rerun()
            with col3:
                if st.button("❌ 무시하기", key=f"ignore_{kw}"):
                    st.session_state.ignored_keywords.append(kw)
                    st.rerun()

# ── [영역 4] 저장 버튼 ───────────────────────────────────
st.subheader("4️⃣ 저장")

col_save, col_preview = st.columns([1, 3])

with col_save:
    save_clicked = st.button("💾 저장하기", type="primary", use_container_width=True)

if save_clicked:
    # 저장 전 검증
    if not selected_names and not raw_text.strip():
        st.error("❌ 학습자 태그 또는 운영기록을 입력해주세요.")
    else:
        # 미처리 신규 키워드가 있으면 경고
        remaining_new = find_new_keywords(raw_text, dictionary["issues"])
        unhandled = [
            kw for kw in remaining_new
            if kw not in st.session_state.ignored_keywords
        ]

        if unhandled:
            st.error(f"❌ 미등록 키워드가 있습니다: {unhandled} → 추가하거나 무시하기를 먼저 처리해주세요.")
        else:
            # JSON 생성
            log_data = build_log_json(
                selected_names=selected_names,
                raw_text=raw_text,
                issue_dict=dictionary["issues"]
            )
            st.session_state.saved_log = log_data

            # 로컬 저장 (data/logs/ 폴더에 JSON 파일로 저장)
            from pathlib import Path
            log_dir = Path("data/logs")
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / f"{log_data['log_id']}.json"
            log_file.write_text(
                json.dumps(log_data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            st.success(f"✅ 저장 완료! `{log_data['log_id']}`")
            st.balloons()

# 저장 결과 미리보기
if st.session_state.saved_log:
    with st.expander("📄 저장된 JSON 확인", expanded=True):
        st.json(st.session_state.saved_log)

# ── 디버깅용 사전 상태 확인 ──────────────────────────────
with st.expander("🔍 현재 사전 상태"):
    st.json(dictionary)
