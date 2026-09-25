import disnake
from disnake.ext import commands

from utils.comands.exp.subcom.rank_cmd import handle_rank
from utils.comands.exp.subcom.top_cmd import handle_top

class ExpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="rank", aliases=["lvl", "exp"])
    async def rank(self, ctx: commands.Context, member: disnake.Member = None):
        """Перевірка рівня та досвіду: !rank або !rank @user"""
        await handle_rank(ctx, member)

    @commands.command(name="top", aliases=["leaderboard", "lb"])
    async def top(self, ctx: commands.Context):
        """Таблиця лідерів сервера: !top"""
        await handle_top(ctx)

def setup(bot: commands.Bot):
    bot.add_cog(ExpCog(bot))