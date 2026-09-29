import random
import time
import disnake
from disnake.ext import commands
import os

from utils.event.exp_sustem.helpers import get_exp_for_lvl, check_level_up
from utils.storage import add_user_exp, get_user_exp, set_user_level, get_top_users

class ExpSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cooldowns = {}
        self.cd_seconds = 20

    def random_exp(self, a: int = 0, b: int = 0):
        return random.randint(a, b)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot or not message.guild:
            return

        if message.content.startswith("!"):
            return
        if message.content.startswith("/"):
            return
        if message.content.startswith("."):
            return
        if message.content.startswith("https:"):
            return

        user_id = message.author.id
        now = time.time()

        last_time = self.cooldowns.get(user_id, 0)
        if now - last_time < self.cd_seconds:
            return

        self.cooldowns[user_id] = now
        length_message = int(len(message.content.replace(" ", "")))

        match length_message:
            case n if n <= 3:
                earned_xp = self.random_exp(1, 3)
            case n if n <= 5:
                earned_xp = self.random_exp(3, 7)
            case n if n <= 9:
                earned_xp = self.random_exp(7, 11)
            case n if n <= 15:
                earned_xp = self.random_exp(11, 17)
            case _:
                earned_xp = self.random_exp(17, 25)
            
        user_data = add_user_exp(user_id, earned_xp, username=message.author.display_name)

        current_xp = user_data.get("xp", 0)
        current_lvl = user_data.get("lvl", 1)

        remaining_xp, new_lvl, did_level_up = check_level_up(current_xp, current_lvl)

        if did_level_up:
            set_user_level(user_id, new_lvl)
            await message.channel.send(
                f"🎉 WOW IT'S IDIOT UP LVL XD {message.author.mention} HE NOW HAS LVL**{new_lvl}**!"
            )

def setup(bot: commands.Bot):
    bot.add_cog(ExpSystem(bot))