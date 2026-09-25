import disnake
from disnake.ext import commands

from .subcom.user_sound_cmd import handle_sound_menu, handle_play_named
from .subcom.stop_cmd import handle_sound_stop
from .subcom.admin_mixer_cmd import handle_admin_mixer
from .mixer import get_sound_files

class SoundSlashCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="sound", description="Audio soundboard and voice controls")
    async def sound(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @sound.sub_command(name="menu", description="Open interactive soundboard menu")
    async def menu(self, inter: disnake.ApplicationCommandInteraction):
        await handle_sound_menu(inter, self.bot)

    @sound.sub_command(name="stop", description="Stop sound and disconnect from voice")
    async def stop(self, inter: disnake.ApplicationCommandInteraction):
        await handle_sound_stop(inter)

    @sound.sub_command(name="play", description="Play a specific sound clip directly")
    async def play(
        self,
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(description="Name or keyword of the sound")
    ):
        await handle_play_named(inter, self.bot, name)

    # Автодоповнення для підкоманди /sound play
    @play.autocomplete("name")
    async def sound_autocomplete(self, inter: disnake.ApplicationCommandInteraction, current: str):
        files = get_sound_files()
        suggestions = []
        for f in files:
            name_clean = f.rsplit(".", 1)[0]
            if current.lower() in name_clean.lower():
                suggestions.append(name_clean)
        return suggestions[:25]