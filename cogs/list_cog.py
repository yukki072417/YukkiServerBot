import os
import discord
from discord import app_commands
from discord.ext import commands

from minecraft.rcon import RconClient, RconError


class ListCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='list', description='サーバーにいるプレイヤー一覧を表示します')
    async def player_list(self, interaction: discord.Interaction):
        mc = self.bot.mc_server
        if not mc.is_running:
            await interaction.response.send_message('サーバーは起動していません。')
            return

        host = os.environ.get('MC_RCON_HOST', 'localhost')
        port = int(os.environ.get('MC_RCON_PORT', '25575'))
        password = os.environ.get('MC_RCON_PASSWORD', '')

        if not password:
            await interaction.response.send_message(
                'RCON パスワードが設定されていません。`.env` の `MC_RCON_PASSWORD` を設定してください。',
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        try:
            async with RconClient(host, port, password) as rcon:
                response = await rcon.send_command('list')
        except RconError as e:
            await interaction.followup.send(f'RCON 接続に失敗しました。\n```{e}```')
            return
        except Exception as e:
            await interaction.followup.send(f'エラーが発生しました。\n```{e}```')
            return

        await interaction.followup.send(f'👥 {response}')


async def setup(bot: commands.Bot):
    await bot.add_cog(ListCog(bot))
