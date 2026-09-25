import random
import asyncio
import disnake
from disnake.ext import commands
from ..helpers import DuelInviteView, GIFS_DUEL_START, GIFS_DUEL_SHOOT

async def handle_shootout(ctx: commands.Context, opponent: disnake.Member):
    if opponent.id == ctx.author.id:
        await ctx.send("❌ You cannot duel yourself!")
        return

    if opponent.bot:
        await ctx.send("❌ You cannot duel bots!")
        return

    invite_view = DuelInviteView(challenger=ctx.author, opponent=opponent)
    embed = disnake.Embed(
        title="⚔️ Western Shootout Challenge!",
        description=(
            f"{opponent.mention}, you have been challenged to a **Western Shootout** by {ctx.author.mention}!\n\n"
            "> Click **Accept Duel** below to draw your revolvers."
        ),
        color=disnake.Color.gold()
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_footer(text="Challenge expires in 45 seconds.")

    msg = await ctx.send(content=opponent.mention, embed=embed, view=invite_view)

    timed_out = await invite_view.wait()
    if timed_out or not invite_view.accepted:
        return

    anim_embed = disnake.Embed(
        title="🤠 Duel Started! Draw!",
        description=f"**{ctx.author.display_name}** and **{opponent.display_name}** step 10 paces apart...",
        color=disnake.Color.dark_gray()
    )
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
    final_embed.set_image(url=random.choice(GIFS_DUEL_SHOOT))
    final_embed.set_footer(text="Honor restored on the battlefield.")

    await msg.edit(embed=final_embed)