import disnake
from disnake.ext import commands

from .subcom.user_sound_cmd import handle_sound_menu, handle_play_named
from .subcom.stop_cmd import handle_stop_sound


class SoundCog(commands.Cog):
    """Prefix sound commands: !sound / !s."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="sound", aliases=["s"])
    async def sound(self, ctx: commands.Context, action: str = None, *args):
        if not action:
            await handle_sound_menu(ctx, self.bot)
            return

        action_l = action.casefold()

        if action_l in ("help", "h"):
            embed = disnake.Embed(
                title="🔊 Soundboard Help",
                description=(
                    "`!sound` — open mixer\n"
                    "`!sound <name>` — play directly\n"
                    "`!sound play <name>` — play directly\n"
                    "`!sound stop` — stop playback\n"
                    "`!sound help` — show this help"
                ),
                color=disnake.Color.teal(),
            )
            await ctx.send(embed=embed)
            return

        if action_l in ("stop", "leave", "dc"):
            await handle_stop_sound(ctx)
            return

        if action_l in ("play", "p"):
            if not args:
                await ctx.send("❌ Usage: `!sound play <name>`")
                return
            await handle_play_named(ctx, self.bot, " ".join(args))
            return

        await handle_play_named(
            ctx,
            self.bot,
            " ".join((action, *args)),
        )


def setup(bot: commands.Bot):
    bot.add_cog(SoundCog(bot))
