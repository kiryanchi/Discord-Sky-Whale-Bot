import discord
from discord.ext import commands

SPACE = "\u17B5"


class Core(commands.Cog, name="기본"):
    """
    하늘 고래의 기본 명령어 카테고리입니다.
    """

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.command(name="role")
    async def role(self, ctx):
        info = await self.bot.application_info()
        find = False
        bot_role = None
        for role in ctx.guild.roles:
            print(role)
            for member in role.members:
                print(member)
                if member.id == info.id:
                    find = True
            print(find)
            if find:
                bot_role = role

        print(bot_role)
        if bot_role:
            await bot_role.edit(colour=discord.Color.dark_gold())


#   @commands.command(name="도움", help="도움말을 보여줍니다", usage=".도움")
#   async def help(self, ctx, func=None):
#       cog_list = ["기본", "음악"]
#       if func is None:
#           embed = discord.Embed(
#               title="하늘 고래 도우미", description="명령어 앞에 `.` 를 꼭 붙여주세요."
#           )
#
#           for cog in cog_list:
#               cog_data = self.bot.get_cog(cog)
#               command_list = cog_data.get_commands()
#               embed.add_field(
#                   name=cog,
#                   value=" ".join([command.name for command in command_list]),
#                   inline=True,
#               )
#           embed.set_footer(text="명령어를 자세히 보려면 .도움 명령어 를 입력해주세요. ex) .도움 초기화")
#           await ctx.send(embed=embed)
#       else:
#           command_notfound = True
#           for _title, cog in self.bot.cogs.items():
#               if not command_notfound:
#                   break
#
#               else:
#                   for title in cog.get_commands():
#                       if title.name == func:
#                           cmd = self.bot.get_command(title.name)
#                           embed = discord.Embed(
#                               title=f"명령어 : {cmd.name}", description=cmd.help
#                           ).add_field(name="사용법", value=cmd.usage)
#                           await ctx.send(embed=embed)
#                           command_notfound = False
#                           break
#                       else:
#                           command_notfound = True
#           if command_notfound:
#               if func in cog_list:
#                   cog_data = self.bot.get_cog(func)
#                   command_list = cog_data.get_commands()
#                   embed = discord.Embed(
#                       title=f"카테고리: {cog_data.qualified_name}",
#                       description=cog_data.description,
#                   ).add_field(
#                       name="명령어들",
#                       value=", ".join([command.name for command in command_list]),
#                   )
#                   await ctx.send(embed=embed)
#               else:
#                   await ctx.send("그런 이름의 명렁어나 카테고리는 없습니다.")


def setup(bot):
    bot.add_cog(Core(bot))
