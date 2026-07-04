import discord
from discord import app_commands
from discord.ext import commands


class ServerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    server_group = app_commands.Group(name='server', description='マインクラフトサーバー管理')

    @server_group.command(name='start', description='マインクラフトサーバーを起動します')
    async def server_start(self, interaction: discord.Interaction):
        mc = self.bot.mc_server
        if mc.is_running:
            await interaction.response.send_message('サーバーはすでに起動しています。')
            return

        await interaction.response.defer()
        try:
            started = await mc.start()
        except Exception as e:
            await interaction.followup.send(f'サーバーの起動に失敗しました。\n```{e}```')
            return

        if started:
            await interaction.followup.send('マインクラフトサーバーが起動しました。')
            await self._notify_log('マインクラフトサーバーが起動しました。')
        else:
            await interaction.followup.send('サーバーの起動に失敗しました。screen セッションがすぐ終了しました。`run.sh` のパスや権限を確認してください。')

    @server_group.command(name='stop', description='マインクラフトサーバーを停止します')
    async def server_stop(self, interaction: discord.Interaction):
        mc = self.bot.mc_server
        if not mc.is_running:
            await interaction.response.send_message('サーバーは起動していません。')
            return

        await interaction.response.defer()
        try:
            stopped = await mc.stop()
        except Exception as e:
            await interaction.followup.send(f'サーバーの停止に失敗しました。\n```{e}```')
            return

        if stopped:
            await interaction.followup.send('サーバーを停止しました。')
            await self._notify_log('マインクラフトサーバーが停止しました。')
        else:
            await interaction.followup.send('サーバーの停止に失敗しました。')

    async def _notify_log(self, message: str):
        cfg = self.bot.config
        if cfg.log_channel_id:
            channel = self.bot.get_channel(cfg.log_channel_id)
            if channel:
                await channel.send(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(ServerCog(bot))
