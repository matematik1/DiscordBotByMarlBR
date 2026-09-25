import random
import asyncio
import random
import disnake
from disnake.ext import commands

from utils.comands.duel.helpers import (
    DuelInviteView,
    RussianRouletteView,
    GIFS_DUEL_START,
    GIFS_DUEL_SHOOT,
    GIFS_ROULETTE_SPIN
)

class DuelCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["dzone", "fight"])
    async def duel(self, ctx: commands.Context, sub_or_user: str = None, target_user: disnake.Member = None):
        # 1. Меню довідки
        if not sub_or_user or sub_or_user.lower() in ("help", "h"):
            embed = disnake.Embed(
                title="⚔️ Duel & Russian Roulette Arena",
                description="Challenge other server members to instant duels or step-by-step Russian Roulette:",
                color=disnake.Color.dark_gold()
            )
            embed.add_field(
                name="• `!duel @user`",
                value="> Fast 50/50 western shootout with animated reload and standoff results.",
                inline=False
            )
            embed.add_field(
                name="• `!duel rr @user` (or `roulette`)",
                value="> Turn-based Russian Roulette with a 6-chamber revolver. Loser takes a 60s timeout!",
                inline=False
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
            return

        # 2. Визначення режиму гри та опонента
        is_roulette = sub_or_user.lower() in ("rr", "roulette", "r")
        opponent = target_user if is_roulette else None

        if not is_roulette and ctx.message.mentions:
            opponent = ctx.message.mentions[0]
        elif not opponent and ctx.message.mentions:
            opponent = ctx.message.mentions[0]

        if not opponent:
            await ctx.send("❌ You must tag a valid member to challenge! Example: `!duel @user` or `!duel rr @user`")
            return

        if opponent.id == ctx.author.id:
            await ctx.send("❌ You cannot duel yourself!")
            return

        if opponent.bot:
            await ctx.send("❌ You cannot duel bots!")
            return

        # 3. Надсилання виклику
        invite_view = DuelInviteView(challenger=ctx.author, opponent=opponent)
        game_name = "Russian Roulette" if is_roulette else "Western Shootout"

        embed = disnake.Embed(
            title=f"⚔️ {game_name} Challenge!",
            description=(
                f"{opponent.mention}, you have been challenged to a **{game_name}** by {ctx.author.mention}!\n\n"
                "> Click **Accept Duel** below to start the game."
            ),
            color=disnake.Color.gold()
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(text="Challenge expires in 45 seconds.")

        msg = await ctx.send(content=opponent.mention, embed=embed, view=invite_view)

        timed_out = await invite_view.wait()
        if timed_out or not invite_view.accepted:
            return

        # --- РОСІЙСЬКА РУЛЕТКА ---
        if is_roulette:
            roulette_view = RussianRouletteView(ctx.author, opponent)
            r_embed = disnake.Embed(
                title="🎰 Russian Roulette Initiated!",
                description=(
                    "The cylinder has been spun with **1 live round** in **6 chambers**.\n\n"
                    f"🎲 Coin flip decided: **{roulette_view.turn.mention}** pulls first!\n"
                    "> Click the **Pull Trigger** button when ready."
                ),
                color=disnake.Color.dark_red()
            )
            # Рандомний барабан
            r_embed.set_image(url=random.choice(GIFS_ROULETTE_SPIN))
            await msg.edit(content=None, embed=r_embed, view=roulette_view)
            return

        # --- КЛАСИЧНА ДУЕЛЬ 50/50 ---
        anim_embed = disnake.Embed(
            title="🤠 Duel Started! Draw!",
            description=f"**{ctx.author.display_name}** and **{opponent.display_name}** step 10 paces apart...",
            color=disnake.Color.dark_gray()
        )
        # Рандомний початок перестрілки
        anim_embed.set_image(url=random.choice(GIFS_DUEL_START))
        await msg.edit(content=None, embed=anim_embed, view=None)

        await asyncio.sleep(3.5)

        winner = random.choice([ctx.author, opponent])
        loser = opponent if winner.id == ctx.author.id else ctx.author

        final_embed = disnake.Embed(
            title="💥 Quickdraw Result!",
            description=(
                f"**{winner.mention}** drew faster and hit the mark!\n\n"
                f"🏆 **Winner:** {winner.mention}\n"
                f"💀 **Fallen:** {loser.mention}"
            ),
            color=disnake.Color.green()
        )
        # Рандомне влучання/постріл
        final_embed.set_image(url=random.choice(GIFS_DUEL_SHOOT))
        final_embed.set_footer(text="Honor restored on the battlefield.")

        await msg.edit(embed=final_embed)

def setup(bot: commands.Bot):
    bot.add_cog(DuelCog(bot))