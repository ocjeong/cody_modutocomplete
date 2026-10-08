# parser.py
import re
from datetime import datetime, timezone

# [@키워드] 패턴 정규식
MARKER_PATTERN = re.compile(r'\[@(.*?)\]')

def extract_markers(text: str) -> list[str]:
    """
    텍스트에서 [@키워드] 형태의 마커를 모두 추출
    예: "[@결석] 처리 [@건강문제]" → ["결석", "건강문제"]
    """
    return MARKER_PATTERN.findall(text)

def find_new_keywords(text: str, issue_dict: list) -> list[str]:
    """
    텍스트의 마커 중 사전에 없는 신규 키워드만 반환
    예: 사전에 "결석"만 있을 때 "[@결석] [@신규이슈]" → ["신규이슈"]
    """
    markers = extract_markers(text)
    return [m for m in markers if m not in issue_dict]

def build_tags(text: str, selected_names: list, issue_dict: list) -> list[dict]:
    """
    텍스트와 선택된 이름으로부터 태그 메타데이터 생성
    span: 텍스트 내 위치 (시작, 끝) 인덱스
    """
    tags = []

    # 이름 태그 (칩으로 선택된 것)
    for name in selected_names:
        for match in re.finditer(re.escape(name), text):
            tags.append({
                "keyword": name,
                "type": "learner",
                "span": [match.start(), match.end()]
            })

    # 이슈 태그 ([@키워드] 마커)
    for match in MARKER_PATTERN.finditer(text):
        keyword = match.group(1)
        if keyword in issue_dict:
            tags.append({
                "keyword": keyword,
                "type": "issue",
                "span": [match.start(), match.end()]
            })

    # span 시작 위치 기준 정렬
    tags.sort(key=lambda x: x["span"][0])
    return tags

def build_log_json(selected_names: list, raw_text: str, issue_dict: list, author: str = "퍼실리테이터") -> dict:
    """
    최종 저장용 JSON 구조 생성 (기획안 C. 데이터 저장 구조)
    """
    now = datetime.now(timezone.utc)
    log_id = f"LOG_{now.strftime('%Y%m%d_%H%M%S')}"

    return {
        "log_id": log_id,
        "timestamp": now.isoformat(),
        "author": author,
        "tagged_names": selected_names,
        "raw_text": raw_text,
        "tags": build_tags(raw_text, selected_names, issue_dict)
    }
