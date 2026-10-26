from disnake.ext import commands
from .chek_rang.chek import CheckRank

class SteamVerification(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

def setup(bot: commands.Bot):
    bot.add_cog(CheckRank(bot))