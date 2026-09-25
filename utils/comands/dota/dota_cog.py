import random
import disnake
import aiohttp
import asyncio
import os
from disnake.ext import commands
from utils.config import DOTA_GUILD_INFO, DOTA_POSITIONS, DOTA_SUBCOMMANDS, HEROES_GIF_DIR
from utils.storage import get_user_steam_id
from utils.comands.dota.helpers import (
    get_available_heroes, 
    generate_inventory_image, 
    VerifySteamView,
    format_rank_tier,
    ProfileLinksView
)

class DotaLinksView(disnake.ui.View):
    def __init__(self, d2pt_slug: str = None, dotabuff_slug: str = None):
        super().__init__(timeout=None)
        if d2pt_slug and dotabuff_slug:
            self.d2pt_url = f"https://dota2protracker.com/hero/{d2pt_slug}"
            self.dotabuff_url = f"https://www.dotabuff.com/heroes/{dotabuff_slug}"
        else:
            self.d2pt_url = "https://dota2protracker.com/meta"
            self.dotabuff_url = "https://www.dotabuff.com/heroes/meta"

    @disnake.ui.button(label="Dota2ProTracker", style=disnake.ButtonStyle.primary, emoji="📊")
    async def protracker_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message(f"📊 **Dota2ProTracker:** {self.d2pt_url}", ephemeral=True)

    @disnake.ui.button(label="Dotabuff", style=disnake.ButtonStyle.danger, emoji="📈")
    async def dotabuff_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message(f"📈 **Dotabuff:** {self.dotabuff_url}", ephemeral=True)

class DotaCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["d"])
    async def dota(self, ctx: commands.Context, dota_contex: str = None, steam_id: str = None):
        if dota_contex is None:
            await ctx.send("WRITE `!dota help`")
            return

        sub = dota_contex.lower()

        if dota_contex and dota_contex.lower() in ("help", "h"):
            embed = disnake.Embed(
                title="🎮 Dota 2 Command Center",
                description="List of available subcommands for Dota 2 profiles, builds, and tools:",
                color=disnake.Color.red()
            )
            embed.add_field(
                name="• `!d connect <SteamID32>`",
                value="> Link your Steam account via profile Real Name verification",
                inline=False
            )
            embed.add_field(
                name="• `!d profile [SteamID32]`",
                value="> View rank medal, win rate, total matches, and recent games summary",
                inline=False
            )
            embed.add_field(
                name="• `!d inv [SteamID32]`",
                value="> Render your active custom 6-slot inventory image",
                inline=False
            )
            embed.add_field(
                name="• `!d roll [min-max]`",
                value="> Roll the dice with animation (aliases: `!d r`, default: `1-100`, custom: `!d r 100-200`)",
                inline=False
            )
            embed.add_field(
                name="💡 Aliases & Syntax",
                value="• You can use `!d` instead of `!dota`\n• Example: `!d profile` or `!d roll 50`",
                inline=False
            )
            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url
            )
            await ctx.send(embed=embed)
            return

        if sub in ("guild", "g"):
            embed = disnake.Embed(
                title=f"⚔️ Dota 2 Guild — {DOTA_GUILD_INFO['name']}",
                description="Join our guild to complete contracts and play party ranked/unranked!",
                color=disnake.Color.red()
            )
            embed.add_field(name="🏷️ Tag", value=f"`[{DOTA_GUILD_INFO['tag']}]`", inline=True)
            embed.add_field(name="🆔 Leader Friend ID", value=f"`{DOTA_GUILD_INFO['leader_dota_id']}`", inline=True)
            embed.add_field(
                name="👑 Guild Leadership",
                value=(
                    f"• **Leader:** [{DOTA_GUILD_INFO['leader_name']}]({DOTA_GUILD_INFO['leader_steam']})\n"
                    f"• **Officer:** [{DOTA_GUILD_INFO['officer_name']}]({DOTA_GUILD_INFO['officer_steam']})"
                ),
                inline=False
            )
            embed.add_field(
                name="📌 How to join via Leader:",
                value=(
                    f"1. Copy Leader's Friend ID: `{DOTA_GUILD_INFO['leader_dota_id']}`\n"
                    "2. Open Dota 2 -> Friends -> **Add Friend** (or search in Guilds by name).\n"
                    "3. Open the profile -> **View Guild** -> **Apply to Guild**."
                ),
                inline=False
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
            return

        if sub in ("random", "r"):
            available_heroes = get_available_heroes()
            if not available_heroes:
                await ctx.send(f"Error: No hero GIF files found in `{HEROES_GIF_DIR}`.")
                return

            hero_data = random.choice(available_heroes)
            position = random.choice(DOTA_POSITIONS)
            boot_id = random.randint(1, 5)
            chosen_items = random.sample(list(range(1, 64)), 5)

            try:
                inv_buffer = generate_inventory_image(boot_id, chosen_items)
            except Exception as e:
                await ctx.send(f"Error generating item layout: {e}")
                return

            hero_file = disnake.File(hero_data["file_path"], filename="hero.gif")
            inventory_file = disnake.File(fp=inv_buffer, filename="inventory.png")

            embed = disnake.Embed(
                title=f"🎲 Hero Roulette: {hero_data['name']}",
                description=f"📍 **Position:** `{position}`\n🎒 **RANDOM Item Build:**",
                color=disnake.Color.gold(),
            )
            embed.set_thumbnail(url="attachment://hero.gif")
            embed.set_image(url="attachment://inventory.png")
            embed.set_footer(text=f"Rolled by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed, files=[hero_file, inventory_file])
            return

        if sub in ("hero", "signa"):
            available_heroes = get_available_heroes()
            if not available_heroes:
                await ctx.send(f"Error: No hero GIF files found in `{HEROES_GIF_DIR}`.")
                return

            hero = random.choice(available_heroes)
            gif_file = disnake.File(hero["file_path"], filename=hero["file_name"])

            embed = disnake.Embed(
                title=f"🎭 Random Hero: {hero['name']}",
                description=f"You rolled **{hero['name']}**!\nCheck out current pro builds and meta stats using the buttons below:",
                color=disnake.Color.dark_red()
            )
            embed.set_image(url=f"attachment://{hero['file_name']}")
            embed.set_footer(text=f"Rolled by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

            view = DotaLinksView(d2pt_slug=hero["d2pt_slug"], dotabuff_slug=hero["dotabuff_slug"])
            await ctx.send(embed=embed, file=gif_file, view=view)
            return

        if sub in ("meta", "m", "мета", "м"):
            embed = disnake.Embed(
                title="🏆 Dota 2 Current Meta & Tier Lists",
                description=(
                    "Track the strongest heroes, win rates, and trending high-MMR builds across patches:\n\n"
                    "• **Dota2ProTracker Meta:** Analyzes 7k–12k+ MMR matches, pro pub builds, item timings, and hero facets.\n"
                    "• **Dotabuff Meta:** Win rate and pick rate tiers categorized by skill brackets (Herald to Immortal)."
                ),
                color=disnake.Color.purple()
            )
            embed.add_field(
                name="📌 Quick ProTracker Roles:",
                value=(
                    "[Carry (Pos 1)](https://dota2protracker.com/meta?mmr=7000&position=pos%2B1&period=patch&meta_period=patch) • "
                    "[Mid (Pos 2)](https://dota2protracker.com/meta?mmr=7000&position=pos%2B2&period=patch&meta_period=patch) • "
                    "[Offlane (Pos 3)](https://dota2protracker.com/meta?mmr=1000&position=pos%2B3&period=patch&meta_period=patch) • "
                    "[Support (Pos 4/5)](https://dota2protracker.com/meta?mmr=1000&position=pos%2B5M&period=patch&meta_period=patch)"
                ),
                inline=False
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

            view = DotaLinksView()
            await ctx.send(embed=embed, view=view)
            return
        if sub in ("connect", "c"):
            parts = ctx.message.content.split()
            if len(parts) < 3 or not parts[2].isdigit():
                await ctx.send("❌ Usage: `!dota connect <Dota Friend ID>`\nExample: `!dota connect 1257746704`")
                return

            account_id = int(parts[2])
            verify_code = f"MarBR-{random.randint(1000, 9999)}"

            embed = disnake.Embed(
                title="🔗 Steam Account Linking",
                description=(
                    f"To verify ownership of Dota account **`{account_id}`**:\n\n"
                    f"1. Go to **Edit Profile** in Steam.\n"
                    f"2. Paste this code into the **Real Name** field:\n"
                    f"👉 **`{verify_code}`**\n\n"
                    f"3. Click **Save** at the bottom of the page in Steam.\n"
                    f"4. Click the **Verify Account** button below."
                ),
                color=disnake.Color.blue()
            )
            embed.set_footer(text="You have 3 minutes to complete verification.")

            view = VerifySteamView(
                author_id=ctx.author.id,
                account_id=account_id,
                verify_code=verify_code
            )
            await ctx.send(embed=embed, view=view)
            return

        if sub in ("roll", "r"):
            first = 1
            last = 100
            query = str(steam_id)

            if query:
                clean_query = query.strip().replace(" ", "")
                if "-" in clean_query:
                    parts = clean_query.split("-")
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        p1, p2 = int(parts[0]), int(parts[1])
                        first = min(p1, p2)
                        last = max(p1, p2)
                elif query.isdigit():
                    last = int(query)

            if first == last:
                last = first + 1

            anim_embed = disnake.Embed(
                title="🎲 Rolling the dice...",
                description="> *Shaking the cup...* ⏳",
                color=disnake.Color.dark_gray()
            )
            anim_embed.set_author(
                name=f"{ctx.author.display_name} is rolling...",
                icon_url=ctx.author.display_avatar.url
            )

            msg = await ctx.send(embed=anim_embed)

            dice_frames = ["🎲", "♥️", "🧩", "🎴", "🎰", "🎱", "🪩"]
            for _ in range(3):
                fake_num = random.randint(first, last)
                frame = random.choice(dice_frames)
                anim_embed.description = f"> *Rolling...* {frame} **[{fake_num}]**"
                await msg.edit(embed=anim_embed)
                await asyncio.sleep(0.45)

            number = random.randint(first, last)
            gif_filename = "luck_cat.gif"
            gif_path = os.path.join("video", gif_filename)

            final_embed = disnake.Embed(
                title="🎲 Roll Results 🎲",
                description=(
                    "> *A roll for those without chat in Dota 2!*\n\n"
                    f"**Range:** `{first} – {last}`\n"
                    f"**Rolled:** 🎯 **{number}**"
                ),
                color=disnake.Color.gold()
            )
            final_embed.set_author(
                name=f"{ctx.author.display_name} rolled the dice",
                icon_url=ctx.author.display_avatar.url
            )
            final_embed.set_footer(text="May the roll gods be on your side")

            await msg.delete()

            if os.path.exists(gif_path):
                file = disnake.File(gif_path, filename=gif_filename)
                final_embed.set_thumbnail(url=f"attachment://{gif_filename}")
                await ctx.send(file=file, embed=final_embed)
            else:
                await ctx.send(embed=final_embed)
            return


        if sub in ("profile", "me", "stats", "p"):
            account_id = None

            parts = ctx.message.content.split()
            if len(parts) >= 3 and parts[2].isdigit():
                account_id = int(parts[2])
            else:
                account_id = get_user_steam_id(ctx.author.id)

            if not account_id:
                await ctx.send(
                    "❌ **No linked account found!**\n"
                    "Use `!dota connect <Friend ID>` first, or provide an ID: `!dota profile <Friend ID>`"
                )
                return

            loading_msg = await ctx.send("🔄 *Fetching stats from OpenDota...*")

            # Параллельно стягиваем профиль, win/loss и последние матчи
            base_url = f"https://api.opendota.com/api/players/{account_id}"
            headers = {"User-Agent": "Mozilla/5.0"}

            async with aiohttp.ClientSession(headers=headers) as session:
                try:
                    async with session.get(base_url, timeout=10) as r1, \
                               session.get(f"{base_url}/wl", timeout=10) as r2, \
                               session.get(f"{base_url}/recentMatches", timeout=10) as r3:
                        
                        if r1.status != 200:
                            await loading_msg.edit(content="❌ Failed to fetch player profile. Check if profile is public.")
                            return

                        player_data = await r1.json()
                        wl_data = await r2.json() if r2.status == 200 else {"win": 0, "lose": 0}
                        recent_matches = await r3.json() if r3.status == 200 else []
                except Exception as e:
                    print(f"Error fetching Dota profile: {e}")
                    await loading_msg.edit(content="❌ Error connecting to OpenDota API.")
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

            # Статистика побед/поражений
            embed.add_field(
                name="📈 Winrate & Matches",
                value=(
                    f"• **Total:** `{total_matches}` matches\n"
                    f"• **Wins:** `{wins}` | **Losses:** `{losses}`\n"
                    f"• **Winrate:** `{winrate:.1f}%`"
                ),
                inline=True
            )

            # Формирование блока последних 5 матчей
            if recent_matches and isinstance(recent_matches, list):
                match_lines = []
                for m in recent_matches[:5]:
                    is_radiant = m.get("player_slot", 0) < 128
                    radiant_win = m.get("radiant_win", False)
                    won = (is_radiant and radiant_win) or (not is_radiant and not radiant_win)
                    
                    outcome_icon = "🟢 **WIN**" if won else "🔴 **LOSS**"
                    kills = m.get("kills", 0)
                    deaths = m.get("deaths", 0)
                    assists = m.get("assists", 0)
                    duration_min = m.get("duration", 0) // 60
                    
                    match_lines.append(
                        f"{outcome_icon} • `{kills}/{deaths}/{assists}` • ⏱️ `{duration_min}m`"
                    )

                embed.add_field(
                    name="🕒 Recent Matches (Last 5)",
                    value="\n".join(match_lines),
                    inline=False
                )
            else:
                embed.add_field(
                    name="🕒 Recent Matches",
                    value="*No recent public matches found.*",
                    inline=False
                )

            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}", 
                icon_url=ctx.author.display_avatar.url
            )

            view = ProfileLinksView(account_id)
            await loading_msg.delete()
            await ctx.send(embed=embed, view=view)
            return

def setup(bot: commands.Bot):
    bot.add_cog(DotaCog(bot))