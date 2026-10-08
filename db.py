# db.py
import json
from pathlib import Path

DICT_PATH = Path("data/dictionary.json")

def load_dictionary() -> dict:
    """사전 로드 (파일 없으면 기본값 생성)"""
    if not DICT_PATH.exists():
        DICT_PATH.parent.mkdir(exist_ok=True)
        default = {"names": [], "issues": []}
        DICT_PATH.write_text(json.dumps(default, ensure_ascii=False, indent=2))
        return default
    return json.loads(DICT_PATH.read_text(encoding="utf-8"))

def add_issue(keyword: str):
    """신규 이슈 키워드를 사전에 추가"""
    data = load_dictionary()
    if keyword not in data["issues"]:
        data["issues"].append(keyword)
        DICT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
