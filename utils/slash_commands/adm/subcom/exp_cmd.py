import disnake
from utils.storage import add_user_exp, update_user_exp_and_lvl, get_user_data
from utils.commands.exp.helpers import check_level_up

async def handle_give_exp(inter: disnake.ApplicationCommandInteraction, user: disnake.Member, amount: int):
    if amount <= 0:
        await inter.response.send_message("❌ Amount of EXP must be greater than 0!", ephemeral=True)
        return

    # Начисляем опыт и сохраняем имя
    data = add_user_exp(user.id, amount, username=user.display_name)
    current_xp = data.get("xp", 0)
    current_lvl = data.get("lvl", 1)

    # Проверяем переход на новый уровень
    remaining_xp, new_lvl, did_level_up = check_level_up(current_xp, current_lvl)
    if did_level_up:
        update_user_exp_and_lvl(user.id, remaining_xp, new_lvl, username=user.display_name)

    embed = disnake.Embed(
        title="✨ Experience Granted",
        description=(
            f"Successfully gave **{amount} XP** to {user.mention}!\n\n"
            f"• **Current Level:** `{new_lvl if did_level_up else current_lvl}`\n"
            f"• **Current XP:** `{remaining_xp if did_level_up else current_xp}`"
        ),
        color=disnake.Color.green()
    )
    await inter.response.send_message(embed=embed)

async def handle_set_lvl(inter: disnake.ApplicationCommandInteraction, user: disnake.Member, level: int):
    if level < 1:
        await inter.response.send_message("❌ Level cannot be less than 1!", ephemeral=True)
        return

    # Принудительно ставим уровень и сбрасываем опыт на 0 для этого уровня
    update_user_exp_and_lvl(user.id, 0, level, username=user.display_name)

    embed = disnake.Embed(
        title="🎖️ Level Set",
        description=f"Successfully set {user.mention}'s level to **{level}** (0 XP).",
        color=disnake.Color.gold()
    )
    await inter.response.send_message(embed=embed)