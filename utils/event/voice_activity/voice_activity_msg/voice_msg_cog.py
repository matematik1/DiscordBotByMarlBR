from disnake.ext import commands

from .connect_cog import VoiceConnectCog
from .disconnect_cog import VoiceDisconnectCog
from .transfer_cog import VoiceTransferCog


class VoiceMessagesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


def setup(bot: commands.Bot):
    bot.add_cog(VoiceConnectCog(bot))
    bot.add_cog(VoiceDisconnectCog(bot))
    bot.add_cog(VoiceTransferCog(bot))
    bot.add_cog(VoiceMessagesCog(bot))