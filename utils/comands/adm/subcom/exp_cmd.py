import disnake
from disnake.ext import commands
from utils.storage import add_user_exp, update_user_exp_and_lvl
from utils.comands.exp.helpers import check_level_up
from utils.comands.exp.helpers import check_level_up

async def handle_give_exp(ctx: commands.Context, user: disnake.Member, amount: int):
    if amount <= 0:
        await ctx.send("❌ Amount of EXP must be greater than 0!")
        return

    data = add_user_exp(user.id, amount, username=user.display_name)
    current_xp = data.get("xp", 0)
    current_lvl = data.get("lvl", 1)

    remaining_xp, new_lvl, did_change = check_level_up(current_xp, current_lvl)
    if did_change:
        update_user_exp_and_lvl(user.id, remaining_xp, new_lvl, username=user.display_name)

    embed = disnake.Embed(
        title="✨ Experience Granted",
        description=(
            f"Successfully granted **{amount} XP** to {user.mention}!\n\n"
            f"• **Current Level:** `{new_lvl if did_change else current_lvl}`\n"
            f"• **Current XP:** `{remaining_xp if did_change else current_xp}`"
        ),
        color=disnake.Color.green()
    )
    await ctx.send(embed=embed)

async def handle_set_lvl(ctx: commands.Context, user: disnake.Member, level: int):
    if level < 1:
        await ctx.send("❌ Level cannot be less than 1!")
        return

    update_user_exp_and_lvl(user.id, 0, level, username=user.display_name)

    embed = disnake.Embed(
        title="🎖️ Level Set",
        description=f"Successfully set {user.mention}'s level to **{level}** (0 XP).",
        color=disnake.Color.gold()
    )
    await ctx.send(embed=embed)