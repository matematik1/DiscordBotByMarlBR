import disnake
from disnake.ext import commands

async def handle_stop_sound(ctx: commands.Context):
    voice_client: disnake.VoiceClient = ctx.guild.voice_client
    if voice_client and voice_client.is_connected():
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()
        await voice_client.disconnect()
        await ctx.send("⏹️ Playback stopped and disconnected from voice channel.")
    else:
        await ctx.send("⚠️ Bot is not connected to any voice channel.")