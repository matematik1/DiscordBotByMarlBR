import disnake
from disnake.ext import commands, tasks
import time
from utils.commands.exp.helpers import check_level_up 
from utils.storage import add_user_exp, update_user_exp_and_lvl
import random

class VoiceActivity(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cooldowns = {}
        self.cd_seconds = 300

        self.voice_check_loop.start()

    def cog_unload(self):
        self.voice_check_loop.cancel()

    @tasks.loop(seconds=60)
    async def voice_check_loop(self):
        current_time = time.time()

        for guild in self.bot.guilds:
            for voice_chanel in guild.voice_channels:
                for member in voice_chanel.members:
                    if member.bot:
                        continue

                    user_id = member.id
                    last_check = self.cooldowns.get(user_id, 0)

                    if current_time - last_check >= self.cd_seconds:

                        earned_xp = random.randint(1, 15)
                        user_data = add_user_exp(user_id, earned_xp, username=member.display_name)

                        current_xp = user_data.get("xp", 0)
                        current_lvl = user_data.get("lvl", 1)

                        remaining_xp, new_lvl, did_level_up = check_level_up(current_xp, current_lvl)

                        if did_level_up:
                            update_user_exp_and_lvl(user_id, remaining_xp, new_lvl, username=member.display_name)
                        
                        self.cooldowns[user_id] = current_time

    @voice_check_loop.before_loop
    async def before_voice_check_loop(self):
        await self.bot.wait_until_ready()

def setup(bot: commands.Bot):
    bot.add_cog(VoiceActivity(bot))