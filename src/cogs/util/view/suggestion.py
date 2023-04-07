from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ui, TextStyle, Interaction

from setting import FEEDBACK_CHANNEL_ID

if TYPE_CHECKING:
    from src.extended_bot import ExtendedBot


class SuggestionModal(ui.Modal, title="건의하기"):
    name = ui.TextInput(label="제목", placeholder="제목을 입력해주세요...")

    suggestion = ui.TextInput(
        label="무엇을 건의하고 싶으신가요?",
        style=TextStyle.long,
        placeholder="건의 내용을 작성해주세요...",
        required=True,
        max_length=400,
    )

    def __init__(self, bot: ExtendedBot):
        super().__init__()
        self.feedback_channel = bot.get_channel(FEEDBACK_CHANNEL_ID)

    async def on_submit(self, interaction: Interaction) -> None:
        await self.feedback_channel.send(
            f"길드: {interaction.guild} | {interaction.guild_id}\n유저: {interaction.user.name} | {interaction.user.id}\n{self.suggestion.value}"
        )
        await interaction.response.send_message(
            f"소중한 피드백 감사합니다! 봇 개발에 큰 도움이 됩니다.", ephemeral=True
        )

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        await interaction.response.send_message("건의하실 내용이 생기면 언제든지 얘기해주세요!")
