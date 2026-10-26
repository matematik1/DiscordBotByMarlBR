from utils.config import VERIFICATION_ROLE_ID, DOTA_RANK_ID
import disnake
from disnake.ext import commands, tasks

UNRANKED_ROLE_ID = 1553011169218793562

class CheckRank(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.rank_check_loop.start()

    def cog_unload(self):
        self.rank_check_loop.cancel()

    @tasks.loop(minutes=15)
    async def rank_check_loop(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.bot:
                    continue

                current_roles = {role.id for role in member.roles}

                # Перевіряємо тільки верифікованих користувачів
                if VERIFICATION_ROLE_ID not in current_roles:
                    continue

                # Перевіряємо, чи є в користувача будь-який ранг
                has_rank = any(
                    rank_id in current_roles
                    for rank_id in DOTA_RANK_ID.values()
                )

                unranked_role = guild.get_role(UNRANKED_ROLE_ID)
                if unranked_role is None:
                    continue

                has_unranked = UNRANKED_ROLE_ID in current_roles

                # Немає рангу та UNRANKED — додаємо UNRANKED
                if not has_rank and not has_unranked:
                    await member.add_roles(
                        unranked_role,
                        reason="Verified member has no Dota rank"
                    )

                # Є ранг і UNRANKED — видаляємо UNRANKED
                elif has_rank and has_unranked:
                    await member.remove_roles(
                        unranked_role,
                        reason="Member has a Dota rank"
                    )

    @rank_check_loop.before_loop
    async def before_rank_check_loop(self):
        await self.bot.wait_until_ready()

def setup(bot: commands.Bot):
    bot.add_cog(CheckRank(bot))