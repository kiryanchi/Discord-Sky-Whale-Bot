import discord
from db import DB
from discord.ext import commands, tasks
from itertools import cycle
import os

from Modules.Music.components.queue import Queue

TOKEN = open("token", "r").readline()
GAME_LIST = cycle(["재획", "유튜브 검색", "일", "모교는"])

db = DB()
q = Queue()
intents = discord.Intents.all()
app = commands.Bot(command_prefix=".", intents=intents)

for filename in os.listdir("Cogs"):
    if filename.endswith(".py"):
        app.load_extension(f"Cogs.{filename[:-3]}")


@app.event
async def on_ready():
    @tasks.loop(minutes=30)
    async def change_game():
        await app.change_presence(activity=discord.Game(next(GAME_LIST)))

    print("MusicpleStory app Activate")
    print(f"app name: {app.user.name}")
    print("--------------------------")
    change_game.start()


@app.event
async def on_message(message):
    if message.author == app.user:
        return

    # 음악 채널에 명령어를 사용하면 종료
    if (
        q[message.guild.id]
        and message.channel.id == q[message.guild.id].get_channel_id()
    ):
        if message.content.startswith("."):
            return

    if message.content.startswith("."):
        await app.process_commands(message)
        return


@app.command(name="로드")
@commands.has_permissions(administrator=True)
async def load_commands(ctx, extension):
    app.load_extension(f"Cogs.{extension}")
    await ctx.send(f":white_check_mark: {extension}을(를) 로드했습니다.")


@app.command(name="언로드")
@commands.has_permissions(administrator=True)
async def unload_commands(ctx, extension):
    app.unload_extension(f"Cogs.{extension}")
    await ctx.send(f":white_check_mark: {extension}을(를) 언로드했습니다.")


@app.command(name="리로드")
@commands.has_permissions(administrator=True)
async def reload_commands(ctx, extension=None):
    if extension is None:
        for filename in os.listdir("Cogs"):
            if filename.endswith(".py"):
                app.unload_extension(f"Cogs.{filename[:-3]}")
                app.load_extension(f"Cogs.{filename[:-3]}")
                await ctx.send(f":white_check_mark: {filename[:-3]}을(를) 다시 불러왔습니다!")
    else:
        app.unload_extension(f"Cogs.{extension}")
        app.load_extension(f"Cogs.{extension}")
        await ctx.send(f":white_check_mark: {extension}을(를) 다시 불러왔습니다!")


@app.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("권한이 없어요", mention_author=True)

    if isinstance(error, commands.CommandNotFound):
        await ctx.reply("그런 명령어는 없어요", mention_author=True)


if __name__ == "__main__":
    app.run(TOKEN)
    db.close()
