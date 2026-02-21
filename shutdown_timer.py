"""Windows シャットダウンタイマー"""

import argparse
import configparser
import json
import math
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_MINUTES = 90
MAX_SECONDS = 315360000  # shutdown /t の上限

STATE_FILE = Path(__file__).parent / ".shutdown_state.json"


def load_default_minutes() -> int:
    config_path = Path(__file__).parent / "config.ini"
    if not config_path.exists():
        return DEFAULT_MINUTES
    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")
    return config.getint("shutdown", "default_minutes", fallback=DEFAULT_MINUTES)


def parse_time_arg(time_str: str) -> int:
    """時刻文字列 (HH:MM) から現在時刻との差分を分で返す。過去なら翌日扱い。"""
    now = datetime.now()
    target = datetime.strptime(time_str, "%H:%M").replace(
        year=now.year, month=now.month, day=now.day
    )
    diff = (target - now).total_seconds()
    if diff <= 0:
        diff += 24 * 60 * 60  # 翌日として扱う
    return math.ceil(diff / 60)


def save_state(minutes: int) -> None:
    scheduled_at = datetime.now() + timedelta(minutes=minutes)
    STATE_FILE.write_text(
        json.dumps({"scheduled_at": scheduled_at.isoformat()}), encoding="utf-8"
    )


def clear_state() -> None:
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def schedule_shutdown(minutes: int) -> None:
    seconds = minutes * 60
    if seconds > MAX_SECONDS:
        print(f"エラー: 指定時間が上限({MAX_SECONDS // 60} 分)を超えています。")
        sys.exit(1)
    subprocess.run(["shutdown", "/s", "/t", str(seconds)], check=True)
    save_state(minutes)
    print(f"シャットダウンを {minutes} 分後({seconds} 秒後)に予約しました。")
    print("キャンセルするには: python shutdown_timer.py cancel")


def cancel_shutdown() -> None:
    result = subprocess.run(["shutdown", "/a"], capture_output=True, text=True)
    if result.returncode == 0:
        clear_state()
        print("シャットダウン予約をキャンセルしました。")
    else:
        print("キャンセルに失敗しました（予約がないか、権限不足です）。")


def show_status() -> None:
    if not STATE_FILE.exists():
        print("シャットダウンの予約はありません。")
        return
    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    scheduled_at = datetime.fromisoformat(data["scheduled_at"])
    now = datetime.now()
    if scheduled_at <= now:
        print("シャットダウンの予約はありません（または既に実行済みです）。")
        clear_state()
        return
    remaining_min = math.ceil((scheduled_at - now).total_seconds() / 60)
    print(f"シャットダウン予定時刻: {scheduled_at.strftime('%H:%M:%S')}")
    print(f"残り約 {remaining_min} 分")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="指定時間または時刻に Windows PC をシャットダウンします。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
使用例:
  python shutdown_timer.py          デフォルト時間 (config.ini) で予約
  python shutdown_timer.py 60       60 分後にシャットダウン
  python shutdown_timer.py 23:30    23:30 にシャットダウン
  python shutdown_timer.py cancel   予約をキャンセル
  python shutdown_timer.py status   予約状況を確認
""",
    )
    parser.add_argument(
        "time",
        nargs="?",
        metavar="TIME",
        help="分数(例: 60)、時刻(例: 23:30)、cancel、または status",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.time is None:
        minutes = load_default_minutes()
        print(f"引数なし → config.ini のデフォルト値 {minutes} 分で予約します。")
        schedule_shutdown(minutes)
        return

    arg = args.time

    if arg == "cancel":
        cancel_shutdown()
        return

    if arg == "status":
        show_status()
        return

    if ":" in arg:
        try:
            minutes = parse_time_arg(arg)
        except ValueError:
            print(f"エラー: '{arg}' は有効な時刻(HH:MM)ではありません。")
            sys.exit(1)
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
