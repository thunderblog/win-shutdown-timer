# Shutdown Timer

指定した時間または時刻に Windows PC をシャットダウンするスクリプトです。

## 動作環境

- Windows
- Python 3.x（標準ライブラリのみ使用、追加インストール不要）

## 使い方

### 分数で指定

```bash
python shutdown_timer.py 60
```

60 分後にシャットダウンを予約します。

### 時刻で指定（HH:MM 形式）

```bash
python shutdown_timer.py 23:30
```

23:30 にシャットダウンを予約します。指定時刻が過去の場合は翌日として扱います。

### 引数なし（デフォルト値を使用）

```bash
python shutdown_timer.py
```

`config.ini` の `default_minutes` の値でシャットダウンを予約します。

### キャンセル

```bash
python shutdown_timer.py cancel
```

予約済みのシャットダウンをキャンセルします。

## 設定ファイル

`config.ini` でデフォルトの待機時間を変更できます。

```ini
[shutdown]
default_minutes = 90
```
