import disnake
from disnake.ext import commands

from utils.commands.adm.subcom.bot_cmd import handle_restart, handle_close
from utils.commands.adm.subcom.exp_cmd import handle_give_exp, handle_set_lvl
from utils.commands.adm.subcom.sync_cmd import handle_sync_roles
from utils.commands.sound.subcom.admin_mixer_cmd import handle_admin_mixer
# Змінили імпорт: прибрали EXP_ROLE і додали recalculate_all_levels
from utils.storage import recalculate_all_levels

class AdmCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="adm", aliases=["a"])
    @commands.has_permissions(administrator=True)
    async def adm(self, ctx: commands.Context, action: str = None, *args):
        # 1. Довідка панелі адміністратора
        if not action or action.lower() in ("help", "h"):
            embed = disnake.Embed(
                title="🛡️ Admin Control Panel",
                description=(
                    "Available administrative commands:\n\n"
                    "• `!adm sound` (or `!a s`) — Open interactive sound mixer\n"
                    "• `!adm give_exp <@user> <amount>` — Grant experience points\n"
                    "• `!adm set_lvl <@user> <level>` — Set user level\n"
                    "• `!adm exp_update` — Recalculate experience and levels for all users\n"
                    "• `!adm sync_roles` — Sync Dota 2 rank roles for all members\n"
                    "• `!adm restart` — Restart the bot application\n"
                    "• `!adm close` — Safely terminate bot execution"
                ),
                color=disnake.Color.dark_theme()
            )
            embed.set_footer(text=f"Invoked by {ctx.author.display_name}")
            await ctx.send(embed=embed)
            return

        act = action.lower()

        # 2. Адмінський саунд-мікшер: !adm sound
        if act in ("sound", "s", "mixer"):
            await handle_admin_mixer(ctx, self.bot)
            return

        # 3. Перезавантаження бота: !adm restart
        if act in ("restart", "res"):
            await handle_restart(ctx, self.bot)
            return

        # 4. Вимкнення бота: !adm close (без небезпечного аліасу "e")
        if act in ("close", "shutdown", "stop_bot"):
            await handle_close(ctx, self.bot)
            return

        # 5. Перерахунок рівнів досвіду: !adm exp_update
        if act in ("exp_update", "update_exp", "eu"):
            # Замість видачі ролей тепер просто перераховуємо рівні в базі даних
            updated_count = recalculate_all_levels()
            await ctx.send(f"✅ Successfully recalculated experience and levels for **{updated_count}** database entries.")
            return

        # 6. Синхронізація ролей Dota: !adm sync_roles
        if act in ("sync_roles", "sync", "roles"):
            await handle_sync_roles(ctx)
            return

        # 7. Нарахування досвіду: !adm give_exp @user 500
        if act in ("give_exp", "giveexp", "exp"):
            if not ctx.message.mentions or len(args) < 1:
                await ctx.send("❌ Usage: `!adm give_exp <@user> <amount>`")
                return
            target = ctx.message.mentions[0]
            try:
                amount_str = [arg for arg in args if not arg.startswith("<@")][0]
                amount = int(amount_str)
            except (IndexError, ValueError):
                await ctx.send("❌ Please provide a valid integer amount of XP!")
                return

            await handle_give_exp(ctx, target, amount)
            return

        # 8. Встановлення рівня: !adm set_lvl @user 10
        if act in ("set_lvl", "setlvl", "level"):
            if not ctx.message.mentions or len(args) < 1:
                await ctx.send("❌ Usage: `!adm set_lvl <@user> <level>`")
                return
            target = ctx.message.mentions[0]
            try:
                lvl_str = [arg for arg in args if not arg.startswith("<@")][0]
                lvl = int(lvl_str)
            except (IndexError, ValueError):
                await ctx.send("❌ Please provide a valid integer level!")
                return

            await handle_set_lvl(ctx, target, lvl)
            return

        await ctx.send(f"⚠️ Unknown action `{action}`. Use `!adm help` to see all commands.")

    @adm.error
    async def adm_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You do not have administrator permissions to run this command!")

def setup(bot: commands.Bot):
    bot.add_cog(AdmCog(bot))