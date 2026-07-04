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

- Minecraft Forge サーバー (`run.sh` で起動できる状態)
- Discord Bot トークン
- **直接起動の場合**: Python 3.10 以上、`screen` コマンド
- **Docker で起動の場合**: Docker、Docker Compose

## 共通設定

### 1. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集して各項目を設定してください。

```env
DISCORD_TOKEN=your_bot_token_here

MC_SERVER_DIR=/path/to/minecraft-server  # run.sh があるディレクトリ (ホスト側のパス)
MC_SCREEN_NAME=create                     # screen セッション名
MC_START_SCRIPT=run.sh

MC_RCON_HOST=localhost
MC_RCON_PORT=25575
MC_RCON_PASSWORD=your_rcon_password
```

### 2. Minecraft サーバーの設定

`server.properties` で RCON を有効にしてください（`/list` コマンドに必要）。

```properties
enable-rcon=true
rcon.port=25575
rcon.password=（.env の MC_RCON_PASSWORD と同じ値）
```

---

## 起動方法 A — Python で直接起動

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 起動

```bash
python main.py
```

---

## 起動方法 B — Docker で起動

### 1. ユーザー ID の確認

`/server start|stop` コマンドがホストの screen セッションを操作できるよう、コンテナをホストと同じユーザーで動かす必要があります。  
以下のコマンドで UID と GID を確認してください。

```bash
id
# 例: uid=1000(ubuntu) gid=1000(ubuntu) ...
```

`docker-compose.yml` の `user` 行を確認した値に合わせてください（デフォルト `1000:1000`）。

```yaml
user: "1000:1000"  # ← UID:GID を変更
```

### 2. ビルドと起動

```bash
docker compose up -d
```

### 3. ログの確認

```bash
docker compose logs -f
```

### 4. 停止

```bash
docker compose down
```

### Docker 起動時の仕組み

| 機能 | 方法 |
|---|---|
| ログ監視 | MC サーバーディレクトリをコンテナに読み取り専用でマウント |
| RCON (`/list`) | `network_mode: host` でホストの localhost に接続 |
| サーバー起動/停止 | `/run/screen` をマウントしてホストの screen セッションを共有 |

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
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```
