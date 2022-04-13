import discord
from db import DB
from discord.ext import commands, tasks
from itertools import cycle
import os

from Cogs.Music import Music

TOKEN = open("token", "r").readline()
GAME_LIST = cycle(["재획", "유튜브 검색", "일", "모교는"])

db = DB()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

for filename in os.listdir("Cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"Cogs.{filename[:-3]}")


@bot.event
async def on_ready():
    @tasks.loop(minutes=30)
    async def change_game():
        await bot.change_presence(activity=discord.Game(next(GAME_LIST)))

    print("MusicpleStory Bot Activate")
    print(f"bot name: {bot.user.name}")
    print("--------------------------")
    change_game.start()

    channel = bot.get_channel(962232434613710878)
    await Music._init_channel(channel)


@bot.event
async def on_message(msg):
    return


@bot.command(name="로드")
@commands.has_permissions(administrator=True)
async def load_commands(ctx, extension):
    bot.load_extension(f"Cogs.{extension}")
    await ctx.send(f":white_check_mark: {extension}을(를) 로드했습니다.")


@bot.command(name="언로드")
@commands.has_permissions(administrator=True)
async def unload_commands(ctx, extension):
    bot.unload_extension(f"Cogs.{extension}")
    await ctx.send(f":white_check_mark: {extension}을(를) 언로드했습니다.")


@bot.command(name="리로드")
@commands.has_permissions(administrator=True)
async def reload_commands(ctx, extension=None):
    if extension is None:
        for filename in os.listdir("Cogs"):
            if filename.endswith(".py"):
                bot.unload_extension(f"Cogs.{filename[:-3]}")
                bot.load_extension(f"Cogs.{filename[:-3]}")
                await ctx.send(f":white_check_mark: {filename[:-3]}을(를) 다시 불러왔습니다!")
    else:
        bot.unload_extension(f"Cogs.{extension}")
        bot.load_extension(f"Cogs.{extension}")
        await ctx.send(f":white_check_mark: {extension}을(를) 다시 불러왔습니다!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("권한이 없어요", mention_author=True)

    if isinstance(error, commands.CommandNotFound):
        await ctx.reply("그런 명령어는 없어요", mention_author=True)


if __name__ == "__main__":
    bot.run(TOKEN)
    db.close()
