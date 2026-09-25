import disnake
from disnake.ext import commands

from .subcom.profile_cmd import handle_profile
from .subcom.connect_cmd import handle_connect
from .subcom.roll_cmd import handle_roll
from .subcom.random_cmd import handle_random

class DotaSlashCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="dota", description="Dota 2 commands and profile tools")
    async def dota(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @dota.sub_command(name="profile", description="View OpenDota stats and recent matches")
    async def profile(
        self,
        inter: disnake.ApplicationCommandInteraction,
        steam_id: int = commands.Param(default=None, description="32-bit Dota Friend ID")
    ):
        await handle_profile(inter, steam_id)

    @dota.sub_command(name="connect", description="Link your Steam account")
    async def connect(
        self,
        inter: disnake.ApplicationCommandInteraction,
        account_id: int = commands.Param(description="Your 32-bit Dota Friend ID")
    ):
        await handle_connect(inter, account_id)

    @dota.sub_command(name="roll", description="Roll animated dice")
    async def roll(
        self,
        inter: disnake.ApplicationCommandInteraction,
        min_val: int = commands.Param(default=1, description="Minimum value"),
        max_val: int = commands.Param(default=100, description="Maximum value")
    ):
        await handle_roll(inter, min_val, max_val)

    @dota.sub_command(name="random", description="Generate random hero & inventory build")
    async def random(self, inter: disnake.ApplicationCommandInteraction):
        await handle_random(inter)