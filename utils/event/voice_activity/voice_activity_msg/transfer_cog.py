import disnake
from disnake.ext import commands

from .helpers import send_voice_log


class VoiceTransferCog(commands.Cog):
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

        # Перевіряємо, чи користувач змінив канал
        if (
            before.channel is not None
            and after.channel is not None
            and before.channel.id != after.channel.id
        ):
            await send_voice_log(
                bot=self.bot,
                member=member,
                action="Switched voice channel",
                event_type="transfer",
                channel_name=after.channel.name,
                previous_channel=before.channel.name,
            )


def setup(bot: commands.Bot):
    bot.add_cog(VoiceTransferCog(bot))