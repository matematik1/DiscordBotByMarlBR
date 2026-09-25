import disnake
from disnake.ext import commands

from .subcom.shootout_cmd import handle_shootout
from .subcom.roulette_cmd import handle_roulette

class DuelSlashCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="duel", description="Challenge members to Western shootouts or Russian Roulette")
    async def duel(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @duel.sub_command(name="shootout", description="Fast 50/50 western quickdraw shootout")
    async def shootout(
        self,
        inter: disnake.ApplicationCommandInteraction,
        user: disnake.Member = commands.Param(description="Member to challenge to a shootout")
    ):
        await handle_shootout(inter, user)

    @duel.sub_command(name="roulette", description="Turn-based Russian Roulette (loser gets 60s timeout)")
    async def roulette(
        self,
        inter: disnake.ApplicationCommandInteraction,
        user: disnake.Member = commands.Param(description="Member to challenge to Russian Roulette")
    ):
        await handle_roulette(inter, user)