import disnake
from disnake.ext import commands

from .subcom.rank_cmd import handle_rank
from .subcom.top_cmd import handle_top

class ExpSlashCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="exp", description="Experience and leveling system")
    async def exp(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @exp.sub_command(name="rank", description="Check your or another member's level and XP progress")
    async def rank(
        self,
        inter: disnake.ApplicationCommandInteraction,
        user: disnake.Member = commands.Param(default=None, description="Target member (leave empty for yourself)")
    ):
        await handle_rank(inter, user)

    @exp.sub_command(name="top", description="Display the server experience leaderboard")
    async def top(self, inter: disnake.ApplicationCommandInteraction):
        await handle_top(inter)