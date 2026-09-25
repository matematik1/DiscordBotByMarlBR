import disnake
from disnake.ext import commands

from utils.storage import get_user_exp
from utils.commands.exp.helpers import get_exp_for_lvl, create_progress_bar

async def handle_rank(ctx: commands.Context, target: disnake.Member | None):
    member = target if target else ctx.author

    if member.bot:
        await ctx.send("❌ Bots do not participate in the experience system!")
        return

    # Використовуємо правильну функцію для отримання EXP
    data = get_user_exp(member.id)
    current_xp = data.get("xp", 0)
    current_lvl = data.get("lvl", 1)
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
    embed.set_footer(text=f"Requested by {ctx.author.display_name}")

    await ctx.send(embed=embed)