import disnake
from disnake.ext import commands
from utils.config import ADM_SUBCOMMANDS
from utils.storage import add_user_exp, update_user_exp_and_lvl, recalculate_all_levels
from utils.comands.exp.helpers import check_level_up

class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["a"])
    @commands.has_permissions(administrator=True)
    async def adm(self, ctx: commands.Context, action: str = None, *args):
        if action is None:
            await ctx.send("❌ Use `!adm help` to see available commands.")
            return

        action_clean = action.lower()

        # 1. Очищення повідомлень: !adm clear 25
        if action_clean in ("clear", "c"):
            amount = 10
            if args and args[0].isdigit():
                amount = int(args[0])

            if amount <= 0:
                await ctx.send("The number of messages must be greater than 0")
                return
            if amount > 150:
                await ctx.send("You can delete a maximum of 150 messages at a time")
                return

            deleted = await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f"Cleared **{len(deleted) - 1}** messages", delete_after=3)
            return

        # 2. Перезавантаження
        if action_clean in ("restart", "r"):
            print("Bot start restart command")
            if ctx.voice_client and ctx.voice_client.is_connected():
                await ctx.voice_client.disconnect(force=True)
            self.bot.is_restarting = True
            await self.bot.close()
            return

        # 3. Вимикання бота (без скорочення "e", щоб не закривати при помилці в exp)
        if action_clean in ("close", "end", "stop"):
            print("Bot close!")
            if ctx.voice_client and ctx.voice_client.is_connected():
                await ctx.voice_client.disconnect(force=True)
            self.bot.is_restarting = False
            await self.bot.close()
            return

        # 4. Перерахунок усіх рівнів у базі: !adm exp_update (або !a e_u)
        if action_clean in ("exp_update", "e_u", "recalc"):
            count = recalculate_all_levels()
            await ctx.send(f"✅ Recalculated levels and fixed XP formatting for **{count}** users.")
            return

        # 5. Видача/зняття досвіду: !adm exp 500 @User або !adm exp -200
        if action_clean in ("exp", "give_exp"):
            if not args:
                await ctx.send("❌ Usage: `!adm exp <amount> [@user/name]` or `!adm exp [@user/name] <amount>`")
                return

            target = None
            amount = None

            if ctx.message.mentions:
                target = ctx.message.mentions[0]

            for arg in args:
                clean_arg = arg.lstrip("-")
                if clean_arg.isdigit() and amount is None:
                    amount = int(arg)
                elif target is None:
                    member = ctx.guild.get_member_named(arg)
                    if not member and arg.isdigit():
                        member = ctx.guild.get_member(int(arg))
                    if member:
                        target = member

            target = target or ctx.author
            amount = amount if amount is not None else 10

            user_id = target.id
            user_data = add_user_exp(user_id, amount, username=target.display_name)
            current_xp = user_data.get("xp", 0)
            current_lvl = user_data.get("lvl", 1)

            remaining_xp, new_lvl, did_level_change = check_level_up(current_xp, current_lvl)
            update_user_exp_and_lvl(user_id, remaining_xp, new_lvl, username=target.display_name)

            if did_level_change:
                await ctx.send(f"🎉 {target.mention} level changed to **{new_lvl}**!")

            action_type = "Added" if amount >= 0 else "Removed"
            await ctx.send(f"✅ {action_type} **{abs(amount)} XP** for {target.mention}. Now: Lvl **{new_lvl}** (`{remaining_xp} XP`).")
            return

        # 6. Меню довідки
        if action_clean in ("help", "h"):
            embed = disnake.Embed(
                title="⚙️ Administrator Control Panel",
                description="List of available administrator management subcommands:",
                color=disnake.Color.dark_red()
            )

            for cmd_format, desc in ADM_SUBCOMMANDS.items():
                embed.add_field(
                    name=f"• `!adm {cmd_format}`",
                    value=f"> {desc}",
                    inline=False
                )

            embed.add_field(
                name="💡 Quick Syntax Tips",
                value=(
                    "• Aliases: `!adm` or `!a`\n"
                    "• XP management supports both directions: `!a exp 500 @user` or `!a exp -200`\n"
                    "• Database repair: run `!a exp_update` to recalculate all levels"
                ),
                inline=False
            )
            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url
            )
            await ctx.send(embed=embed)
            return

    @adm.error
    async def adm_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have administrator permissions!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid arguments! Check `!adm help`.")
        else:
            print(f"Error in adm: {error}")

def setup(bot: commands.Bot):
    bot.add_cog(AdminCog(bot))