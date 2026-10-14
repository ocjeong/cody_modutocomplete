# modules/parser.py
import re

# 전화번호(010-1234-5678) | 주민번호(123456-1234567)
SENSITIVE_PATTERN = re.compile(r'\d{3}-\d{3,4}-\d{4}|\d{6}-\d{7}')

# [@키워드] 형태 추출
ISSUE_PATTERN = re.compile(r'\[@(.*?)\]')


def find_sensitive(text: str) -> list[str]:
    """민감정보(전화/주민번호) 매칭 결과 리스트 반환."""
    return SENSITIVE_PATTERN.findall(text)


def find_issues(text: str) -> list[str]:
    """본문에서 [@키워드] 형태를 모두 추출."""
    return ISSUE_PATTERN.findall(text)


def find_new_issues(text: str, known_issues: list[str]) -> list[str]:
    """등록되지 않은 신규 키워드만 골라낸다 (집합 차집합)."""
    used = set(find_issues(text))
    known = set(known_issues)
    return list(used - known)
