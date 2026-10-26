import disnake
from disnake.ext import commands

from .helpers import send_voice_log


class VoiceDisconnectCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: disnake.Member,
        before: disnake.VoiceState,
        after: disnake.VoiceState,
    ):
        if member.bot:
            return

        # Користувач відключився від каналу
        if before.channel is not None and after.channel is None:
            await send_voice_log(
                bot=self.bot,
                member=member,
                action="Left voice channel",
                event_type="disconnect",
                channel_name=before.channel.name,
            )


def setup(bot: commands.Bot):
    bot.add_cog(VoiceDisconnectCog(bot))