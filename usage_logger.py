#!/usr/bin/env python3
import os
from datetime import datetime

# ログファイルの保存先：このスクリプトと同じディレクトリの usage.log
LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "usage.log"))

def log_usage(skill_name):
    """
    スキルの使用をログに記録する。
    1行に「日付 時刻, スキル名」の形式で追記する。
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{timestamp}, {skill_name}\n")
    except Exception:
        # ロギングの失敗がメインの処理を止めないようにする
        pass

if __name__ == "__main__":
    # 直接実行された場合は、コマンドライン引数からスキル名を取得して記録
    import sys
    if len(sys.argv) > 1:
        log_usage(sys.argv[1])
    else:
        print("Usage: python usage_logger.py <skill_name>")
