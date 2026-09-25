import disnake
from disnake.ext import commands

from .voice_activity.voice_activity_cog import VoiceActivity
from .censored_words.cen_word_cog import CensoredWords

def setup(bot: commands.Bot):
    bot.add_cog(VoiceActivity(bot))
    bot.add_cog(CensoredWords(bot))