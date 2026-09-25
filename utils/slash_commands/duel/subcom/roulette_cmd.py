import random
import disnake
from ..helpers import DuelInviteView, RussianRouletteView, GIFS_ROULETTE_SPIN

async def handle_roulette(inter: disnake.ApplicationCommandInteraction, opponent: disnake.Member):
    if opponent.id == inter.author.id:
        await inter.response.send_message("❌ You cannot play Russian Roulette against yourself!", ephemeral=True)
        return

    if opponent.bot:
        await inter.response.send_message("❌ You cannot challenge bots!", ephemeral=True)
        return

    invite_view = DuelInviteView(challenger=inter.author, opponent=opponent)
    embed = disnake.Embed(
        title="🎰 Russian Roulette Challenge!",
        description=(
            f"{opponent.mention}, you have been challenged to **Russian Roulette** by {inter.author.mention}!\n\n"
            "> ⚠️ **Warning:** The loser receives a 60-second server timeout!\n"
            "> Click **Accept Duel** below to spin the cylinder."
        ),
        color=disnake.Color.dark_red()
    )
    embed.set_thumbnail(url=inter.author.display_avatar.url)
    embed.set_footer(text="Challenge expires in 45 seconds.")

    await inter.response.send_message(content=opponent.mention, embed=embed, view=invite_view)

    timed_out = await invite_view.wait()
    if timed_out or not invite_view.accepted:
        return

    roulette_view = RussianRouletteView(inter.author, opponent)
    r_embed = disnake.Embed(
        title="🎰 Russian Roulette Initiated!",
        description=(
            "The cylinder has been spun with **1 live round** in **6 chambers**.\n\n"
            f"🎲 Coin flip decided: **{roulette_view.turn.mention}** pulls first!\n"
            "> Click the **Pull Trigger** button when ready."
        ),
        color=disnake.Color.dark_red()
    )
    r_embed.set_image(url=random.choice(GIFS_ROULETTE_SPIN))
    await inter.edit_original_response(content=None, embed=r_embed, view=roulette_view)