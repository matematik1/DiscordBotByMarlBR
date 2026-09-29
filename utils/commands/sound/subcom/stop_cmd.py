from disnake.ext import commands

from utils.commands.sound.mixer import invalidate_playback


async def handle_stop_sound(ctx: commands.Context):
    voice_client = ctx.guild.voice_client

    if not voice_client or not voice_client.is_connected():
        await ctx.send("⚠️ Bot is not connected to any voice channel.")
        return

    invalidate_playback(ctx.guild.id)

    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()

    try:
        await voice_client.disconnect()
    except Exception:
        pass

    await ctx.send(
        "⏹️ Playback stopped and disconnected from voice channel."
    )
