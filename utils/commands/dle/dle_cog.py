import disnake
from disnake.ext import commands
from utils.event.dle.storage import get_current_hero
from utils.event.dle.views import DLEView

class DLECog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="dle", aliases=["daily_hero"])
    async def dle(self, ctx: commands.Context):
        embed = disnake.Embed(
            title="🎮 DLE — Dota Daily Guess",
            description="Guess the hero of the day!\n\n Use the button below to make your guess.",
            color=disnake.Color.blurple()
        )

        await ctx.send(
            embed=embed,
            view=DLEView()
        )

    @commands.command(name="dle_gh", aliases=["dlegh"])
    @commands.has_permissions(administrator=True)
    async def dle_gh(self, ctx: commands.Context):
        """Генерація нового щоденного героя (для адміністраторів): !generate_hero"""
        from utils.event.dle.dle_cog import DLEEventCog

        dle_cog = self.bot.get_cog("DLEEventCog")
        if dle_cog:
            new_hero = dle_cog.generate_daily_hero()
            hero_name = new_hero.get("championName")
            hero_id = new_hero.get("heroId")
            await ctx.send(f"New daily hero generated: {hero_name} (ID: {hero_id})")
        else:
            await ctx.send("DLEEventCog is not loaded.")