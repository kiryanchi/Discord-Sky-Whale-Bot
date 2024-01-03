from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

from setting import ADMIN_GUILD_ID
from src.components.music import Music
from src.components.search import Search
from src.db.music_channel import MusicChannel
from src.util.function import get_info
from src.util.log import logger

if TYPE_CHECKING:
    from discord import Message

    from src.extended_bot import ExtendedBot


class AdminCog(commands.Cog):
    def __init__(self, bot: ExtendedBot):
        self.bot = bot
        self.search = Search(bot)
        logger.debug("MusicCog 초기화 완료")

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        if message.guild.id != ADMIN_GUILD_ID:
            return

        if message.content.startswith("#@!길드 추가"):
            guild_ids = message.content.split(' ')[2:]
            print(guild_ids)
            for guild_id in guild_ids:
                print(guild_id)
                added_guild_id = int(guild_id)
                if added_guild_id in self.bot.musics:
                    await message.channel.send(f"이미 {added_guild_id}는 있음")
                    continue

                guild = self.bot.get_guild(added_guild_id)
                if guild:
                    is_find = False
                    # 하늘 고래 채널을 찾으면 그냥 Music 초기화
                    for channel in guild.channels:
                        if channel.name == '하늘-고래':
                            self.bot.musics[channel.guild.id] = await Music.new(self.bot, channel)
                            if not MusicChannel.get(added_guild_id):
                                MusicChannel.add(MusicChannel(guild_id=channel.guild.id, channel_id=channel.id))
                            is_find = True
                            break

                    # 못 찾으면
                    if not is_find:
                        channel = await guild.create_text_channel(name="하늘-고래")
                        self.bot.musics[channel.guild.id] = await Music.new(self.bot, channel)
                        MusicChannel.add(MusicChannel(guild_id=channel.guild.id, channel_id=channel.id))
                        logger.info(f"{get_info(guild)} 음악 채널 생성")


async def setup(bot: ExtendedBot) -> None:
    await bot.add_cog(AdminCog(bot))
