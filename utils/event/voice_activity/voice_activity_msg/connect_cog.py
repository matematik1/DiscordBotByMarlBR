import disnake
from disnake.ext import commands

from .helpers import send_voice_log


class VoiceConnectCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: disnake.Member,
        before: disnake.VoiceState,
        after: disnake.VoiceState,
    ):
        # Ігноруємо ботів
        if member.bot:
            return

        # Користувач підключився до каналу
        if before.channel is None and after.channel is not None:
            await send_voice_log(
                bot=self.bot,
                member=member,
                action="Joined voice channel",
                event_type="connect",
                channel_name=after.channel.name,
            )


def setup(bot: commands.Bot):
    bot.add_cog(VoiceConnectCog(bot))