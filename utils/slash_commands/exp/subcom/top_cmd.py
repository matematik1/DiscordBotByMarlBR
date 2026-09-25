import disnake
from utils.storage import get_all_users_data

async def handle_top(inter: disnake.ApplicationCommandInteraction):
    all_users = get_all_users_data()

    if not all_users:
        await inter.response.send_message("📊 The leaderboard is currently empty.", ephemeral=True)
        return

    # Фільтруємо лише учасників поточного сервера та сортуємо: спочатку рівень, потім досвід
    guild_members_data = []
    for user_id_str, user_info in all_users.items():
        if not user_id_str.isdigit():
            continue

        member = inter.guild.get_member(int(user_id_str))
        if member and not member.bot:
            lvl = user_info.get("lvl", 1)
            xp = user_info.get("xp", 0)
            username = user_info.get("username", member.display_name)
            guild_members_data.append((username, lvl, xp))

    guild_members_data.sort(key=lambda item: (item[1], item[2]), reverse=True)

    if not guild_members_data:
        await inter.response.send_message("📊 No active server members found in the database.", ephemeral=True)
        return

    top_lines = []
    medals = ["🥇", "🥈", "🥉"]

    for index, (name, lvl, xp) in enumerate(guild_members_data[:10], start=1):
        rank_icon = medals[index - 1] if index <= 3 else f"`#{index}`"
        top_lines.append(f"{rank_icon} **{name}** — Lvl `{lvl}` (`{xp} XP`)")

    embed = disnake.Embed(
        title=f"🏆 Experience Leaderboard — {inter.guild.name}",
        description="\n".join(top_lines),
        color=disnake.Color.gold()
    )
    embed.set_footer(text=f"Top 10 active members • {inter.guild.member_count} total")

    await inter.response.send_message(embed=embed)