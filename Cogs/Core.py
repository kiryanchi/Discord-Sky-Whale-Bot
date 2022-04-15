import discord
import re
from discord.ext import commands

from Modules.Music.utils.embeds import Embed

SPACE = "\u17B5"


class Core(commands.Cog):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app

    @commands.command(name="클리어")
    async def clear(self, ctx):
        await ctx.channel.purge()

    @commands.command(name="핑")
    async def ping(self, ctx):
        await ctx.send("pong")

    @commands.command(name="q")
    async def queue(self, ctx):
        await ctx.send(self.queue.queue)

    @commands.command(name="embed")
    async def embed(self, ctx):
        cur = "ssaf"
        nex = "> "
        for i in range(10):
            nex += f"\n> {SPACE}[{i+1}] ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ"
            nex += f"\n> {SPACE}[{i+1}] ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ"

        nex += f"\n> {SPACE}"
        embed = Embed.playlist(cur, nex)
        await ctx.send("aa", embed=embed)

    @commands.command(name="embed2")
    async def embed2(self, ctx):
        cur = "ssaf"
        nex = "> "
        text_list = [
            "asdfafasdfadfasdfasdfadfasdfjalsdfkjasdlkfjadf",
            "ㅁㄴㅇ럼ㅇ러밍ㄴ로민아럼니아러민아럼니ㅏㅇ럼ㄴ아러ㅣㅁㄴ얼미아렁닐",
            "asdasdfㅁㄴㅇㄹㅁㄴ어ㅏㅣㄹ밍asdfnalskdfㅁ니아룸닝ㄹ",
            "🔥불 지르기 쌉가능한 노래🔥 AJR - Burn The House Down [가사/해석/lyrics]",
            "가나다라",
            "Cloudless",
        ]
        for i in range(len(text_list)):
            text = self.wrap(text_list[i])
            nex += f"\n> {SPACE}[{i+1}] {text}"

        nex += f"\n> {SPACE}"
        embed = Embed.playlist(cur, nex)
        await ctx.send(embed=embed)

    def wrap(self, text):
        def is_korean(char):
            hangul = re.compile("[^ㄱ-ㅣ가-힣]+")
            result = hangul.sub("", char)
            return result != ""

        word_cnt = 0
        result_text = ""
        for char in text:
            if word_cnt > 42:
                result_text += "..."
                break

            if is_korean(char):
                word_cnt += 2
            else:
                word_cnt += 1
            result_text += char
        return result_text


def setup(app):
    app.add_cog(Core(app))
