import disnake
from disnake.ext import commands

from .dota.dota_cog import DotaSlashCog
from .adm.adm_cog import AdmSlashCog
from .sound.sound_cog import SoundSlashCog
from .duel.duel_cog import DuelSlashCog
from .exp.exp_cog import ExpSlashCog
from .play.play_cog import PlaySlashCog

def setup(bot: commands.Bot):
    bot.add_cog(DotaSlashCog(bot))
    bot.add_cog(AdmSlashCog(bot))
    bot.add_cog(SoundSlashCog(bot))
    bot.add_cog(DuelSlashCog(bot))
    bot.add_cog(ExpSlashCog(bot))
    bot.add_cog(PlaySlashCog(bot))