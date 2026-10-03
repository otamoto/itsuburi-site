#!/usr/bin/env python3
"""質問ごとの静的ページ生成（q/<id>/index.html）。

質問リンク共有の安全原則（itsuburi/docs/spec_v1.md 追補13）に従い、
このスクリプトは「アプリの質問バンクCSVの質問文を、質問IDごとの
静的ページへそのまま焼き込む」だけを行う。クエリ文字列を読んで画面に
出力するようなJavaScriptは書かない（そもそもJS自体を使わない）。

使い方:
    python3 tools/generate_question_pages.py

アプリ側の assets/data/questions_v1.csv（../itsuburi と同じ階層にある
前提）を読み、itsuburi-site/q/<id>/index.html を全件生成する。
"""

from __future__ import annotations

import csv
import html
import sys
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent
# 同階層の itsuburi リポジトリ（アプリ本体）のCSVが質問バンクの正
CSV_PATH = SITE_ROOT.parent / "itsuburi" / "assets" / "data" / "questions_v1.csv"

APP_STORE_URL = "https://apps.apple.com/jp/app/id6814577326"

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex">
<title>いつぶり？ — {question_text}</title>
<style>
  :root {{
    --paper: #FBF6EC;
    --ink: #2B2A2E;
    --ink2: #4A4842;
    --ink3: #6E6B66;
    --line: #D9D3C8;
  }}
  body {{
    background: var(--paper);
    color: var(--ink);
    font-family: "Hiragino Mincho ProN", "Yu Mincho", serif;
    line-height: 1.9;
    max-width: 560px;
    margin: 0 auto;
    padding: 64px 20px 80px;
    text-align: center;
  }}
  h1 {{
    font-size: 1rem;
    letter-spacing: 0.2em;
    color: var(--ink3);
    margin: 0 0 2.4em;
    font-weight: 400;
  }}
  .question {{
    font-size: 1.4rem;
    line-height: 1.8;
    margin: 0 0 2.8em;
  }}
  .actions {{
    display: flex;
    flex-direction: column;
    gap: 14px;
    align-items: center;
  }}
  .btn {{
    display: inline-block;
    width: 100%;
    max-width: 320px;
    box-sizing: border-box;
    padding: 14px 20px;
    border-radius: 14px;
    text-decoration: none;
    font-size: 0.95rem;
  }}
  .btn.primary {{ background: var(--ink); color: var(--paper); }}
  .btn.secondary {{ background: #fff; color: var(--ink); border: 1px solid var(--line); }}
  .note {{ font-size: 0.85rem; color: var(--ink3); margin-top: 3em; }}
  .note a {{ color: var(--ink2); }}
</style>
</head>
<body>
<h1>いつぶり？</h1>
<p class="question">{question_text}</p>
<div class="actions">
  <a class="btn primary" href="itsuburi://q/{id}">アプリで開く</a>
  <a class="btn secondary" href="{app_store_url}">App Storeで入手</a>
  <!-- Google Playは未公開のため非表示。公開後はここに
       <a class="btn secondary" href="https://play.google.com/store/apps/details?id=...">Google Playで入手</a>
       を追加する -->
</div>
<p class="note"><a href="../../">アプリについて</a></p>
</body>
</html>
"""


def load_questions(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        if not row.get("id") or not row.get("question"):
            raise ValueError(f"id/question列が読めない行があります: {row}")
    return rows


def generate(csv_path: Path, out_root: Path) -> int:
    rows = load_questions(csv_path)
    count = 0
    for row in rows:
        question_id = int(row["id"].strip())
        question_text = row["question"].strip()
        page = PAGE_TEMPLATE.format(
            id=question_id,
            question_text=html.escape(question_text),
            app_store_url=APP_STORE_URL,
        )
        page_dir = out_root / "q" / str(question_id)
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(page, encoding="utf-8")
        count += 1
    return count


def main() -> None:
    if not CSV_PATH.exists():
        print(f"質問バンクCSVが見つかりません: {CSV_PATH}", file=sys.stderr)
        sys.exit(1)
    count = generate(CSV_PATH, SITE_ROOT)
    print(f"{count}件のページを生成しました（{SITE_ROOT / 'q'}）")


if __name__ == "__main__":
    main()
