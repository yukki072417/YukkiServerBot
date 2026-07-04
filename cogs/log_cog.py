import discord
from discord import app_commands
from discord.ext import commands


class LogCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    log_group = app_commands.Group(name='log', description='ログ設定コマンド')

    @log_group.command(name='channel', description='ログを送信するチャネルIDを設定します')
    @app_commands.describe(channel_id='ログ送信先チャネルのID')
    async def log_channel(self, interaction: discord.Interaction, channel_id: str):
        try:
            cid = int(channel_id)
        except ValueError:
            await interaction.response.send_message('無効なチャネルIDです。数字のIDを指定してください。', ephemeral=True)
            return

        channel = self.bot.get_channel(cid)
        if channel is None:
            await interaction.response.send_message('指定されたチャネルが見つかりません。BotがそのチャネルのあるサーバーにいるかAを確認してください。', ephemeral=True)
            return

        self.bot.config.log_channel_id = cid
        self.bot.config.save()
        await interaction.response.send_message(f'ログチャネルを {channel.mention} に設定しました。')

    @log_group.command(name='send', description='入退出ログのDiscord送信を切り替えます')
    @app_commands.describe(enabled='true で有効、false で無効')
    async def log_send(self, interaction: discord.Interaction, enabled: bool):
        if enabled and self.bot.config.log_channel_id is None:
            await interaction.response.send_message(
                '❌ ログチャネルが設定されていません。先に `/log channel <ID>` で設定してください。',
                ephemeral=True,
            )
            return

        self.bot.config.log_send_enabled = enabled
        self.bot.config.save()
        status = '有効' if enabled else '無効'
        await interaction.response.send_message(f'入退出ログの送信を **{status}** にしました。')


async def setup(bot: commands.Bot):
    await bot.add_cog(LogCog(bot))
