# modules/db.py
import json
import os
from datetime import datetime

DATA_DIR = "data"
DICT_PATH = os.path.join(DATA_DIR, "dict.json")
LOGS_DIR = os.path.join(DATA_DIR, "logs")


def load_dict() -> dict:
    """학습자 목록 + 이슈 키워드 사전을 불러온다."""
    if not os.path.exists(DICT_PATH):
        # 파일이 없으면 기본 구조 반환 (최초 실행 방어)
        return {"learners": [], "issues": []}
    with open(DICT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_dict(data: dict) -> None:
    """사전 갱신 (신규 키워드 추가 시 사용)."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DICT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_log(record: dict) -> str:
    """운영기록 1건을 JSON으로 저장. 저장된 파일 경로 반환."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    # 파일명: 타임스탬프 기반 (중복 방지)
    filename = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".json"
    path = os.path.join(LOGS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return path
