import disnake
from utils.storage import get_all_users_data
from utils.comands.dota.helpers import update_member_dota_role

async def sync_all_guild_dota_roles(guild: disnake.Guild) -> tuple[int, int]:
    """
    Масово синхронізує ролі Dota 2 для всіх верифікованих учасників гільдії.
    Повертає кортеж (успішно_оновлено, пропущено/помилок).
    """
    users_data = get_all_users_data()
    updated_count = 0
    failed_count = 0

    for member in guild.members:
        if member.bot:
            continue

        user_info = users_data.get(str(member.id))
        if not user_info or not user_info.get("steam_id"):
            continue

        rank_tier = user_info.get("rank_tier")
        role = await update_member_dota_role(member, rank_tier)
        if role:
            updated_count += 1
        else:
            failed_count += 1

    return updated_count, failed_count