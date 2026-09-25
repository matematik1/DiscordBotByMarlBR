import random
import time
import disnake
from disnake.ext import commands
import os

from utils.comands.exp.helpers import get_exp_for_lvl, check_level_up
from utils.storage import add_user_exp, get_user_exp, set_user_level, get_top_users


class ExpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cooldowns = {}
        self.cd_seconds = 60

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot or not message.guild:
            return

        if message.content.startswith("!"):
            return

        user_id = message.author.id
        now = time.time()

        last_time = self.cooldowns.get(user_id, 0)
        if now - last_time < self.cd_seconds:
            return

        self.cooldowns[user_id] = now

        earned_xp = random.randint(15, 25)
        user_data = add_user_exp(user_id, earned_xp, username=message.author.display_name)

        current_xp = user_data.get("xp", 0)
        current_lvl = user_data.get("lvl", 1)

        remaining_xp, new_lvl, did_level_up = check_level_up(current_xp, current_lvl)

        if did_level_up:
            set_user_level(user_id, new_lvl)
            await message.channel.send(
                f"🎉 WOW IT'S IDIOT UP LVL XD {message.author.mention} HE NOW HAS LVL**{new_lvl}**!"
            )

    @commands.command(aliases=["lvl", "levl", "exp"])
    async def rank(self, ctx: commands.Context, member: disnake.Member = None):
        target = member or ctx.author

        if target.bot:
            await ctx.send("❌ Bots don't have levels!")
            return

        data = get_user_exp(target.id)
        current_xp = data.get("xp", 0)
        current_lvl = data.get("lvl", 1)
        needed_xp = get_exp_for_lvl(current_lvl)

        embed = disnake.Embed(
            title=f"📊 Rank Profile — {target.display_name}",
            color=disnake.Color.green()
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="🎖️ Level", value=f"`{current_lvl}`", inline=True)
        embed.add_field(name="✨ Experience (XP)", value=f"`{current_xp} / {needed_xp}`", inline=True)
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["t", "lider"])
    async def top(self, ctx: commands.Context):
        top_list = get_top_users(limit=10)

        if not top_list:
            await ctx.send("❌ Leaderboard is empty right now!")
            return

        embed = disnake.Embed(
            title="🏆 Server Experience Leaderboard",
            color=disnake.Color.gold()
        )

        leaderboard_lines = []
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}

        for rank_num, user_data in enumerate(top_list, start=1):
            user_id = user_data.get("user_id")
            lvl = user_data.get("lvl", 1)
            xp = user_data.get("xp", 0)

            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"User ID: {user_id}"

            icon = medals.get(rank_num, f"`#{rank_num}`")

            leaderboard_lines.append(
                f"{icon} **{name}** — Lvl **{lvl}** `({xp} XP)`"
            )

        embed.description = "\n".join(leaderboard_lines)
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        gif_path = os.path.join("video", "logo.gif")

        if os.path.exists(gif_path):
            file = disnake.File(gif_path, filename="logo.gif")
            embed.set_thumbnail(url="attachment://logo.gif")
            await ctx.send(embed=embed, file=file)
        else:
            await ctx.send(embed=embed)
            
    @commands.command(name="exp_help", aliases=["eh"])
    async def exp_help(self, ctx: commands.Context):
        embed = disnake.Embed(
            title="✨ Experience & Levels System",
            description="Earn XP by chatting and climbing the server leaderboard:",
            color=disnake.Color.gold()
        )
        embed.add_field(
            name="• `!rank [user]`",
            value="> View current level, remaining XP, progress bar, and server standing (aliases: `!lvl`, `!level`)",
            inline=False
        )
        embed.add_field(
            name="• `!top`",
            value="> Display top active server members with the custom logo animation (aliases: `!t`, `!lider`)",
            inline=False
        )
        embed.add_field(
            name="📈 Leveling Mechanics",
            value=(
                "• XP is awarded per message with integer-based progression\n"
                "• Admins can award or deduct experience using `!adm exp`"
            ),
            inline=False
        )
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(ExpCog(bot))