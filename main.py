import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from bot_config import BotConfig
from minecraft.process import MinecraftServer

load_dotenv()

intents = discord.Intents.default()


class MinecraftBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.config = BotConfig.load()
        self.mc_server = MinecraftServer(
            server_dir=os.environ.get('MC_SERVER_DIR', './minecraft-server'),
            screen_name=os.environ.get('MC_SCREEN_NAME', 'create'),
            start_script=os.environ.get('MC_START_SCRIPT', 'run.sh'),
        )

    async def setup_hook(self):
        self.mc_server.on_player_join = self._on_player_join
        self.mc_server.on_player_leave = self._on_player_leave

        await self.load_extension('cogs.log_cog')
        await self.load_extension('cogs.server_cog')
        await self.load_extension('cogs.list_cog')

        guild_id = os.environ.get('DISCORD_GUILD_ID')
        if guild_id:
            # ギルド指定同期: 即時反映 (開発・本番ともに推奨)
            guild = discord.Object(id=int(guild_id))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f'ギルド {guild_id} にスラッシュコマンドを同期しました。')
        else:
            # グローバル同期: 反映まで最大1時間かかる
            await self.tree.sync()
            print('スラッシュコマンドをグローバル同期しました (反映まで最大1時間)。')

    async def on_ready(self):
        print(f'ログイン成功: {self.user} (ID: {self.user.id})')
        print('------')
        # Bot 起動時にサーバーがすでに動いていればログ監視を再開
        self.mc_server.resume_monitoring()

    async def _on_player_join(self, player_name: str):
        await self._send_log(f'➡️ **{player_name}** がサーバーに参加しました。')

    async def _on_player_leave(self, player_name: str):
        await self._send_log(f'⬅️ **{player_name}** がサーバーから退出しました。')

    async def _send_log(self, message: str):
        if not self.config.log_send_enabled:
            return
        if not self.config.log_channel_id:
            return
        channel = self.get_channel(self.config.log_channel_id)
        if channel:
            await channel.send(message)


async def main():
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        raise RuntimeError('DISCORD_TOKEN が .env に設定されていません。')

    bot = MinecraftBot()
    async with bot:
        await bot.start(token)


if __name__ == '__main__':
    asyncio.run(main())
