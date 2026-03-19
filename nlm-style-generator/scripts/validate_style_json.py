#!/usr/bin/env python3
"""NotebookLM スタイルJSON バリデーター

スタイルJSONファイルを検証する:
- JSON構文チェック
- 必須フィールド存在チェック
- 5000文字制限チェック（プリアンブル込み）

Usage:
    python validate_style_json.py <file_path>
"""

import json
import sys
from pathlib import Path

PREAMBLE = "スタイルは下記を適用すること。\n\n"
CHAR_LIMIT = 5000

REQUIRED_FIELDS = {
    "design_directive": ["theme_name", "objective", "target_audience"],
    "visual_identity.color_palette": ["background", "primary_ink", "accent"],
    "visual_identity.typography": ["headings", "body"],
    "illustration_style_guide": ["core_aesthetic", "negative_prompts"],
    "slide_layout_structure": ["grid", "white_space"],
    "content_tone_and_voice": ["style", "language"],
}


def get_nested(data: dict, dotted_key: str) -> dict | None:
    """ドット区切りキーで辞書を掘る"""
    obj = data
    for part in dotted_key.split("."):
        if not isinstance(obj, dict) or part not in obj:
            return None
        obj = obj[part]
    return obj


def validate(file_path: str) -> list[str]:
    errors: list[str] = []
    path = Path(file_path)

    if not path.exists():
        return [f"File not found: {file_path}"]

    raw = path.read_text(encoding="utf-8")

    # プリアンブル除去してJSON部分を取得
    json_text = raw.strip()
    if json_text.startswith("スタイルは"):
        # プリアンブル行を除去してJSON部分のみ抽出
        brace_pos = json_text.find("{")
        if brace_pos == -1:
            return ["JSON object not found in file"]
        json_text = json_text[brace_pos:]

    # JSON構文チェック
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as e:
        return [f"JSON syntax error: {e}"]

    if not isinstance(data, dict):
        return ["Root element must be a JSON object"]

    # 必須フィールドチェック
    for section_path, fields in REQUIRED_FIELDS.items():
        section = get_nested(data, section_path)
        if section is None:
            errors.append(f"Missing section: {section_path}")
            continue
        if not isinstance(section, dict):
            errors.append(f"{section_path} must be an object")
            continue
        # 代替キー名の許容マップ
        alt_keys = {
            "primary_ink": ["primary_text"],
            "accent": ["accent_highlight", "accent_color"],
        }
        for field in fields:
            if field not in section:
                # 代替キー名をチェック
                alternatives = alt_keys.get(field, [])
                if not any(alt in section for alt in alternatives):
                    errors.append(f"Missing required field: {section_path}.{field}")

    # minify形式で文字数カウント（プリアンブル込み）
    minified = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    full_text = PREAMBLE + minified
    char_count = len(full_text)

    return errors, char_count


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_style_json.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    result = validate(file_path)

    if isinstance(result, list):
        # ファイルが見つからない等の致命的エラー
        for err in result:
            print(f"ERROR: {err}")
        sys.exit(1)

    errors, char_count = result

    print(f"Character count: {char_count} / {CHAR_LIMIT}")

    if char_count <= CHAR_LIMIT:
        print(f"OK: Within limit (remaining: {CHAR_LIMIT - char_count} chars)")
    else:
        print(f"OVER: Exceeds limit by {char_count - CHAR_LIMIT} chars")
        errors.append(f"Character count {char_count} exceeds limit of {CHAR_LIMIT}")

    if errors:
        print(f"\nFound {len(errors)} issue(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\nAll checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
