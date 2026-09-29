from disnake.ext import commands

from .voice_activity.voice_activity_cog import VoiceActivity
from .censored_words.cen_word_cog import CensoredWords
from .exp_sustem.exp_sustem_cog import ExpSystem
from .money_system.money_system_cog import MoneySystem
from .money_system.subevent.salary_system import SalarySystem


def setup(bot: commands.Bot):
    bot.add_cog(VoiceActivity(bot))
    bot.add_cog(CensoredWords(bot))
    bot.add_cog(ExpSystem(bot))
    bot.add_cog(MoneySystem(bot))
    bot.add_cog(SalarySystem(bot))
