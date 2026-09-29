import disnake
from disnake.ext import commands

from .subcom.user_sound_cmd import handle_sound_menu, handle_play_named
from .subcom.stop_cmd import handle_sound_stop
from .subcom.admin_mixer_cmd import handle_admin_mixer
from .mixer import find_sound_matches


class SoundSlashCog(commands.Cog):
    """Slash sound commands: /sound ..."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        name="sound",
        description="Soundboard and voice audio controls",
    )
    async def sound(self, inter: disnake.ApplicationCommandInteraction):
        # Do not respond here. Child commands own the interaction response.
        return

    @sound.sub_command(name="help", description="Show soundboard command help")
    async def help(self, inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title="🔊 Soundboard Help",
            description=(
                "`/sound play <name>` — play directly\n"
                "`/sound menu` — open mixer\n"
                "`/sound stop` — stop playback\n"
                "`/sound help` — show this help"
            ),
            color=disnake.Color.teal(),
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

    @sound.sub_command(name="menu", description="Open the interactive sound mixer")
    async def menu(self, inter: disnake.ApplicationCommandInteraction):
        await handle_sound_menu(inter, self.bot)

    @sound.sub_command(name="stop", description="Stop playback and leave voice")
    async def stop(self, inter: disnake.ApplicationCommandInteraction):
        await handle_sound_stop(inter)

    @sound.sub_command(
        name="play",
        description="Play a sound directly without opening the mixer",
    )
    async def play(
        self,
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(
            description="Sound name, path or keyword",
            autocomplete=True,
        ),
    ):
        await handle_play_named(inter, self.bot, name)

    @play.autocomplete("name")
    async def sound_autocomplete(
        self,
        inter: disnake.ApplicationCommandInteraction,
        current: str,
    ):
        matches = find_sound_matches(current, limit=25)

        return [
            disnake.OptionChoice(
                name=(
                    f"{file_name.rsplit('/', 1)[-1].rsplit('.', 1)[0]}"
                    if "/" not in file_name
                    else (
                        f"{file_name.rsplit('/', 2)[-2]} / "
                        f"{file_name.rsplit('/', 1)[-1].rsplit('.', 1)[0]}"
                    )
                )[:100],
                value=file_name[:100],
            )
            for file_name in matches
        ]


def setup(bot: commands.Bot):
    bot.add_cog(SoundSlashCog(bot))
