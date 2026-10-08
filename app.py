# app.py
import streamlit as st
from db import load_dictionary

st.set_page_config(page_title="운영기록 작성", layout="wide")
st.title("📝 퍼실리테이터 운영기록 작성")

# 앱 실행 시 사전 1회 로드 → 캐싱 (기획안 Data Flow 1번)
@st.cache_data
def get_dictionary():
    return load_dictionary()

dictionary = get_dictionary()

# [영역 1] 학습자 태그 (Chip UI)
st.subheader("1️⃣ 학습자 태그")
selected_names = st.multiselect(
    "학습자를 선택하세요",
    options=dictionary["names"],
    placeholder="이름 입력 또는 선택"
)

# [영역 2] 운영기록 작성
st.subheader("2️⃣ 운영기록 작성")
raw_text = st.text_area(
    "운영기록을 작성하세요 (이슈는 [@키워드] 형태로 입력)",
    height=200,
    placeholder="예: 오늘 [@결석] 처리 부탁드립니다."
)

# [영역 4] 저장 버튼
st.subheader("3️⃣ 저장")
if st.button("💾 저장하기", type="primary"):
    st.write("선택된 학습자:", selected_names)
    st.write("작성 내용:", raw_text)
    st.success("저장 로직은 다음 단계에서 구현합니다!")

# (디버깅용) 현재 사전 상태 확인
with st.expander("🔍 현재 사전 상태"):
    st.json(dictionary)
