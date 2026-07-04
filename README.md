# Minecraft Server Manager Bot

Discord からマインクラフト (Forge) サーバーを管理する Bot です。

## 機能

| コマンド | 説明 |
|---|---|
| `/log channel <ID>` | ログを送信する Discord チャネルを設定 |
| `/log send true\|false` | 入退出ログ送信の ON/OFF |
| `/server start` | サーバーを起動 |
| `/server stop` | サーバーを停止 |
| `/list` | 現在のプレイヤー一覧を表示 |

## 必要なもの

- Python 3.10 以上
- `screen` コマンド
- Minecraft Forge サーバー (`run.sh` で起動できる状態)
- Discord Bot トークン

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集して各項目を設定してください。

```env
DISCORD_TOKEN=your_bot_token_here

MC_SERVER_DIR=/path/to/minecraft-server  # run.sh があるディレクトリ
MC_SCREEN_NAME=create                     # screen セッション名
MC_START_SCRIPT=run.sh

MC_RCON_HOST=localhost
MC_RCON_PORT=25575
MC_RCON_PASSWORD=your_rcon_password
```

### 3. Minecraft サーバーの設定

`server.properties` で RCON を有効にしてください（`/list` コマンドに必要）。

```properties
enable-rcon=true
rcon.port=25575
rcon.password=（.env の MC_RCON_PASSWORD と同じ値）
```

### 4. Bot の起動

```bash
python main.py
```

## Discord Bot の作成

1. [Discord Developer Portal](https://discord.com/developers/applications) でアプリケーションを作成
2. **Bot** ページでトークンを発行し `.env` の `DISCORD_TOKEN` に設定
3. **OAuth2 → URL Generator** で `bot` と `applications.commands` スコープを選択してサーバーに招待

## 入退出ログの使い方

1. `/log channel <チャネルID>` でログ送信先を設定
2. `/log send true` で送信を有効化

チャネル ID は Discord でチャネルを右クリック →「IDをコピー」で取得できます（開発者モードが必要）。

## ファイル構成

```
.
├── main.py              # エントリポイント
├── bot_config.py        # 設定の永続化 (config.json)
├── minecraft/
│   ├── process.py       # screen 経由のサーバー管理・ログ監視
│   └── rcon.py          # RCON クライアント
├── cogs/
│   ├── log_cog.py       # /log コマンド
│   ├── server_cog.py    # /server コマンド
│   └── list_cog.py      # /list コマンド
├── requirements.txt
└── .env.example
```
