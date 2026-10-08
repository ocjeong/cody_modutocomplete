# fuzzy_match.py
from rapidfuzz import fuzz, process

# 한글 초성 리스트
CHO = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ',
       'ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']

def get_chosung(text: str) -> str:
    """한글 문자열에서 초성만 추출. 예: '홍길동' → 'ㅎㄱㄷ'"""
    result = []
    for ch in text:
        code = ord(ch) - 0xAC00
        if 0 <= code <= 11171:
            result.append(CHO[code // 588])
        else:
            result.append(ch)
    return ''.join(result)

def search_candidates(query: str, dictionary: list, limit: int = 5, threshold: int = 70) -> list:
    """
    퍼지 매칭 파이프라인
    1차: 초성 매칭 (ㅎㄱㄷ → 홍길동)
    2차: 레벤슈타인+자로윈클러 유사도 매칭 (오타 교정)
    """
    if not query or not dictionary:
        return []

    query = query.strip()

    # 1차: 완전 일치 (가장 빠름)
    exact = [w for w in dictionary if query in w]
    if exact:
        return exact[:limit]

    # 2차: 초성 매칭
    q_cho = get_chosung(query)
    cho_matches = [w for w in dictionary if get_chosung(w).startswith(q_cho)]
    if cho_matches:
        return cho_matches[:limit]

    # 3차: 유사도 기반 매칭 (오타 허용)
    results = process.extract(
        query,
        dictionary,
        scorer=fuzz.WRatio,   # 레벤슈타인 + 자로윈클러 가중 혼합
        limit=limit
    )
    return [word for word, score, _ in results if score >= threshold]
