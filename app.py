# app.py
import streamlit as st
import streamlit.components.v1 as components

from modules.db import load_dict, save_log, save_dict
from modules.parser import find_sensitive, find_new_issues, find_issues
from modules.component import build_editor_html

st.set_page_config(page_title="운영기록 작성", layout="centered")
st.title("📝 학습자 운영기록 작성")

# 1) 사전/학습자 데이터 로드
data = load_dict()
learners = data["learners"]
known_issues = data["issues"]

# 2) 멘션 에디터 렌더링 (높이 지정 필수)
editor_html = build_editor_html(learners)
components.html(editor_html, height=250)

st.markdown("---")
st.caption("⬇️ 에디터에서 작성 후, 아래에 내용을 붙여넣고 저장하세요 (MVP 임시 연결)")

# 3) serialize된 텍스트를 받는 입력창
#    (실제로는 JS가 자동 복사하지만, MVP에선 수동 확인 가능하게)
record_text = st.text_area("운영기록 내용", height=120,
                           placeholder="[@홍길동] 오늘 지각 처리했습니다.")

# 4) 저장 버튼 + 검증 로직
if st.button("💾 저장", type="primary"):
    if not record_text.strip():
        st.warning("내용을 입력해주세요.")
        st.stop()

    # ── 검증 ① 민감정보 검출 ──
    sensitive = find_sensitive(record_text)
    if sensitive:
        st.error(f"🚨 민감정보가 감지되었습니다: {sensitive}")
        st.info("전화번호·주민번호를 제거한 후 다시 저장해주세요.")
        st.stop()   # 저장 중단

    # ── 검증 ② 신규 키워드 확인 ──
    new_issues = find_new_issues(record_text, known_issues)
    if new_issues:
        st.warning(f"🆕 사전에 없는 키워드: {new_issues}")
        # 신규 키워드를 사전에 자동 추가
        data["issues"].extend(new_issues)
        save_dict(data)
        st.info(f"사전에 {new_issues}를 추가했습니다.")

    # ── 저장 실행 ──
    record = {
        "text": record_text,
        "issues": find_issues(record_text),   # [@키워드] 전체
    }
    path = save_log(record)
    st.success(f"✅ 저장 완료! ({path})")
    st.balloons()
