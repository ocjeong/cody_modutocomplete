# modules/component.py
import json
import os

FRONTEND_DIR = "frontend"


def build_editor_html(learners: list[dict]) -> str:
    """HTML+CSS+JS를 하나로 합치고 학습자 데이터를 주입."""
    # 1) 각 파일 읽기
    with open(os.path.join(FRONTEND_DIR, "editor.html"), encoding="utf-8") as f:
        html = f.read()
    with open(os.path.join(FRONTEND_DIR, "editor.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(FRONTEND_DIR, "editor.js"), encoding="utf-8") as f:
        js = f.read()

    # 2) <link>, <script src> 를 인라인으로 교체 (외부 파일 못 읽는 iframe 대비)
    html = html.replace(
        '<link rel="stylesheet" href="editor.css">',
        f"<style>{css}</style>"
    )
    html = html.replace(
        '<script src="editor.js"></script>',
        f"<script>{js}</script>"
    )

    # 3) __LEARNERS__ → 실제 JSON 배열로 치환
    learners_json = json.dumps(learners, ensure_ascii=False)
    html = html.replace("__LEARNERS__", learners_json)

    return html
