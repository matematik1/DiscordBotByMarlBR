import disnake
from disnake.ext import commands

from .subcom.profile_cmd import handle_profile
from .subcom.connect_cmd import handle_connect
from .subcom.roll_cmd import handle_roll
from .subcom.random_cmd import handle_random

class DotaCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="dota", aliases=["d"], invoke_without_command=True)
    async def dota(self, ctx: commands.Context):
        # Оформлене меню допомоги в стилі інших команд
        embed = disnake.Embed(
            title="🎮 Dota 2 Utilities",
            description=(
                "Manage your Dota 2 profile, stats, and mini-games:\n\n"
                "• `!d connect <AccountID>` — Link your Steam account\n"
                "• `!d profile [AccountID]` — View OpenDota stats and recent matches\n"
                "• `!d roll [min] [max]` — Roll animated dice\n"
                "• `!d random` — Generate random hero & inventory build"
            ),
            color=disnake.Color.blue()
        )
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        await ctx.send(embed=embed)

    @dota.command(name="profile", description="View OpenDota stats and recent matches", aliases=["p"])
    async def profile(self, ctx: commands.Context, steam_id: int = None):
        await handle_profile(ctx, steam_id)

    @dota.command(name="connect", description="Link your Steam account", aliases=["c"])
    async def connect(self, ctx: commands.Context, account_id: int):
        await handle_connect(ctx, account_id)

    @dota.command(name="roll", description="Roll animated dice")
    async def roll(self, ctx: commands.Context, min_val: int = 1, max_val: int = 100):
        await handle_roll(ctx, min_val, max_val)

    @dota.command(name="random", description="Generate random hero & inventory build", aliases=["r"])
    async def random(self, ctx: commands.Context):
        await handle_random(ctx)

def setup(bot):
    bot.add_cog(DotaCog(bot))