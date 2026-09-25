import disnake
from utils.storage import get_user_data
from ..helpers import get_exp_for_lvl, create_progress_bar

async def handle_rank(inter: disnake.ApplicationCommandInteraction, target: disnake.Member | None):
    member = target if target else inter.author

    if member.bot:
        await inter.response.send_message("❌ Bots do not participate in the experience system!", ephemeral=True)
        return

    data = get_user_data(member.id)
    current_xp = data.get("xp", 0)
    current_lvl = data.get("lvl", 1)
    
    # Використовуємо твою формулу розрахунку вартості рівня
    needed_xp = get_exp_for_lvl(current_lvl)

    progress_bar = create_progress_bar(current_xp, needed_xp, length=12)
    percent = int((current_xp / needed_xp) * 100) if needed_xp > 0 else 0

    embed = disnake.Embed(
        title=f"🎖️ Level Progress — {member.display_name}",
        description=(
            f"**Level:** `{current_lvl}`\n"
            f"**Experience:** `{current_xp} / {needed_xp} XP` (`{percent}%`)\n\n"
            f"> `{progress_bar}`"
        ),
        color=disnake.Color.purple()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"Requested by {inter.author.display_name}")

    await inter.response.send_message(embed=embed)