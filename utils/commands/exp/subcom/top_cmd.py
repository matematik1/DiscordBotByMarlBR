import os
import disnake
from disnake.ext import commands
from utils.storage import get_all_exp_data

async def handle_top(ctx: commands.Context):
    all_users = get_all_exp_data()

    if not all_users:
        await ctx.send("📊 The leaderboard is currently empty.")
        return

    guild_members_data = []
    for user_id_str, user_info in all_users.items():
        if not user_id_str.isdigit():
            continue

        member = ctx.guild.get_member(int(user_id_str))
        if member and not member.bot:
            lvl = user_info.get("lvl", 1)
            xp = user_info.get("xp", 0)
            username = user_info.get("username", member.display_name)
            guild_members_data.append((username, lvl, xp))

    guild_members_data.sort(key=lambda item: (item[1], item[2]), reverse=True)

    if not guild_members_data:
        await ctx.send("📊 No active server members found in the database.")
        return

    top_lines = []
    medals = ["🥇", "🥈", "🥉"]
    gif_filename = "logo.gif"
    gif_path = os.path.join("video", gif_filename)

    for index, (name, lvl, xp) in enumerate(guild_members_data[:10], start=1):
        rank_icon = medals[index - 1] if index <= 3 else f"`#{index}`"
        top_lines.append(f"{rank_icon} **{name}** — Lvl `{lvl}` (`{xp} XP`)")

    embed = disnake.Embed(
        title=f"🏆 Experience Leaderboard — {ctx.guild.name}",
        description="\n".join(top_lines),
        color=disnake.Color.gold()
    )
    embed.set_footer(text=f"Top 10 active members • {ctx.guild.member_count} total")

    if os.path.exists(gif_path):
        file = disnake.File(gif_path, filename=gif_filename)
        embed.set_thumbnail(url=f"attachment://{gif_filename}")
        await ctx.send(embed=embed, file=file)
    else:
        await ctx.send(embed=embed)