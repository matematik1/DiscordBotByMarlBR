import disnake
from disnake.ext import commands

from .subcom.bot_cmd import handle_restart, handle_close
from .subcom.exp_cmd import handle_give_exp, handle_set_lvl
from .subcom.sync_cmd import handle_sync_roles
from utils.slash_commands.sound.subcom.admin_mixer_cmd import handle_admin_mixer

class AdmSlashCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Базовая слеш-команда: доступна ТОЛЬКО администраторам сервера
    @commands.slash_command(
        name="adm",
        description="Administrative management tools",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def adm(self, inter: disnake.ApplicationCommandInteraction):
        pass

    # 1. /adm give_exp <user> <amount>
    @adm.sub_command(name="give_exp", description="Add experience points to a member")
    async def give_exp(
        self,
        inter: disnake.ApplicationCommandInteraction,
        user: disnake.Member = commands.Param(description="Target server member"),
        amount: int = commands.Param(description="Amount of XP to grant")
    ):
        await handle_give_exp(inter, user, amount)

    # 2. /adm set_lvl <user> <level>
    @adm.sub_command(name="set_lvl", description="Set exact level for a member")
    async def set_lvl(
        self,
        inter: disnake.ApplicationCommandInteraction,
        user: disnake.Member = commands.Param(description="Target server member"),
        level: int = commands.Param(description="New level value")
    ):
        await handle_set_lvl(inter, user, level)

    # 3. /adm sync_roles
    @adm.sub_command(name="sync_roles", description="Bulk sync Dota 2 rank roles for all linked members")
    async def sync_roles(self, inter: disnake.ApplicationCommandInteraction):
        await handle_sync_roles(inter)

    # 4. /adm restart
    @adm.sub_command(name="restart", description="Safely restart the bot process")
    async def restart(self, inter: disnake.ApplicationCommandInteraction):
        await handle_restart(inter, self.bot)

    # 5. /adm close
    @adm.sub_command(name="close", description="Shut down the bot completely")
    async def close(self, inter: disnake.ApplicationCommandInteraction):
        await handle_close(inter, self.bot)

    # 6. /adm sound
    @adm.sub_command(name="sound", description="Open administrative sound mixer (volume, repeat, default save)")
    async def adm_sound(self, inter: disnake.ApplicationCommandInteraction):
        await handle_admin_mixer(inter, self.bot)