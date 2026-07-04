"""
screen セッション経由の Minecraft サーバー管理と logs/latest.log の監視
"""
import asyncio
import os
import re
import subprocess
from typing import Callable, Awaitable, Optional

_JOIN_RE = re.compile(r'\[.*?/INFO\].*?:\s+(\S+) joined the game')
_LEAVE_RE = re.compile(r'\[.*?/INFO\].*?:\s+(\S+) (?:left the game|lost connection)')


class MinecraftServer:
    def __init__(
        self,
        server_dir: str,
        screen_name: str = 'minecraft',
        start_script: str = 'run.sh',
    ):
        self.server_dir = server_dir
        self.screen_name = screen_name
        self.start_script = start_script

        self._log_task: Optional[asyncio.Task] = None
        self.on_player_join: Optional[Callable[[str], Awaitable[None]]] = None
        self.on_player_leave: Optional[Callable[[str], Awaitable[None]]] = None

    @property
    def is_running(self) -> bool:
        try:
            result = subprocess.run(
                ['screen', '-list'],
                capture_output=True,
                text=True,
            )
            return self.screen_name in result.stdout
        except FileNotFoundError:
            # screen コマンドが見つからない場合
            return False

    async def start(self) -> bool:
        if self.is_running:
            return False

        proc = await asyncio.create_subprocess_exec(
            'screen', '-dmS', self.screen_name, 'bash', self.start_script,
            cwd=self.server_dir,
        )
        await proc.wait()

        if proc.returncode != 0:
            return False

        self._start_log_task()
        return True

    async def stop(self) -> bool:
        if not self.is_running:
            return False

        # screen セッションに stop コマンドを送信
        proc = await asyncio.create_subprocess_exec(
            'screen', '-S', self.screen_name, '-X', 'stuff', 'stop\r',
        )
        await proc.wait()

        # 最大 60 秒待機
        for _ in range(60):
            await asyncio.sleep(1)
            if not self.is_running:
                break

        if self._log_task:
            self._log_task.cancel()
            self._log_task = None

        return True

    def resume_monitoring(self):
        """Bot 起動時にすでにサーバーが動いている場合のログ監視再開"""
        if self.is_running and (self._log_task is None or self._log_task.done()):
            self._start_log_task()

    def _start_log_task(self):
        self._log_task = asyncio.create_task(self._tail_log())

    async def _tail_log(self):
        log_path = os.path.join(self.server_dir, 'logs', 'latest.log')

        # ログファイルが生成されるまで待機 (最大 60 秒)
        for _ in range(60):
            if os.path.exists(log_path):
                break
            await asyncio.sleep(1)
        else:
            return

        try:
            with open(log_path, encoding='utf-8', errors='replace') as f:
                f.seek(0, 2)  # ファイル末尾から監視開始
                while True:
                    line = f.readline()
                    if line:
                        await self._dispatch_log(line.rstrip())
                    else:
                        await asyncio.sleep(0.5)
                        if not self.is_running:
                            break
        except asyncio.CancelledError:
            pass

    async def _dispatch_log(self, line: str):
        join_m = _JOIN_RE.search(line)
        if join_m and self.on_player_join:
            await self.on_player_join(join_m.group(1))
            return

        leave_m = _LEAVE_RE.search(line)
        if leave_m and self.on_player_leave:
            await self.on_player_leave(leave_m.group(1))
