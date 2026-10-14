# modules/fuzzy_match.py
from rapidfuzz import fuzz

# 초성 테이블 (유니코드 한글 분해용)
CHOSUNG = [
    'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ',
    'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
]

HANGUL_START = 0xAC00  # '가'
HANGUL_END = 0xD7A3     # '힣'


def get_chosung(text: str) -> str:
    """문자열을 초성으로 변환. 예: '홍길동' → 'ㅎㄱㄷ'"""
    result = []
    for ch in text:
        code = ord(ch)
        if HANGUL_START <= code <= HANGUL_END:
            # (코드 - 시작점) // (중성21 * 종성28) = 초성 인덱스
            idx = (code - HANGUL_START) // 588
            result.append(CHOSUNG[idx])
        else:
            result.append(ch)  # 한글이 아니면 그대로
    return ''.join(result)


def is_chosung_only(text: str) -> bool:
    """입력이 초성(ㄱ~ㅎ)으로만 이뤄졌는지 판별."""
    return all(ch in CHOSUNG for ch in text) and len(text) > 0


def search(query: str, learners: list[dict], threshold: int = 70) -> list[dict]:
    """
    학습자 검색.
    - 초성 입력(@ㅎㄱㄷ): 이름 초성과 '접두 매칭'
    - 일반 입력(@홍길):   접두 매칭 + RapidFuzz 유사도
    """
    if not query:
        return []

    results = []
    for learner in learners:
        name = learner["name"]

        if is_chosung_only(query):
            # 초성 검색: 이름의 초성이 query로 시작하는가
            name_cho = get_chosung(name)
            if name_cho.startswith(query):
                results.append(learner)
        else:
            # 1) 접두 매칭 (홍길 → 홍길동) 우선
            if name.startswith(query):
                results.append(learner)
            # 2) 오타 허용 유사도 매칭
            elif fuzz.ratio(query, name) >= threshold:
                results.append(learner)

    return results
