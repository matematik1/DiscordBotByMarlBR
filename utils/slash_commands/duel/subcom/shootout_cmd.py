import random
import asyncio
import disnake
from ..helpers import DuelInviteView, GIFS_DUEL_START, GIFS_DUEL_SHOOT

async def handle_shootout(inter: disnake.ApplicationCommandInteraction, opponent: disnake.Member):
    if opponent.id == inter.author.id:
        await inter.response.send_message("❌ You cannot duel yourself!", ephemeral=True)
        return

    if opponent.bot:
        await inter.response.send_message("❌ You cannot duel bots!", ephemeral=True)
        return

    invite_view = DuelInviteView(challenger=inter.author, opponent=opponent)
    embed = disnake.Embed(
        title="⚔️ Western Shootout Challenge!",
        description=(
            f"{opponent.mention}, you have been challenged to a **Western Shootout** by {inter.author.mention}!\n\n"
            "> Click **Accept Duel** below to draw your revolvers."
        ),
        color=disnake.Color.gold()
    )
    embed.set_thumbnail(url=inter.author.display_avatar.url)
    embed.set_footer(text="Challenge expires in 45 seconds.")

    await inter.response.send_message(content=opponent.mention, embed=embed, view=invite_view)

    timed_out = await invite_view.wait()
    if timed_out or not invite_view.accepted:
        return

    # Анимация дуэли
    anim_embed = disnake.Embed(
        title="🤠 Duel Started! Draw!",
        description=f"**{inter.author.display_name}** and **{opponent.display_name}** step 10 paces apart...",
        color=disnake.Color.dark_gray()
    )
    anim_embed.set_image(url=random.choice(GIFS_DUEL_START))
    await inter.edit_original_response(content=None, embed=anim_embed, view=None)

    await asyncio.sleep(3.5)

    winner = random.choice([inter.author, opponent])
    loser = opponent if winner.id == inter.author.id else inter.author

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

    await inter.edit_original_response(embed=final_embed)