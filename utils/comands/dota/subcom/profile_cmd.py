import aiohttp
import disnake
from disnake.ext import commands

from utils.storage import get_user_steam_id
from utils.comands.dota.helpers import format_rank_tier, ProfileLinksView, update_member_dota_role

async def handle_profile(ctx: commands.Context, steam_id: int | None):
    account_id = steam_id if steam_id else get_user_steam_id(ctx.author.id)

    if not account_id:
        await ctx.send("❌ **No linked account found!**\nUse `!dota connect <steam_id>` first, or pass a Steam ID: `!dota profile <steam_id>`")
        return

    msg = await ctx.send("⏳ Fetching Dota 2 player profile...")

    base_url = f"https://api.opendota.com/api/players/{account_id}"
    headers = {"User-Agent": "Mozilla/5.0"}

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(base_url, timeout=10) as r1, \
                       session.get(f"{base_url}/wl", timeout=10) as r2, \
                       session.get(f"{base_url}/recentMatches", timeout=10) as r3:

                if r1.status != 200:
                    await msg.edit(content="❌ Failed to fetch player profile. Check if your profile is public.")
                    return

                player_data = await r1.json()
                wl_data = await r2.json() if r2.status == 200 else {"win": 0, "lose": 0}
                recent_matches = await r3.json() if r3.status == 200 else []
        except Exception as e:
            print(f"Error fetching Dota profile: {e}")
            await msg.edit(content="❌ Error connecting to OpenDota API.")
            return

    profile_info = player_data.get("profile") or {}
    player_name = profile_info.get("personaname", "Unknown Player")
    avatar_url = profile_info.get("avatarfull")
    loc_country = profile_info.get("loccountrycode") or "🌍"
    rank_tier = player_data.get("rank_tier")
    rank_str = format_rank_tier(rank_tier)

    wins = wl_data.get("win", 0)
    losses = wl_data.get("lose", 0)
    total_matches = wins + losses
    winrate = (wins / total_matches * 100) if total_matches > 0 else 0.0

    embed = disnake.Embed(
        title=f"📊 Dota 2 Profile — {player_name} [{loc_country}]",
        description=f"**Friend ID:** `{account_id}`\n**Current Rank:** `{rank_str}`",
        color=disnake.Color.blue()
    )
    if avatar_url:
        embed.set_thumbnail(url=avatar_url)

    embed.add_field(
        name="📈 Winrate & Matches",
        value=(
            f"• **Total:** `{total_matches}` matches\n"
            f"• **Wins:** `{wins}` | **Losses:** `{losses}`\n"
            f"• **Winrate:** `{winrate:.1f}%`"
        ),
        inline=True
    )

    if recent_matches and isinstance(recent_matches, list):
        match_lines = []
        for m in recent_matches[:5]:
            is_radiant = m.get("player_slot", 0) < 128
            radiant_win = m.get("radiant_win", False)
            won = (is_radiant and radiant_win) or (not is_radiant and not radiant_win)
            outcome_icon = "🟢 **WIN**" if won else "🔴 **LOSS**"
            duration_min = m.get("duration", 0) // 60
            match_lines.append(
                f"{outcome_icon} • `{m.get('kills', 0)}/{m.get('deaths', 0)}/{m.get('assists', 0)}` • ⏱️ `{duration_min}m`"
            )
        embed.add_field(name="🕒 Recent Matches (Last 5)", value="\n".join(match_lines), inline=False)
    else:
        embed.add_field(name="🕒 Recent Matches", value="*No recent public matches found.*", inline=False)

    embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

    if ctx.guild:
        await update_member_dota_role(ctx.author, rank_tier)

    view = ProfileLinksView(account_id)
    await msg.edit(content=None, embed=embed, view=view)