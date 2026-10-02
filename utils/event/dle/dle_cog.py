import random
from .helpers import HeroInfo

import disnake
from disnake.ext import commands, tasks
from utils.event.dle.storage import save_current_hero, get_daly_date, current_date

class DLEEventCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.dle_loop.start()

    def cog_unload(self):
        self.dle_loop.cancel()

    def generate_daily_hero(self):
        random_hero = random.choice(HeroInfo)
        save_current_hero(random_hero["heroId"], random_hero["championName"])
        return random_hero

    @tasks.loop(minutes=15)
    async def dle_loop(self):
        if get_daly_date() != current_date():
            self.generate_daily_hero()