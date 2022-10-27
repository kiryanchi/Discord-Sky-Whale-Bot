from __future__ import annotations

from typing import TYPE_CHECKING

from discord import app_commands
from discord.ext import commands

from src.cogs.util.view import SuggestionModal

if TYPE_CHECKING:
    from src.whale import Whale
    from discord import Interaction


class Util(commands.Cog):
    def __init__(self, bot: Whale) -> None:
        self.bot = bot

    @app_commands.command(name="건의", description="개발자에게 질문이나 건의합니다.")
    async def suggestion_command(self, interaction: Interaction):
        await interaction.response.send_modal(SuggestionModal(self.bot))


async def setup(bot: Whale) -> None:
    await bot.add_cog(Util(bot))
