#!/usr/bin/env python3
import sys
import re
import argparse

def count_characters(text):
    # MD記法をストリップする簡易エンジン
    # 1. コードブロックの削除
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # 2. インラインコードの削除
    text = re.sub(r'`.*?`', '', text)
    # 3. HTMLタグの削除
    text = re.sub(r'<.*?>', '', text)
    # 4. リンク記法 [text](url) -> text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # 5. 画像記法 ![alt](url) -> 削除
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # 6. 見出し記号 #
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    # 7. リスト記号 * or - or 1.
    text = re.sub(r'^[ \t]*[*+-]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[ \t]*\d+\.\s+', '', text, flags=re.MULTILINE)
    # 8. 太字・斜体
    text = re.sub(r'[*_]{1,3}(.*?)[*_]{1,3}', r'\1', text)
    # 9. 引用記号 >
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)

    # 全体の空白と改行を詰めた純粋な文字数（スペースなし）
    chars_no_spaces = len(re.sub(r'\s', '', text))
    
    # 改行を除外した文字数（スペースあり）
    # 日本語の場合、単語間のスペースはないことが多いが、Wordの「スペースを含まない文字数」に近いもの
    # ここでは「改行以外の文字数」をスペースありとして定義
    chars_with_spaces = len(re.sub(r'[\r\n]', '', text))

    return chars_no_spaces, chars_with_spaces

def main():
    parser = argparse.ArgumentParser(description='MDファイルからWord相当の文字数をカウントします。')
    parser.add_argument('file', help='解析するMDファイルパス')
    args = parser.parse_args()

    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        no_spaces, with_spaces = count_characters(content)
        
        print(f"ファイル: {args.file}")
        print(f"文字数 (スペースなし): {no_spaces}")
        print(f"文字数 (スペースあり): {with_spaces}")
        
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
