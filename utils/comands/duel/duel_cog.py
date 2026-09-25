import disnake
from disnake.ext import commands

from .subcom.shootout_cmd import handle_shootout
from .subcom.roulette_cmd import handle_roulette

class DuelCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="duel", aliases=["du"])
    async def duel(self, ctx: commands.Context, mode_or_user: str = None, target: disnake.Member = None):
        # 1. Довідка
        if not mode_or_user or mode_or_user.lower() in ("help", "h"):
            embed = disnake.Embed(
                title="⚔️ Duel Mini-Games",
                description=(
                    "Challenge server members to deadly shootouts:\n\n"
                    "• `!duel <@user>` — Fast 50/50 Western quickdraw shootout\n"
                    "• `!duel r <@user>` (or `!du roulette <@user>`) — Turn-based Russian roulette (loser gets 60s timeout)"
                ),
                color=disnake.Color.gold()
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            await ctx.send(embed=embed)
            return

        # 2. Російська рулетка: !duel r @user або !duel roulette @user
        if mode_or_user.lower() in ("r", "roulette"):
            opponent = target or (ctx.message.mentions[0] if ctx.message.mentions else None)
            if not opponent:
                await ctx.send("❌ You must mention an opponent: `!duel r <@user>`")
                return
            await handle_roulette(ctx, opponent)
            return

        # 3. Швидкий shootout: !duel @user
        opponent = target or (ctx.message.mentions[0] if ctx.message.mentions else None)
        if opponent:
            await handle_shootout(ctx, opponent)
            return

        await ctx.send("❌ Invalid format! Use `!duel <@user>` or `!duel r <@user>`.")

def setup(bot: commands.Bot):
    bot.add_cog(DuelCog(bot))