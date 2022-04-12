import discord
from db import DB
from discord.ext import tasks
from discord_components import ComponentsBot
from itertools import cycle
import os

TOKEN = open("token", "r").readline()
GAME_LIST = cycle(["재획", "유튜브 검색", "일", "모교는"])

db = DB()
intents = discord.Intents.all()
bot = ComponentsBot(command_prefix=".", intents=intents)

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


@bot.event
async def on_guild_remove(guild):
    # TODO: guild 탈퇴하면 db에서 server id 와 관련된 모든 데이터 삭제
    pass


@bot.event
async def on_message(message):
    # 봇이면 종료
    if message.author == bot.user:
        return

    music_channel_data = db.select_music_channel(message.guild.id)
    if music_channel_data and music_channel_data[0][1] == message.channel.id:
        if message.content.startswith("."):
            return

    if message.content.startswith("."):
        await bot.process_commands(message)


@bot.command(name="로드")
async def load_commands(ctx, extension):
    bot.load_extension(f"Cogs.{extension}")
    await ctx.send(f":white_check_mark: {extension}을(를) 로드했습니다.")


@bot.command(name="언로드")
async def unload_commands(ctx, extension):
    bot.unload_extension(f"Cogs.{extension}")
    await ctx.send(f":white_check_mark: {extension}을(를) 언로드했습니다.")


@bot.command(name="리로드")
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


if __name__ == "__main__":
    bot.run(TOKEN)
    db.close()
