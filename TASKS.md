# 改善タスクリスト

## バグ修正

- [x] `parse_time_arg` で `datetime.now()` を2回呼んでいる問題を修正
- [x] `shutdown /t` の秒数上限チェックを追加

## コード品質

- [x] `config.ini` のデフォルト値をコード定数 `DEFAULT_MINUTES = 90` に合わせる

## 機能追加

- [x] `status` コマンドの追加（現在の予約状況を確認）
- [x] `--help` / `-h` オプションの追加
- [x] `argparse` への移行
