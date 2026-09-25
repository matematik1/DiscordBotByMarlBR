import disnake
from disnake.ext import commands

from .adm.adm_cog import AdmCog
from .dota.dota_cog import DotaCog
from .duel.duel_cog import DuelCog
from .exp.exp_cog import ExpCog
from .play.play_cog import PlayCog
from .sound.sound_cog import SoundCog

def setup(bot: commands.Bot):
    bot.add_cog(AdmCog(bot))
    bot.add_cog(DotaCog(bot))
    bot.add_cog(DuelCog(bot))
    bot.add_cog(ExpCog(bot))
    bot.add_cog(PlayCog(bot))
    bot.add_cog(SoundCog(bot))