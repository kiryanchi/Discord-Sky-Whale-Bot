import discord
from discord.ext import commands


class Music(commands.Cog):
    def __init__(self, app):
        super().__init__()
        self.app = app

    @commands.command('초기화')
    async def init_music_channel(self, ctx):
        await ctx.send('이 채널에 음악봇을 시작합니다.')
        await ctx.channel.purge()

        await self._music_bot_start()

    async def _muisc_bot_start(self, ctx):
        await ctx.send("___***재생목록:***___")
        await ctx.send('재생목록이 될 메시지')
        await ctx.send('버튼이 될 메시지')

def setup(app):
    app.add_cog(Music(app))
