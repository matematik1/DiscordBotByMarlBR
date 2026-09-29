from utils.slash_commands.sound.mixer import get_sound_files, open_admin_mixer


async def handle_admin_mixer(inter, bot):
    if not get_sound_files():
        await inter.response.send_message(
            "⚠️ No audio files found in the sound directory.",
            ephemeral=True,
        )
        return

    await open_admin_mixer(inter, bot, ephemeral=True)
