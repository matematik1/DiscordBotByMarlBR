import disnake

from utils.slash_commands.sound.mixer import invalidate_playback


async def handle_sound_stop(inter: disnake.ApplicationCommandInteraction):
    voice_client: disnake.VoiceClient = inter.guild.voice_client

    if not voice_client or not voice_client.is_connected():
        await inter.response.send_message(
            "⚠️ Bot is not connected to any voice channel.",
            ephemeral=True,
        )
        return

    invalidate_playback(inter.guild.id)

    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()

    try:
        await voice_client.disconnect()
    except Exception:
        pass

    await inter.response.send_message(
        "⏹️ Playback stopped and disconnected from voice.",
        ephemeral=True,
    )
