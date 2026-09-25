import disnake

async def handle_sound_stop(inter: disnake.ApplicationCommandInteraction):
    voice_client: disnake.VoiceClient = inter.guild.voice_client
    if voice_client and voice_client.is_connected():
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()
        await voice_client.disconnect()
        await inter.response.send_message("⏹️ Playback stopped and disconnected from voice.", ephemeral=True)
    else:
        await inter.response.send_message("⚠️ Bot is not in any voice channel.", ephemeral=True)