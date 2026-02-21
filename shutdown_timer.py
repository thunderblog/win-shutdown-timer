"""Windows シャットダウンタイマー"""

import configparser
import math
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_MINUTES = 90


def load_default_minutes() -> int:
    config_path = Path(__file__).parent / "config.ini"
    if not config_path.exists():
        return DEFAULT_MINUTES
    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")
    return config.getint("shutdown", "default_minutes", fallback=DEFAULT_MINUTES)


def parse_time_arg(time_str: str) -> int:
    """時刻文字列 (HH:MM) から現在時刻との差分を分で返す。過去なら翌日扱い。"""
    target = datetime.strptime(time_str, "%H:%M").replace(
        year=datetime.now().year,
        month=datetime.now().month,
        day=datetime.now().day,
    )
    now = datetime.now()
    diff = (target - now).total_seconds()
    if diff <= 0:
        diff += 24 * 60 * 60  # 翌日として扱う
    return math.ceil(diff / 60)


def schedule_shutdown(minutes: int) -> None:
    seconds = minutes * 60
    subprocess.run(["shutdown", "/s", "/t", str(seconds)], check=True)
    print(f"シャットダウンを {minutes} 分後({seconds} 秒後)に予約しました。")
    print("キャンセルするには: python shutdown_timer.py cancel")


def cancel_shutdown() -> None:
    result = subprocess.run(["shutdown", "/a"], capture_output=True, text=True)
    if result.returncode == 0:
        print("シャットダウン予約をキャンセルしました。")
    else:
        print("キャンセルに失敗しました(予約がないか、権限不足です）。")


def main() -> None:
    if len(sys.argv) < 2:
        minutes = load_default_minutes()
        print(f"引数なし → config.ini のデフォルト値 {minutes} 分で予約します。")
        schedule_shutdown(minutes)
        return

    arg = sys.argv[1]

    if arg == "cancel":
        cancel_shutdown()
        return

    if ":" in arg:
        minutes = parse_time_arg(arg)
        print(f"時刻指定 {arg} → 約 {minutes} 分後にシャットダウンします。")
        schedule_shutdown(minutes)
        return

    try:
        minutes = int(arg)
    except ValueError:
        print(f"エラー: '{arg}' は有効な数値または時刻(HH:MM)ではありません。")
        sys.exit(1)

    if minutes <= 0:
        print("エラー: 1分以上を指定してください。")
        sys.exit(1)

    schedule_shutdown(minutes)


if __name__ == "__main__":
    main()
