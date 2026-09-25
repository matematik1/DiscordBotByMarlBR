import disnake
from disnake.ext import commands

from utils.comands.adm.subcom.bot_cmd import handle_restart, handle_close
from utils.comands.adm.subcom.exp_cmd import handle_give_exp, handle_set_lvl
from utils.comands.adm.subcom.sync_cmd import handle_sync_roles
from utils.comands.sound.subcom.admin_mixer_cmd import handle_admin_mixer
from utils.storage import get_all_users_data
from utils.config import EXP_ROLE

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
                    "• `!adm exp_update` — Sync level-based roles for all members\n"
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
        if act == "restart":
            await handle_restart(ctx, self.bot)
            return

        # 4. Вимкнення бота: !adm close (без небезпечного аліасу "e")
        if act in ("close", "shutdown", "stop_bot"):
            await handle_close(ctx, self.bot)
            return

        # 5. Синхронізація ролей рівнів досвіду: !adm exp_update
        if act in ("exp_update", "update_exp", "eu"):
            users_data = get_all_users_data()
            updated_count = 0
            for member in ctx.guild.members:
                if member.bot:
                    continue
                user_id_str = str(member.id)
                if user_id_str in users_data:
                    lvl = users_data[user_id_str].get("lvl", 1)
                    target_role_id = None
                    for req_lvl in sorted(EXP_ROLE.keys(), reverse=True):
                        if lvl >= int(req_lvl):
                            target_role_id = EXP_ROLE[req_lvl]
                            break
                    if target_role_id:
                        role = ctx.guild.get_role(int(target_role_id))
                        if role and role not in member.roles:
                            try:
                                await member.add_roles(role, reason="Admin EXP roles sync")
                                updated_count += 1
                            except disnake.Forbidden:
                                pass
            await ctx.send(f"✅ Synced experience roles for **{updated_count}** members.")
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